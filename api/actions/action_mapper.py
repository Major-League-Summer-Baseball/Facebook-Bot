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
    """The main point for actions"""

    def process(self, action_map):
        # if a not recognized user then need to identify them
        user = self.database.get_user(self.message.get_sender_id())
        if user is None:
            return IdentifyUser(self.database,
                                self.platform,
                                self.messenger,
                                self.message).process()
        if 'action' not in user.keys():
            return IdentifyUser(self.database,
                                self.platform,
                                self.messenger,
                                self.message).process()
        action = user['action']
        for action_key, action in action_map.items():
            if action["id"] == action_key:
                return action(self.database,
                              self.platform,
                              self.messenger,
                              self.message).process()
        raise ActionException("Current action state")
