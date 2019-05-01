'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: Used so bot can connect to different messengers (Facebook, Kik, etc)
'''


class Messenger():
    """
    This is an abstract class that just used to specify the methods
    that need to be implemented by the messenger
    """

    def __init__(self):
        pass

    @abstractmethod
    def send_message(self, message):
        """Sends the given message.
        Parameters:
            message: the message to send (Message)
        """
        raise NotImplementedError("Messenger needs to implement send message")

    @abstractmethod
    def parse_response(self, response):
        """Parses the message from the response given by the messenger.
        Parameters:
            response: response object (dependent upon messenger)
        Returns:
            message: the message parsed from the response (Message)
        """
        raise NotImplementedError("Messenger needs to implement parse message")

    @abstractmethod
    def lookup_user_id(self, user_id):
        """Lookups the user information associated with the given id
        Parameters:
            user_id: the id of the user (dependent upon messenger)
        Returns:
            user: a user object return from the messenger (Object/Dictionary)
        """
        raise NotImplementedError("Messenger needs to imeplement user lookup")
