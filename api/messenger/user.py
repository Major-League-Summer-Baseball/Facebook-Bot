'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: Holds information about the user from the messenger
'''


class User():
    """Holds information about the user where info comes from messenger"""

    def __init__(self, name=None, email=None, gender=None):
        """Constructor"""
        self.name = name
        self.email = email
        self.gender = gender

    def get_email(self):
        """Returns the email of the user"""
        return self.email

    def get_name(self):
        """Returns the name of the user"""
        return self.name

    def get_gender(self):
        """Returns the gender of the person"""
        return self.gender
