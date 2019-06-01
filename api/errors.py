'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds a list of errors that could occur
'''


PLATFORMMESSAGE = "Issue when communicating with website: {}"


class InvalidActionState(Exception):
    pass


class DatabaseException(Exception):
    pass


class FacebookException(Exception):
    pass


class MessengerException(Exception):
    pass


class IdentityException(Exception):
    pass


class NotCaptainException(Exception):
    pass


class BatterException(Exception):
    pass


class InvalidSubscription(Exception):
    pass


class PlatformException(Exception):
    pass


class OptionException(Exception):
    pass


class ActionException(Exception):
    pass


class MultiplePlayersException(Exception):

    def __init__(self, message, players):
        super().__init__(message)
        self.players = players
