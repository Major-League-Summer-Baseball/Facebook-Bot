'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: The subscriptions of the player
'''
from enum import Enum
from api.logging import LOGGER
from api.errors import SubscriptionException
from api.variables import SUBSCRIPTION_TIME_RANGE
from api.helper import difference_in_minutes_between_dates
import datetime
TRUTHINESS = ['true', '1', 't', 'y', 'yes',
              'yeah', 'yup', 'certainly', 'uh-huh', True]


class RelativeTimeEnum(Enum):
    """Holds an enumeration of the various relative times to use"""
    MORNING = "In morning"
    HOUR_BEFORE = "Hour before game"
    NIGHT_BEFORE = "Night before"


class Subscription():
    """Holds attibutes of a specific subscription to one team"""
    SUBCRIBED_KEY = "subscribed"
    TIME_KEY = "time"
    RELATIVE_TIME_KEY = "relative_time"
    MORNING_HOUR = 8
    NIGHT_BEFORE_HOUR = 8

    def __init__(self, dictionary=None):
        """Constructor"""
        # default to reminding before
        self.time = None
        self.subscribed = True
        self.relative_time = RelativeTimeEnum.MORNING
        if dictionary is not None:
            # if given a dictionary loads what values are in the dictionary
            self.from_dictionary(dictionary)

    def from_dictionary(self, dictionary):
        """Sets the properties from a given dictionary"""
        if Subscription.SUBCRIBED_KEY in dictionary.keys():
            self.subscribed = (dictionary[Subscription.SUBCRIBED_KEY]
                               in TRUTHINESS)
        else:
            # can assume not subscribed
            self.subscribed = False
        if Subscription.TIME_KEY in dictionary.keys():
            value = dictionary[Subscription.TIME_KEY]
            self.time = datetime.datetime.strptime(value, "%H:%M").time()
        else:
            self.time = None
        if Subscription.RELATIVE_TIME_KEY in dictionary.keys():
            self.relative_time = RelativeTimeEnum(
                dictionary[Subscription.RELATIVE_TIME_KEY])
        else:
            self.relative_time = None

    def to_dictionary(self):
        """Returns a dictionary representation of the object"""
        result = {Subscription.SUBCRIBED_KEY: self.subscribed}
        if self.time is not None:
            result[Subscription.TIME_KEY] = self.time.strftime("%H:%M")
        if self.relative_time is not None:
            result[Subscription.RELATIVE_TIME_KEY] = self.relative_time.value
        return result

    def is_subscribed(self):
        """Returns whereh the subscription is in place or not"""
        return False if self.subscribed is None else self.subscribed

    def subscribed(self):
        """Activates the subscription"""
        self.subscribed = True

    def unsubscribed(self):
        """Deactivates the subscription"""
        self.subscribed = False

    def should_send_reminder(self,
                             gameDate, comparison=datetime.datetime.now()):
        """Returns whether the subscription calls for a game reminder
        Parameters:
            gameDate: the date of the game to give the reminder about
            comparison: an optional parameter if do not want to compare
            to right now (mainly for testing)
        Returns:
            within: True if the given time is within the subscription range
        """
        time = None
        relative_time = None
        if self.time is not None:
            time = datetime.datetime.combine(gameDate.date(), self.time)
        if self.relative_time is not None:
            if self.relative_time is RelativeTimeEnum.MORNING:
                relative_time = datetime.datetime.combine(gameDate.date(),
                                                          datetime.time(8, 0))
            elif self.relative_time is RelativeTimeEnum.HOUR_BEFORE:
                relative_time = gameDate - datetime.timedelta(hours=1)
            elif self.relative_time is RelativeTimeEnum.NIGHT_BEFORE:
                day_before = (gameDate - datetime.timedelta(days=1))
                relative_time = datetime.datetime.combine(day_before.date(),
                                                          datetime.time(20, 0))
        # check if right now is in the subscription reminder time frame
        c1 = (difference_in_minutes_between_dates(
            time, comparison) < SUBSCRIPTION_TIME_RANGE)
        c2 = (difference_in_minutes_between_dates(
            relative_time, comparison) < SUBSCRIPTION_TIME_RANGE)
        LOGGER.debug("Subscription {} and {}".format(str(c1), str(c2)))
        LOGGER.debug("relative time:{}, time: {}, comparison:{}".format(
            relative_time, time, comparison))
        return c1 or c2

    def set_relative_time(self, relative_enum):
        """Sets the relative time
        Parameters:
            relative_enum: the relative time to use (RelativeTimeEnum)
        Raises:
             SubscriptionException if unrecognized relative time given
        """
        if (relative_enum is RelativeTimeEnum.MORNING or
                relative_enum is RelativeTimeEnum.HOUR_BEFORE or
                relative_enum is RelativeTimeEnum.NIGHT_BEFORE):
            self.relative_time = relative_enum
            return
        message = "Unrecongized relative time: {}".format(relative_enum)
        LOGGER.error(message)
        raise SubscriptionException(message)

    def set_time(self, time):
        """Sets the time of the subscription
        Parameters:
            time: the datetime time to use for the subscription (Time)
        Raises:
             SubscriptionException if time is not of type datetime.Time
        """
        if (isinstance(time, datetime.time) or
                isinstance(time, datetime.datetime)):
            self.time = time
            return
        message = "Given time of the wrong type: {}".format(time)
        LOGGER.error(message)
        raise SubscriptionException(message)


class Subscriptions():
    """
    A model for what teams a player is subscribed to and whether subscribed
    to league updates as well
    """

    def __init__(self, dictionary=None):
        """Constructor"""
        self.league = True
        self.team_lookup = {}
        if dictionary is not None:
            # if given a dictionary loads what values are in the dictionary
            self.from_dictionary(dictionary)

    def from_dictionary(self, dictionary):
        """Sets the properties from a given dictionary"""
        self.team_lookup = {}
        for key, value in dictionary.items():
            if "league" in key.lower():
                self.league = value in TRUTHINESS
            else:
                if isinstance(value, Subscription):
                    value = value.to_dictionary()
                self.team_lookup[key] = Subscription(dictionary=value)

    def to_dictionary(self):
        """Returns the dictionary representation of the subscription"""
        result = {"league": self.league}
        for team_id, subscribed in self.team_lookup.items():

            result[str(team_id)] = subscribed.to_dictionary()
        return result

    def is_subscribed_to_league(self):
        """Returns whether subscribed to the league"""
        return self.league

    def subscribe_to_league(self):
        """Subcribed to the league"""
        self.league = True

    def unsubscribe_to_league(self):
        """Unsubscribe from the league"""
        self.league = False

    def is_subscribed_to_team(self, team_id):
        """Returns whether subscribed to the givem team"""
        if str(team_id) in self.team_lookup.keys():
            return self.team_lookup[str(team_id)].is_subscribed()
        else:
            return False

    def get_subscription_for_team(self, team_id):
        """Returns the subscription for the given team"""
        if str(team_id) in self.team_lookup.keys():
            return self.team_lookup[str(team_id)]
        return None

    def subscribe_to_team(self, team_id, subscription=None):
        """Subscribe to the given team
        Parameters:
            team_id: the id of the team to subscribe to
            subscription: the subscription policy for the team
                (otherwise use default)
        """
        if subscription is None:
            subscription = Subscription()
        self.team_lookup[str(team_id)] = subscription

    def unsubscribe_to_team(self, team_id):
        """Unsubscribe from the given team"""
        self.team_lookup.pop(str(team_id), None)
