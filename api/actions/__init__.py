'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds various actions of the Facebook bot
    An actions is a combination of various states
    that together form a coherent action that user can perform
    E.g. Submit a score, Subscribe to a team
    All actions should keep track of their own state
'''
from api.actions.identify_user import IdentifyUser


class Action():
    """
    This is the entry point into any action
    """

    def __init__(self, database, platform, messenger, message):
        """Constructor"""
        self.database = database
        self.platform = platform
        self.message = message
        self.messenger = messenger

    def process(self, action_map):
        """Processes the given message
        Parameters:
            action_map: a map for the given aciton id to their actions classes
        Returns:
            the result of the action that is processed
        Raises:
            ActionException: if does not recognize what action to take
        """
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
        raise
