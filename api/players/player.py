'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: The basic player
'''
from api.players.subscription import Subscriptions
from api.actions import ActionState, ActionKey
from api.errors import InvalidActionState, InvalidSubscription


class Player():

    IDENTIFIER = "Player"

    def __init__(self, messenger_id=None, name=None):
        self._messenger_id = messenger_id
        self._messenger_name = name
        self._player_info = None
        self._subscriptions = Subscriptions()
        self._action_state = ActionState(key=ActionKey.IDENTIFY_KEY)
        self._convenor = False
        self._teams = []
        self._teams_that_captain = []

    @staticmethod
    def get_messenger_search(messenger_id):
        """Returns the search parameters when searching by messenger id"""
        return {"messenger_id": messenger_id}

    @staticmethod
    def get_player_search(player_info):
        """Returns the search parameters when searching by player info"""
        return {"player_id": player_info["player_id"]}

    @staticmethod
    def from_dictionary(dictionary):
        """Sets the player attributes from the given dictionary"""
        messenger_id = dictionary.get("messenger_id", None)

        messenger_name = dictionary.get("messenger_name", None)
        player = Player(messenger_id=messenger_id, name=messenger_name)
        player._player_info = dictionary.get("player_info", None)
        player._teams = dictionary.get("teams", [])
        player._teams_that_captain = dictionary.get("captain", [])
        player._convenor = dictionary.get("convenor", False)

        # deal with subscriptions
        subs = dictionary.get('subscriptions', None)
        if subs is not None:
            if isinstance(subs, Subscriptions):
                # ensures have a deepcopy
                subs = subs.to_dictionary()
            player._subscriptions = Subscriptions.from_dictionary(subs)

        # deal with action state
        action_state = dictionary.get("action_state", None)
        if action_state is not None:
            if isinstance(action_state, ActionState):
                # ensures have a deepcopy
                action_state = action_state.to_dictionary()
            player._action_state = ActionState.from_dictionary(action_state)
        return player

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
            "action_state": self._action_state.to_dictionary(),
            "convenor": self._convenor}

    def messenger_search(self):
        """Returns the search parameters when searching by messenger id"""
        return {"messenger_id": self._messenger_id}

    def get_name(self):
        """Gets the name of the player"""
        return self._messenger_name

    def get_action_state(self):
        """Returns a copy of the state of the action the player is taking"""
        return ActionState.from_dictionary(self._action_state.to_dictionary())

    def set_action_state(self, action_state):
        """Setter for the action state"""
        if isinstance(action_state, ActionState):
            self._action_state = action_state
        else:
            raise InvalidActionState("Incorrect type: expecting ActionState")

    def set_player_info(self, player_info):
        """Setter for the player info"""
        self._player_info = player_info

    def get_player_info(self):
        """Returns information about the player"""
        return self._player_info

    def get_player_id(self):
        """Return the id associated with this player"""
        return self._player_info["player_id"]

    def get_subscriptions(self):
        """Returns a copy of the subscriptions"""
        return Subscriptions.from_dictionary(self._subscriptions
                                             .to_dictionary())

    def set_subscriptions(self, subscriptions):
        """Sets the subscriptions"""
        if isinstance(subscriptions, Subscriptions):
            self._subscriptions = subscriptions
        else:
            message = "Incorrect type: expecting Subscriptions"
            raise InvalidSubscription(message)

    def is_convenor(self):
        """Returns whether the given player is a convenor"""
        return self._convenor

    def make_convenor(self):
        """Gives the player convenor permissions"""
        self._convenor = True

    def remove_convenor(self):
        """Remove the player's convenor permissions"""
        self._convenor = False

    def get_team_ids(self):
        """Get a list of team ids that player is part of"""
        return self._teams

    def add_team(self, team):
        """Add a team to the list of teams the player is part of"""
        team_id = team.get("team_id", None)
        if team_id is not None and team_id not in self._teams:
            self._teams.append(team["team_id"])
            self._subscriptions.subscribe_to_team(team['team_id'])

    def remove_team(self, team):
        """Removes the player from the given team"""
        try:
            self._teams.remove(team["team_id"])
            self._subscriptions.unsubscribe_to_team(team["team_id"])
        except ValueError:
            pass

    def get_teams_captain(self):
        """Gets a list of team ids that the player is captain of"""
        return self._teams_that_captain

    def make_captain(self, team):
        """Adds the player as a captain"""
        team_id = team.get("team_id", None)
        if team_id is not None and team_id not in self._teams_that_captain:
            self._teams_that_captain.append(team_id)

    def remove_captain(self, team):
        """Remove the captainship from the player for the given team"""
        try:
            self._teams_that_captain.remove(team["team_id"])
        except ValueError:
            pass

    def is_captain(self, team_id=None):
        """Returns whether the given player is a captain

            Parameters:
                team_id: if given then checks if player captain of given team
        """
        if team_id is None:
            return self._convenor or len(self._teams_that_captain) > 0
        else:
            return self._convenor or team_id in self._teams_that_captain

    def __str__(self):
        return "{} - {}".format(self._messenger_name, self._messenger_id)
