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

    def __init__(self, database, messenger, message):
        """Constructor"""
        self.database = database
        self.message = message
        self.messenger = messenger

    def process(self):
        """Processes the given Facebook Id"""
        user = self.database.get_user(self.message.get_sender_id())
        if user is None:
            return IdentifyUser(self.database,
                                self.messenger,
                                self.message).process()
        if 'action' not in user.keys():
            return IdentifyUser(self.database,
                                self.messenger,
                                self.message).process()
        action = user['action']
        if action == IdentifyUser.ACTION_IDENTIFIER:
            return IdentifyUser(self.database,
                                self.messenger,
                                self.message).process()
