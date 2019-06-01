'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: Action to determine the to identify user to someone in the legaue
'''
from api.actions import Action, ActionState
from api.settings.message_strings import ASK_FOR_EMAIL, EMAIL_NOT_FOUND,\
    LOCKED_OUT, IMPOSTER, WELCOME_LEAGUE
from api.settings.action_keys import WELCOME_KEY
from api.helper import parse_out_email
from api.logging import LOGGER
from api.message import Message
from api.errors import IdentityException


class IdentifyUser(Action):
    """
        Action used to identify a given messenger user to a player in league
    """
    EMAIL_STATE = "Asking for email"
    UNKNOWN_STATE = "Cannot find the user, user should consult convenors"
    IMPOSTER_STATE = "Trying to steal someone's else email"
    LOCKED_OUT_STATE = " Locked out for trying 3 different emails"

    def process(self, message, action_map):
        """
            The main entry point

            Notes:
                First use information given by the messenger to lookup player.
                Second if not found ask them for their email
                    and use the given email to lookup player.
                Lock out user if guess too many emails.
        """
        self.message = message
        self.action_map = action_map
        messenger_id = self.message.get_sender_id()
        player = self.database.get_player(messenger_id)
        if player is None:
            # first time we have ever received a response
            messenger_user = self.messenger.lookup_user_id(messenger_id)
            player_info = self.determine_player(messenger_user)
            player = self.database.create_player(messenger_id,
                                                 messenger_user.get_name())
            self.database.save_player(player)

            # if we know the player info already then can just skip
            # and welcome them to the league
            if (player_info is not None and
                    not self.database.already_in_league(player_info)):
                return self.successful(player, player_info)

            # otherwise got to figure them out by asking for their email
            return self.check_email(player)
        elif player.get_action_state().get_state() == IdentifyUser.EMAIL_STATE:
            # try figuring out who they are by their email
            self.check_email(player)
        else:
            # all other states we just ignore them
            pass

    def determine_player(self, messenger_user):
        """
            Determine the player given a messenger user

            Notes:
                if messenger gave email then use that
                otherwise just use the player's name as a lookup
        """
        try:
            email = messenger_user.get_email()
            if email is not None:
                player = self.platform.lookup_player_by_email(email)
            else:
                name = messenger_user.get_name()
                player = self.platform.lookup_player_by_name(name)
                LOGGER.debug("Found player by name:" + str(player))
            return player
        except IdentityException:
            return None

    def ask_email(self, player):
        """Sends a message asking for the players email"""

        # these are copies so can do what we like
        state = player.get_action_state()
        state_data = state.get_data()

        # set the number of wrong guesses and increment it
        if "wrongGuesses" not in state_data.keys():
            state_data["wrongGuesses"] = -1
        state_data["wrongGuesses"] += 1

        # if they have guessed wrong three times then lock them out
        if state_data["wrongGuesses"] > 3:
            LOGGER.info("Player ({}) is locked out".format(str(player)))
            state.set_state(IdentifyUser.LOCKED_OUT_STATE)
            message = Message(self.message.get_sender_id(),
                              message=LOCKED_OUT)
            self.messenger.send_message(message)

        # otherwise just ask them again
        else:
            message = Message(self.message.get_sender_id(),
                              message=ASK_FOR_EMAIL)
            self.messenger.send_message(message)
            state.set_state(IdentifyUser.EMAIL_STATE)

        # now want to save the changes we made
        state.set_data(state_data)
        player.set_action_state(state)
        self.database.save_player(player)

    def check_email(self, player):
        """Tries to lookup the player given they responded with their email"""
        email = parse_out_email(self.message.get_message())
        if email is None:
            self.ask_email(player)
        else:
            try:
                # lookup their player info and make sure they are not posing
                # as someone else
                player_info = self.platform.lookup_player_by_email(
                    email.lower())
                if not self.database.already_in_league(player_info):
                    return self.successful(player, player_info)
                sender = self.message.get_sender_id()
                message = "User {} is posing as {}".format(sender,
                                                           str(player_info))
                LOGGER.warning(message)
                state = IdentifyUser.IMPOSTER_STATE
                action_state = player.get_action_state()
                action_state.set_state(state)
                player.set_action_state(action_state)
                self.database.save_player(player)

                # let the user know their player account already in use
                self.messenger.send_message(Message(sender,
                                                    message=IMPOSTER))

            except IdentityException as e:
                LOGGER.debug("Unable to find email: {}".format(email))
                message = Message(self.message.get_sender_id(),
                                  message=EMAIL_NOT_FOUND)
                self.messenger.send_message(message)

                # ask again but eventually they will be locked out
                self.ask_email(player)
        return None

    def successful(self, player, player_info):
        """Upon being successful update the user to the next action"""
        LOGGER.info("Identified player: " + str(player_info))

        # send them a message - welcoming them to the league
        message = Message(self.message.get_sender_id(),
                          message=WELCOME_LEAGUE.format(player.get_name()))
        self.messenger.send_message(message)

        player.set_player_info(player_info)
        self.database.save_player(player)

        return self.initiate_action(self.message,
                                    self.action_map,
                                    WELCOME_KEY,
                                    player)
