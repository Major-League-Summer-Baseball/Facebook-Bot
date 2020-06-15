'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: The basic player
'''
from typing import List
from api.mlsb.typing import Team, PlayerInfo
from api.players.subscription import Subscriptions
from api.actions import ActionState, ActionKey
from api.errors import InvalidActionState, InvalidSubscription


class Player():

    IDENTIFIER = "Player"

    def __init__(self, messenger_id: str = None, name: str = None):
        self._messenger_id = messenger_id
        self._messenger_name = name
        self._player_info = None
        self._subscriptions = Subscriptions()
        self._action_state = ActionState(key=ActionKey.IDENTIFY_KEY)
        self._convenor = False
        self._teams = []
        self._teams_that_captain = []

    @staticmethod
    def get_messenger_search(messenger_id: str) -> dict:
        """Returns the search parameters when searching by messenger id"""
        return {"messenger_id": messenger_id}

    @staticmethod
    def get_player_search(player_info: PlayerInfo) -> dict:
        """Returns the search parameters when searching by player info"""
        return {"player_id": player_info["player_id"]}

    @staticmethod
    def from_dictionary(dictionary: dict) -> 'Player':
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

    def to_dictionary(self) -> dict:
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

    def messenger_search(self) -> dict:
        """Returns the search parameters when searching by messenger id"""
        return {"messenger_id": self._messenger_id}

    def get_name(self) -> str:
        """Gets the name of the player"""
        return self._messenger_name

    def get_action_state(self) -> ActionState:
        """Returns a copy of the state of the action the player is taking"""
        return ActionState.from_dictionary(self._action_state.to_dictionary())

    def set_action_state(self, action_state: ActionState) -> None:
        """Setter for the action state"""
        if isinstance(action_state, ActionState):
            self._action_state = action_state
        else:
            raise InvalidActionState("Incorrect type: expecting ActionState")

    def set_player_info(self, player_info: PlayerInfo) -> None:
        """Setter for the player info"""
        self._player_info = player_info

    def get_player_info(self) -> PlayerInfo:
        """Returns information about the player"""
        return self._player_info

    def get_player_id(self) -> int:
        """Return the id associated with this player"""
        return self._player_info[PlayerInfo.ID]

    def get_subscriptions(self) -> Subscriptions:
        """Returns a copy of the subscriptions"""
        return Subscriptions.from_dictionary(self._subscriptions
                                             .to_dictionary())

    def set_subscriptions(self, subscriptions: Subscriptions) -> None:
        """Sets the subscriptions"""
        if isinstance(subscriptions, Subscriptions):
            self._subscriptions = subscriptions
        else:
            message = "Incorrect type: expecting Subscriptions"
            raise InvalidSubscription(message)

    def is_convenor(self) -> bool:
        """Returns whether the given player is a convenor"""
        return self._convenor

    def make_convenor(self) -> None:
        """Gives the player convenor permissions"""
        self._convenor = True

    def remove_convenor(self) -> None:
        """Remove the player's convenor permissions"""
        self._convenor = False

    def get_team_ids(self) -> List[int]:
        """Get a list of team ids

        Returns:
            List[int]: a list of teams that player is part of
        """
        return self._teams

    def add_team(self, team: Team) -> None:
        """Add the player to the team and subscribed them to the team.

        Args:
            team (team): the team
        """
        team_id = team.get(Team.ID, None)
        if team_id is not None and team_id not in self._teams:
            self._teams.append(team[Team.ID])
            self._subscriptions.subscribe_to_team(team[Team.ID])

    def remove_team(self, team: Team) -> None:
        """Remove the player from the team

        Args:
            team (Team): the team
        """
        try:
            self._teams.remove(team[Team.ID])
            self._subscriptions.unsubscribe_to_team(team[Team.ID])
        except ValueError:
            pass

    def get_teams_captain(self) -> List[int]:
        """Get a list of teams that the players is a captain.

        Returns:
            List[int]: a list of team ids
        """
        return self._teams_that_captain

    def make_captain(self, team: Team) -> None:
        """Make the player a captain of the given team.

        Args:
            team (Team): the team
        """
        team_id = team.get(Team.ID, None)
        if team_id is not None and team_id not in self._teams_that_captain:
            self._teams_that_captain.append(team_id)

    def remove_captain(self, team: Team) -> None:
        """Remove the captainship for the given team.

        Args:
            team (Team): the team
        """
        try:
            self._teams_that_captain.remove(team.get(Team.ID))
        except ValueError:
            pass

    def is_captain(self, team_id: int = None) -> bool:
        """Is the player a captain of the given team.

        Args:
            team_id (int, optional): if want to check captain of some team.
                                     Defaults to None.

        Returns:
            bool: True if player is a captain otherwise False
        """
        if team_id is None:
            return self._convenor or len(self._teams_that_captain) > 0
        else:
            return self._convenor or team_id in self._teams_that_captain

    def __str__(self) -> str:
        return "{} - {}".format(self._messenger_name, self._messenger_id)
