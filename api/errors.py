
class FacebookException(Exception):
    pass


class IdentityException(Exception):
    pass

class NotCaptainException(Exception):
    pass

PLATFORMMESSAGE = "Platform not available - try again later"
class PlatformException(Exception):
    pass

class MultiplePlayersException(Exception):
    def __init__(self, message, players):
        super().__init__(message)
        self.players = players
