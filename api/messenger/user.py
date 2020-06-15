'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: Holds information about the user from the messenger
'''


class User():
    """
        Holds information about the user where info comes from the
        messenger platform
    """

    def __init__(self, sender_id: str, name: str = None,
                 email: str = None, gender: str = None):
        """Constructor"""
        self._name = name
        self._email = email
        self._gender = gender
        self.sender_id = sender_id

    def get_sender_id(self) -> str:
        return self.sender_id

    def get_email(self) -> str:
        """Returns the email of the user"""
        return self._email

    def get_name(self) -> str:
        """Returns the name of the user"""
        return self._name

    def get_gender(self) -> str:
        """Returns the gender of the person"""
        return self._gender
