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
from api.errors import ActionException
from copy import deepcopy


class ActionState():
    """Holds the state of the action"""

    def __init__(self, key=None, state=None, data={}, dictionary=None):
        """Constructor
        Parameters:
            key: the key of the action (maps state to action class)
            state: the state of the action
            dictionary: the save dictionary of the action state
        Notes:
            key needs to be set as a parameter or in dictionary
        """
        self._key = key
        self._state = state
        self._data = {}
        if dictionary is not None:
            self.from_dictionary(dictionary)
        if self._key is None:
            raise ActionException("Action id not set")

    def get_data(self):
        """Get the data dictionary of the action"""
        return deepcopy(self._data)

    def set_data(self, data):
        """Set the data dictionary of the action"""
        self._data = data

    def set_state(self, state):
        """Setter for the state"""
        self._state = state

    def get_state(self):
        """Getter for the state"""
        return self._state

    def get_id(self):
        """Getter for the id of the action"""
        return self._key

    def from_dictionary(self, dictionary):
        """Loads action state from a dictionary"""
        self._key = (self._key if dictionary.get("id", None) is None
                     else dictionary.get("id"))
        self._data = (self._data if dictionary.get("data", None) is None
                      else dictionary.get("data"))
        self._state = (self._state if dictionary.get("state", None) is None
                       else dictionary.get("state"))

    def to_dictionary(self):
        """Return a dictionary representation of the action state"""
        return {"id": self._key,
                "data": self._data,
                "state": self._state}

    def __str__(self):
        return "Id: {}, data:{}:, state:{}".format(self._key,
                                                   str(self._data),
                                                   self._state)


class ActionInterface():
    """
    The action interface
    """

    def __init__(self, database, platform, messenger):
        """Constructor"""
        self.database = database
        self.platform = platform
        self.messenger = messenger

    def process(self, message, action_map):
        """Process the action
        Parameters:
            action_map: maps action ids to their classes
        """
        raise NotImplementedError("Action needs to implement process method")

    def initiate_action(self, message, action_map, next_action_key, player):
        """Initiate the action for the given key and update the player state"""
        player.set_action_state(ActionState(key=next_action_key))
        self.database.save_player(player)

        next_action = action_map[next_action_key]
        return next_action(self.database,
                           self.platform,
                           self.messenger).process(message, action_map)
