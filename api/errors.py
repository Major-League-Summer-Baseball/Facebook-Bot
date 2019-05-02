
class FacebookException(Exception):
    pass


class IdentityException(Exception):
    pass


class NotCaptainException(Exception):
    pass


class BatterException(Exception):
    pass


class SubscriptionException(Exception):
    pass

PLATFORMMESSAGE = "Platform not available - try again later"


class PlatformException(Exception):
    pass


class OptionException(Exception):
    pass


class MultiplePlayersException(Exception):

    def __init__(self, message, players):
        super().__init__(message)
        self.players = players
