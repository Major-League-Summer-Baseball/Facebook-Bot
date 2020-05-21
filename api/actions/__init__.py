'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: The state related to some action
'''
from copy import deepcopy
from enum import Enum
from api.errors import ActionException


class ActionKey(Enum):
    """An enumeration of all actions keys."""
    WELCOME_KEY = "welcome"
    IDENTIFY_KEY = "identify user"
    HOME_KEY = "homescreen"
    SUBMIT_SCORE_KEY = "submit score"

    def __str__(self) -> str:
        """Returns the string representation of the action key"""
        return str(self.value)


class ActionState():
    """Holds the state of the action"""

    def __init__(self, key: ActionKey, state: str = None, data: dict = {}):
        """Constructor
        Parameters:
            key: the key of the action (maps state to action class)
            state: the state of the action
            data: data related to the action and stored while processing
        Notes:
            key needs to be set as a parameter or in dictionary
        """
        self._key = key
        self._state = state
        self._data = data

    def get_data(self) -> dict:
        """Get the data dictionary of the action"""
        return deepcopy(self._data)

    def set_data(self, data: dict) -> 'ActionState':
        """Set the data dictionary of the action"""
        self._data = deepcopy(data)
        return self

    def set_state(self, state: ActionKey) -> 'ActionState':
        """Setter for the state"""
        self._state = state
        return self

    def get_state(self) -> ActionKey:
        """Getter for the state"""
        return self._state

    def get_id(self) -> str:
        """Getter for the id of the action"""
        return self._key

    @staticmethod
    def from_dictionary(dictionary: dict) -> None:
        """Loads action state from a dictionary"""
        key = dictionary.get("id", None)
        if key is None:
            raise ActionException("Action id not set")
        return ActionState(key, data=dictionary.get("data", {}),
                           state=dictionary.get("state", None))

    def to_dictionary(self) -> dict:
        """Return a dictionary representation of the action state"""
        return {"id": self._key,
                "data": self._data,
                "state": self._state}

    def __str__(self) -> str:
        """Returns the string representation of the action state"""
        return "Id: {}, data:{}:, state:{}".format(self._key,
                                                   str(self._data),
                                                   self._state)
