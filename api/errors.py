'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds a list of errors that could occur
'''
PLATFORMMESSAGE = "Issue when communicating with website: {}"


class BotException(Exception):
    """A general issue with the bot programming."""
    pass


class InvalidActionState(BotException):
    """Somehow the action state is invalid."""
    pass


class InvalidSubscription(BotException):
    """The players subscriptions are invalid."""
    pass


class NotCaptainForAnyTeam(BotException):
    """Asking to submit scores but not a captain."""
    pass


class IdentityException(BotException):
    """Unable to identify the user."""
    pass


class OptionException(BotException):
    """The message option was not initialized properly."""
    pass


class ActionException(BotException):
    """The action could not be processed."""
    pass


class MessengerException(Exception):
    """An issue that might be encountered when sending and receiving messages
       from a given messenger implementation.
    """
    pass


class FacebookException(MessengerException):
    """An issue that might be encountered when sending and receiving messages
       when using facebook apis and data.
    """
    pass


class UnableToSendMessage(FacebookException):
    """Unable to send the Facebook message."""
    pass


class UnableToLookupUserInformation(FacebookException):
    """Unable to lookup facebook info on the user."""
    pass


class UnableToFindSender(FacebookException):
    """Got a message from some unknown sender."""
    pass


class DatabaseException(Exception):
    """An issue when reading/writing to bot database."""
    pass


class PlatformException(Exception):
    """An issue when communicating with the platform"""
    pass


class TeamDoesNotExist(PlatformException):
    """The team does not exist"""
    pass


class GameDoesNotExist(PlatformException):
    """The game does not exist"""
    pass


class NotCaptainException(PlatformException):
    """The player making the request is not the captain"""
    pass


class BatterException(Exception):
    pass


class MultiplePlayersException(Exception):

    def __init__(self, message, players):
        super().__init__(message)
        self.players = players
