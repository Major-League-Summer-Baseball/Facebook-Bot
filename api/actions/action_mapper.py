'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: The main entry point for actions
'''
from api.actions import ActionInterface
from api.actions.identify_user import IdentifyUser
from api.errors import ActionException


class ActionMapper(ActionInterface):
    """The main entry point for actions"""

    def process(self, action_map):
        # if not a recognized user then need to identify them
        player = self.database.get_player(self.message.get_sender_id())
        if player is None:
            return IdentifyUser(self.database,
                                self.platform,
                                self.messenger,
                                self.message).process(action_map)
        action = player.get_action_state()
        if action is None:
            return IdentifyUser(self.database,
                                self.platform,
                                self.messenger,
                                self.message).process(action_map)
        for action_key, action in action_map.items():
            if action.get_id() == action_key:
                return action(self.database,
                              self.platform,
                              self.messenger,
                              self.message).process(action_map)
        raise ActionException("Unrecognized action state")
