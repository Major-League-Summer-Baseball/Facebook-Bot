'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: The basic player
'''
from api.players.subscription import Subscriptions
from api.actions import ActionState
from api.variables import IDENTIFY_KEY


class Player():

    IDENTIFIER = "Player"

    def __init__(self, messenger_id=None, name=None, dictionary=None):
        self._messenger_id = messenger_id
        self._messenger_name = name
        self._player_info = None
        self._subscriptions = Subscriptions()
        self._action_state = ActionState(key=IDENTIFY_KEY)
        self._convenor = False
        self._teams = []
        self._teams_that_captain = []
        if dictionary is not None:
            self.from_dictionary(dictionary)

    def from_dictionary(self, dictionary):
        """Sets the player attributes from the given dictionary"""
        self._messenger_id = (self._messenger_id
                              if dictionary.get("messenger_id", None) is None
                              else dictionary.get("messenger_id"))

        messenger_name = dictionary.get("messenger_name", None)
        self._messenger_name = (self._messenger_name
                                if messenger_name is None
                                else messenger_name)

        self._player_info = (self._player_info
                             if dictionary.get("player_info", None) is None
                             else dictionary.get("player_info"))

        self._teams = (self._teams
                       if dictionary.get("teams", None) is None
                       else dictionary.get("teams"))

        self._teams_that_captain = (self._teams_that_captain
                                    if dictionary.get("captain", None) is None
                                    else dictionary.get("captain"))

        self._convenor = (self._convenor
                          if dictionary.get("convenor", None) is None
                          else dictionary.get("convenor"))

        subscriptions = dictionary.get('subscriptions', None)
        if subscriptions is not None:
            if isinstance(subscriptions, Subscriptions):
                value = subscriptions.to_dictionary()
                self._subscriptions = Subscriptions(dictionary=value)
            else:
                self._subscriptions = Subscriptions(dictionary=subscriptions)

        action_state = dictionary.get("action_state", None)
        if action_state is not None:
            if isinstance(action_state, ActionState):
                value = action_state.to_dictionary()
                self._action_state = ActionState(None, dictionary=value)
            else:
                self._action_state = ActionState(None, dictionary=action_state)

    def to_dictionary(self):
        """Returns the dictionary representation of the player"""
        player_id = None
        if (self._player_info is not None and
                "player_id" in self._player_info.keys()):
            player_id = self._player_info["player_id"]
        return {
            "messenger_name": self._messenger_name,
            "messenger_id": self._messenger_id,
            "player_info": self._player_info,
            "player_id": player_id,
            "teams": self._teams,
            "captain": self._teams_that_captain,
            "subscriptions": self._subscriptions.to_dictionary(),
            "action_state": self._action_state.to_dictionary()}

    @staticmethod
    def get_messenger_search(self, messenger_id):
        """Returns the search parameters when searching by messenger id"""
        return {"messenger_id": messenger_id}

    @staticmethod
    def get_player_search(self, player_info):
        """Returns the search parameters when searching by player info"""
        return {"player_id": player_info["player_id"]}

    def get_action_state(self):
        """Returns the current state of the action the player is taking"""
        return self._action_state

    def set_action_state(self, action_state):
        """Setter for the action state"""
        self._action_state = action_state

    def set_player_info(self, player_info):
        """Setter for the player info"""
        self._player_info = player_info

    def get_player_info(self):
        """Returns whether information about the player"""
        return self._player_info

    def get_player_id(self):
        """Return the id associated with this player"""
        return self._player_info["player_id"]

    def get_subscription(self):
        """Returns the what the player is subscribed to"""
        return self._subscription

    def is_captain(self, team_id):
        """Returns whether the given player is a captain"""
        return self._convenor or len(self._teams_that_captain) > 0

    def is_convenor(self):
        """Returns whether the given player is a convenor"""
        return self._convenor

    def make_convenor(self):
        """Gives the player convenor permissions"""
        self._convenor = True

    def demote_convenor(self):
        """Demote the player's convenor permissions"""
        self._convenor = False

    def get_team_ids(self):
        """Get a list of team ids that player is part of"""
        return self._teams

    def add_team(self, team):
        """Add a team to the list of teams the player is part of"""
        # just need the ids
        self._teams.append(team["team_id"])

    def remove_team(self, team):
        """Removes the player from the given team"""
        try:
            self._teams.remove(team["team_id"])
        except ValueError:
            pass

    def get_teams_captain(self):
        """Gets a list of team ids that the player is captain of"""
        return self._teams_that_captain

    def add_captain(self, team):
        """Adds the player as a captain"""
        self._teams_that_captain.append(team["team_id"])

    def remove_captain(self, team):
        """Remove the captainship from the player for the given team"""
        try:
            self._teams_that_captain.remove(team["team_id"])
        except ValueError:
            pass
