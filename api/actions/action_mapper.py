'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: The main entry point for actions
'''
from api.logging import LOGGER
from api.actions import Action
from api.actions.identify_user import IdentifyUser
from api.errors import ActionException


class ActionMapper(Action):
    """The main entry point for actions"""

    def process(self, message, action_map):
        # if not a recognized user then need to identify them
        player = self.database.get_player(message.get_sender_id())
        if player is None:
            return IdentifyUser(self.database,
                                self.platform,
                                self.messenger).process(message, action_map)
        action = player.get_action_state()
        if action is None:
            return IdentifyUser(self.database,
                                self.platform,
                                self.messenger).process(message, action_map)
        LOGGER.debug("Current state of player:" +
                     player.get_action_state().get_id() + " " + str(player))
        action = action_map.get(player.get_action_state().get_id(), None)
        if action is not None:
            return action(self.database,
                          self.platform,
                          self.messenger).process(message, action_map)
        raise ActionException("Unrecognized action state")
