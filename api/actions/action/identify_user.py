'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: Action to determine the to identify user to someone in the legaue
'''
from typing import Tuple, List
from api.actions import ActionKey, ActionState
from api.actions.action import Action
from api.settings.message_strings import Registration
from api.parsers import parse_out_email
from api.logging import LOGGER
from api.message import Message
from api.players.player import Player
from api.errors import IdentityException


class IdentifyUser(Action):
    """
        Action used to identify a given messenger user to a player in league
    """
    EMAIL_STATE = "Asking for email"
    UNKNOWN_STATE = "Cannot find the user, user should consult convenors"
    IMPOSTER_STATE = "Trying to steal someone's else email"
    LOCKED_OUT_STATE = " Locked out for trying 3 different emails"
    NUMBER_OF_TRIES = 3

    def process(self, player: Player,
                message: Message) -> Tuple[ActionState, List[Message],
                                           ActionKey]:
        """
            The main entry point

            Notes:
                First use information given by the messenger to lookup player.
                Second if not found ask them for their email
                    and use the given email to lookup player.
                Lock out user if guess too many emails.
        """
        self.message = message
        if (player.get_action_state() is None or
           player.get_action_state().get_state() is None):
            # otherwise got to figure them out by asking for their email
            state = ActionState(key=ActionKey.IDENTIFY_KEY,
                                state=IdentifyUser.EMAIL_STATE)
            player.set_action_state(state)
            return (player,
                    [Message(message.get_sender_id(),
                             message=Registration.EMAIL_PROMPT.value)],
                    None)
        elif player.get_action_state().get_state() == IdentifyUser.EMAIL_STATE:
            # try figuring out who they are by their email
            return self.check_email(player)
        else:
            # all other states we just ignore them
            return (player, [], None)

    def ask_email(self, player):
        """Sends a message asking for the players email"""
        messages = []

        # these are copies so can do what we like
        state = player.get_action_state()
        state_data = state.get_data()

        # set the number of wrong guesses and increment it
        if "wrongGuesses" not in state_data.keys():
            state_data["wrongGuesses"] = -1
        state_data["wrongGuesses"] += 1

        # if they have guessed wrong three times then lock them out
        if state_data["wrongGuesses"] > IdentifyUser.NUMBER_OF_TRIES:
            LOGGER.info("Player ({}) is locked out".format(str(player)))
            state.set_state(IdentifyUser.LOCKED_OUT_STATE)
            message = Message(self.message.get_sender_id(),
                              message=Registration.LOCKED_OUT.value)
            messages.append(message)

        # otherwise just ask them again
        else:
            message = Message(self.message.get_sender_id(),
                              message=Registration.EMAIL_PROMPT.value)
            messages.append(message)
            state.set_state(IdentifyUser.EMAIL_STATE)

        # remember the data for next time
        player.set_action_state(state.set_data(state_data))
        return (player, messages, None)

    def check_email(self, player: Player):
        """Tries to lookup the player given they responded with their email"""
        email = parse_out_email(self.message.get_message())
        if email is None:
            return self.ask_email(player)
        else:
            try:
                # lookup their player info and make sure they are not posing
                # as someone else
                player_info = self.platform.lookup_player_by_email(
                    email.lower())
                if self.database.already_in_league(player_info):
                    sender = self.message.get_sender_id()
                    p_info = str(player_info)
                    LOGGER.warning(f"User {sender} is posing as {p_info}")
                    state = IdentifyUser.IMPOSTER_STATE
                    action_state = player.get_action_state().set_state(state)
                    player.set_action_state(action_state)

                    # let the user know their player account already in use
                    return (player,
                            [Message(sender,
                                     message=Registration.IMPOSTER.value)],
                            None)

                # they are good to go
                LOGGER.info("Identified player: " + str(player_info))
                player.set_player_info(player_info)
                return (player, [], ActionKey.WELCOME_KEY)

            except IdentityException:
                LOGGER.debug("Unable to find email: {}".format(email))
                message = Message(self.message.get_sender_id(),
                                  message=Registration.EMAIL_NOT_FOUND.value)
                (state, messages, next_action) = self.ask_email(player)
                # ask again but eventually they will be locked out
                return (state, [message] + messages, next_action)
