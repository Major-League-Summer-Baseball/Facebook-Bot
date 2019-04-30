'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: The subscriptions of the player
'''
TRUTHINESS = ['true', '1', 't', 'y', 'yes',
              'yeah', 'yup', 'certainly', 'uh-huh', True]


class Subscription():
    """
    A model for what teams a player is subscribed to and whether subscribed
    to league updates as well
    """

    def __init__(self, dictionary=None):
        """Constructor"""
        if dictionary is not None:
            self.from_dictionary(dictionary)

    def from_dictionary(self, dictionary):
        """Sets the properties from a given dictionary"""
        self.team_lookup = {}
        for key, value in dictionary.items():
            if (key.lower() == "league"):
                self.league = value in TRUTHINESS
            else:
                self.team_lookup[key] = value in TRUTHINESS

    def to_dictionary(self, dictionary):
        """Returns the dictionary representation of the subscription"""
        result = {"league": self.league}
        for team, subscribed in dictionary.items():
            result[str(team)] = subscribed

    def is_subscribed_to_league(self):
        """Returns whether subscribed to the league"""
        return self.league

    def subscribe_to_league(self):
        """Subcribed to the league"""
        self.league = True

    def unsubscribe_to_league(self):
        self.league = False

    def subscribe_to_team(self, team_id):
        self.team_lookup[team_id] = True

    def unsubscribe_to_team(self, team_id):
        if team_id in self.team_lookup.keys():
            self.team_lookup[team_id] = True
