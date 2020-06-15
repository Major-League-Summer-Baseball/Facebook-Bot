'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: The subscriptions of the player
'''
from enum import Enum
from api.logging import LOGGER
from api.errors import InvalidSubscription
from api.variables import SUBSCRIPTION_TIME_RANGE
from api.helper import difference_in_minutes_between_dates
from datetime import datetime, time, timedelta
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

    def __init__(self):
        """Constructor"""
        # default to reminding before
        self.time = None
        self.subscribed = True
        self.relative_time = RelativeTimeEnum.MORNING

    @staticmethod
    def from_dictionary(dictionary: dict) -> 'Subscription':
        """Parses a subscription from a dictionary"""
        subscription = Subscription()
        if Subscription.SUBCRIBED_KEY in dictionary.keys():
            subscription.subscribed = (dictionary[Subscription.SUBCRIBED_KEY]
                                       in TRUTHINESS)
        else:
            # can assume not subscribed
            subscription.subscribed = False
        if Subscription.TIME_KEY in dictionary.keys():
            value = dictionary[Subscription.TIME_KEY]
            subscription.time = datetime.strptime(value, "%H:%M").time()
        else:
            subscription.time = None
        if Subscription.RELATIVE_TIME_KEY in dictionary.keys():
            subscription.relative_time = RelativeTimeEnum(
                dictionary[Subscription.RELATIVE_TIME_KEY])
        else:
            subscription.relative_time = None

        return subscription

    def to_dictionary(self) -> dict:
        """Returns a dictionary representation of the object"""
        result = {Subscription.SUBCRIBED_KEY: self.subscribed}
        if self.time is not None:
            result[Subscription.TIME_KEY] = self.time.strftime("%H:%M")
        if self.relative_time is not None:
            result[Subscription.RELATIVE_TIME_KEY] = self.relative_time.value
        return result

    def is_subscribed(self) -> bool:
        """Returns whereh the subscription is in place or not"""
        return False if self.subscribed is None else self.subscribed

    def subscribed(self) -> None:
        """Activates the subscription"""
        self.subscribed = True

    def unsubscribed(self) -> None:
        """Deactivates the subscription"""
        self.subscribed = False

    def should_send_reminder(self,
                             gameDate: datetime,
                             comparison: datetime = datetime.now()) -> bool:
        """Should send a reminder based upon the given game date.

        Args:
            gameDate (datetime): the date of the game for the reminder
            comparison (datetime, optional): The comparison date.
                                             Defaults to datetime.now().

        Returns:
            bool: True if should send reminder otherwise False
        """
        local_time = None
        relative_time = None
        if self.time is not None:
            local_time = datetime.combine(gameDate.date(), self.time)
        if self.relative_time is not None:
            if self.relative_time is RelativeTimeEnum.MORNING:
                relative_time = datetime.combine(gameDate.date(), time(8, 0))
            elif self.relative_time is RelativeTimeEnum.HOUR_BEFORE:
                relative_time = gameDate - timedelta(hours=1)
            elif self.relative_time is RelativeTimeEnum.NIGHT_BEFORE:
                day_before = (gameDate - timedelta(days=1))
                relative_time = datetime.combine(day_before.date(),
                                                 time(20, 0))
        # check if right now is in the subscription reminder time frame
        c1 = difference_in_minutes_between_dates(
                local_time, comparison) < SUBSCRIPTION_TIME_RANGE
        c2 = difference_in_minutes_between_dates(
                relative_time, comparison) < SUBSCRIPTION_TIME_RANGE
        LOGGER.debug(f"Subscription {c1} and {c2}")
        LOGGER.debug(f"relative time:{relative_time}, time: {local_time}")
        return c1 or c2

    def set_relative_time(self, relative_enum: RelativeTimeEnum) -> None:
        """Sets the relative time of the subscription.

        Args:
            relative_enum (RelativeTimeEnum): type of relative subscription

        Raises:
            InvalidSubscription:given an invalid subscription
        """
        if (relative_enum is RelativeTimeEnum.MORNING or
                relative_enum is RelativeTimeEnum.HOUR_BEFORE or
                relative_enum is RelativeTimeEnum.NIGHT_BEFORE):
            self.relative_time = relative_enum
            return
        message = "Unrecongized relative time: {}".format(relative_enum)
        LOGGER.error(message)
        raise InvalidSubscription(message)

    def set_time(self, some_time: datetime) -> None:
        """Set the time of the subscription

        Args:
            some_time (datetime): the time of the subscription

        Raises:
            InvalidSubscription: an invalid subscription
        """
        if (isinstance(some_time, time) or
                isinstance(some_time, datetime)):
            self.time = some_time
            return
        message = "Given time of the wrong type: {}".format(some_time)
        LOGGER.error(message)
        raise InvalidSubscription(message)


class Subscriptions():
    """
    A model for what teams a player is subscribed to and whether subscribed
    to league updates as well
    """

    def __init__(self):
        """Constructor"""
        self.league = True
        self.team_lookup = {}

    @staticmethod
    def from_dictionary(dictionary: dict) -> 'Subscriptions':
        """Returns subscriptions parsed from a dictionary"""
        subscriptions = Subscriptions()
        team_lookup = {}
        league = True
        for key, value in dictionary.items():
            if "league" in key.lower():
                league = value in TRUTHINESS
            else:
                if isinstance(value, Subscription):
                    value = value.to_dictionary()
                team_lookup[key] = Subscription.from_dictionary(value)
        subscriptions.league = league
        subscriptions.team_lookup = team_lookup
        return subscriptions

    def to_dictionary(self) -> dict:
        """Returns the dictionary representation of the subscription"""
        result = {"league": self.league}
        for team_id, subscribed in self.team_lookup.items():

            result[str(team_id)] = subscribed.to_dictionary()
        return result

    def is_subscribed_to_league(self) -> bool:
        """Returns whether subscribed to the league"""
        return self.league

    def subscribe_to_league(self) -> None:
        """Subcribed to the league"""
        self.league = True

    def unsubscribe_from_league(self) -> None:
        """Unsubscribe from the league"""
        self.league = False

    def is_subscribed_to_team(self, team_id: int) -> bool:
        """Is the player subscribed to the given team.

        Args:
            team_id (int): the id of the team

        Returns:
            bool: True if subscribed otherwise False
        """
        if str(team_id) in self.team_lookup.keys():
            return self.team_lookup[str(team_id)].is_subscribed()
        else:
            return False

    def get_subscription_for_team(self, team_id: int) -> Subscription:
        """Get the subscription for the given team.

        Args:
            team_id (int): id of the team

        Returns:
            Subscription: the subscription if they are subscribed
                          otherwise None
        """
        if str(team_id) in self.team_lookup.keys():
            return self.team_lookup[str(team_id)]
        return None

    def subscribe_to_team(self, team_id: int,
                          subscription: Subscription = None) -> None:
        """Subscribe to the given team.

        Args:
            team_id (int): the id of the team
            subscription (Subscription, optional): the subscription.
                                                   Defaults to None.
        """
        if subscription is None:
            subscription = Subscription()
        self.team_lookup[str(team_id)] = subscription

    def unsubscribe_from_team(self, team_id: int) -> None:
        """Unsubscribe from the given team.

        Args:
            team_id (int): id of the team to unsubscribed from
        """
        self.team_lookup.pop(str(team_id), None)
