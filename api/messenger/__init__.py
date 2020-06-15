'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: Used so bot can connect to different messengers (Facebook, Kik, etc)
'''
from api.message import Message
from api.pl

class Messenger():
    """
    This is an abstract class used to specify the methods
    that need to be implemented by the messenger
    """

    def __init__(self):
        pass

    def send_message(self, message: Message) -> None:
        """Sends the given message

        Args:
            message (Message): the message to send

        Raises:
            NotImplementedError: to be implemented by child
        """
        raise NotImplementedError("Messenger needs to implement send message")

    def parse_response(self, response: dict):
        """[summary]

        Args:
            response (dict): response object (dependent upon messenger)

        Raises:
            NotImplementedError: to be implemented by child
        """
        raise NotImplementedError("Messenger needs to implement parse message")

    def lookup_user_id(self, user_id: str) -> 'User':
        """Lookup the user by the id

        Args:
            user_id (str): [description]

        Returns
        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError("Messenger needs to imeplement user lookup")
