'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: The class that processes the main entry point for actions
'''
from api.logging import LOGGER
from api.database import DatabaseInterface
from api.platform import PlatformService
from api.messenger import Messenger
from api.messenger.user import User
from api.players.player import Player
from api.actions import ActionState, ActionKey
from api.actions.action import Action
from api.message import Message
from api.errors import ActionException, IdentityException


class ActionProcessor():
    """Processes all the actions"""
    def __init__(self, database: DatabaseInterface, platform: PlatformService,
                 messenger: Messenger) -> 'ActionProcessor':
        """Returns an object that can process messages"""
        self.database = database
        self.platform = platform
        self.messenger = messenger

    def process(self, message: Message, action_map: dict) -> None:
        """Process the given message using the given action map

        Args:
            message (Message): the message to process
            action_map (dict): mapping actions keys to their implementations

        Returns:
            [type]: [description]
        """
        # if not a recognized user then need to identify them
        player = self.database.get_player(message.get_sender_id())
        if player is None:
            # first time we have ever received a response
            messenger_id = message.get_sender_id()
            messenger_user = self.messenger.lookup_user_id(messenger_id)
            player_info = self.determine_player(messenger_user)
            player = self.database.create_player(messenger_id,
                                                 messenger_user.get_name())
            self.database.save_player(player)

            # if we know the player info already then can just skip
            # and welcome them to the league
            if (player_info is not None and
                    not self.database.already_in_league(player_info)):
                player.set_player_info(player_info)
                player.set_action_state(ActionState(ActionKey.WELCOME_KEY))
                self.database.save_player(player)
                action = self.get_action(ActionKey.WELCOME_KEY, action_map)
                return self._process(action, action_map, player, message)

            # will need to ask for their email to try to identify them
            player.set_action_state(ActionState(ActionKey.IDENTIFY_KEY))
            self.database.save_player(player)
            action = self.get_action(ActionKey.IDENTIFY_KEY, action_map)
            return self._process(action, action_map, player, message)

        # if no action is recorded then still need to identify them
        if player.get_action_state() is None:
            player.set_action_state(ActionState(ActionKey.IDENTIFY_KEY))
            self.database.save_player(player)
            action = self.get_action(ActionKey.IDENTIFY_KEY, action_map)
            return self._process(action, action_map, player, message)

        # now have some action to take and log their current status
        state_key = player.get_action_state().get_id()
        player_info = str(player)
        LOGGER.debug(f"Current state of player: {state_key} {player_info}")
        action_to_take = self.get_action(state_key,
                                         action_map)
        return self._process(action_to_take, action_map, player, message)

    def _process(self, action: Action, action_map: dict, player: Player,
                 message: Message) -> None:
        """Processes the given action and subsequent actions"""
        (player, messages, next_action) = action.process(player, message)

        # send all the messages
        for message in messages:
            self.messenger.send_message(message)

        # setup next action is there is one
        if (next_action is not None):
            player.set_action_state(ActionState(key=next_action))

        # remember the action state
        self.database.save_player(player)

        # process the next action now
        if (next_action is not None):
            self._process(self.get_action(next_action, action_map),
                          action_map, player, message)

    def determine_player(self, messenger_user: User) -> dict:
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

    def get_action(self, key: ActionKey, action_map: dict) -> Action:
        """Returns the action for the given key"""

        LOGGER.debug(f"Getting next action for {key}")
        action = action_map.get(key, None)
        if action is None:
            raise ActionException("Unrecognized action state")
        return action(self.database, self.platform)
