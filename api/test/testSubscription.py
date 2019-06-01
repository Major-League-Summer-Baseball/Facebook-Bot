'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Test subscription and its functionality
'''
from api.players.subscription import Subscription, Subscriptions,\
    RelativeTimeEnum
from api.errors import InvalidSubscription
import unittest
import datetime


class TestSubscription(unittest.TestCase):

    def testEmptyConstructor(self):
        """Test the default subscription"""
        subscription = Subscription()
        self.assertTrue(subscription.is_subscribed())
        dictionary = subscription.to_dictionary()
        self.assertEqual(dictionary[Subscription.SUBCRIBED_KEY], True)
        self.assertEqual(dictionary[Subscription.RELATIVE_TIME_KEY],
                         RelativeTimeEnum.MORNING.value)

    def testToConversion(self):
        """Test that able to create object from dictionary and back"""
        given_time = "8:00"
        relative = RelativeTimeEnum.MORNING
        dictionary_constructor = {Subscription.SUBCRIBED_KEY: False,
                                  Subscription.RELATIVE_TIME_KEY: relative,
                                  Subscription.TIME_KEY: given_time}
        subscription = Subscription(dictionary=dictionary_constructor)
        self.assertFalse(subscription.is_subscribed())
        dictionary = subscription.to_dictionary()
        self.assertEqual(dictionary[Subscription.SUBCRIBED_KEY], False)
        self.assertEqual(dictionary[Subscription.RELATIVE_TIME_KEY],
                         relative.value)
        self.assertEqual(dictionary[Subscription.TIME_KEY],
                         "0" + given_time)

    def testShouldSendReminderTime(self):
        """Test send reminder when the time is set"""
        current = datetime.datetime.now()
        yesterday = current - datetime.timedelta(days=1)
        tomorrow = current + datetime.timedelta(days=1)
        today_at_eight = datetime.datetime.combine(
            current.date(), datetime.time(8, 0))

        #
        subscription = Subscription({Subscription.SUBCRIBED_KEY: True,
                                     Subscription.TIME_KEY: "8:00"})
        # yesterday and tomorrow are not within range
        self.assertFalse(subscription.should_send_reminder(yesterday))
        self.assertFalse(subscription.should_send_reminder(tomorrow))

        # if comparison is today at eight then we should send a reminder
        value = subscription.should_send_reminder(current,
                                                  comparison=today_at_eight)
        self.assertTrue(value)

    def testShouldSendReminderRelativeTimeMorning(self):
        """Test send reminder when the relative time is morning"""
        current = datetime.datetime.now()
        yesterday = current - datetime.timedelta(days=1)
        tomorrow = current + datetime.timedelta(days=1)
        today_at_eight = datetime.datetime.combine(
            current.date(), datetime.time(8, 0))
        relative = RelativeTimeEnum.MORNING
        #
        subscription = Subscription({Subscription.SUBCRIBED_KEY: True,
                                     Subscription.RELATIVE_TIME_KEY: relative})
        # yesterday and tomorrow are not within range
        self.assertFalse(subscription.should_send_reminder(yesterday))
        self.assertFalse(subscription.should_send_reminder(tomorrow))

        # if comparison is today at eight then we should send a reminder
        value = subscription.should_send_reminder(current,
                                                  comparison=today_at_eight)
        self.assertTrue(value)

    def testShouldSendReminderRelativeTimeHourBefore(self):
        """Test send reminder when the relative time is hour before game"""
        current = datetime.datetime.now()
        yesterday = current - datetime.timedelta(days=1)
        tomorrow = current + datetime.timedelta(days=1)
        hour_ago = current - datetime.timedelta(hours=1)
        relative = RelativeTimeEnum.HOUR_BEFORE
        #
        subscription = Subscription({Subscription.SUBCRIBED_KEY: True,
                                     Subscription.RELATIVE_TIME_KEY: relative})
        # yesterday and tomorrow are not within range
        self.assertFalse(subscription.should_send_reminder(yesterday))
        self.assertFalse(subscription.should_send_reminder(tomorrow))

        # if comparison is hour before game then we should send a reminder
        value = subscription.should_send_reminder(current,
                                                  comparison=hour_ago)
        self.assertTrue(value)

    def testShouldSendReminderRelativeTimeNightBefore(self):
        """Test send reminder when the relative time is night before game"""
        current = datetime.datetime.now()
        yesterday = current - datetime.timedelta(days=1)
        tomorrow = current + datetime.timedelta(days=1)
        night_before = datetime.datetime.combine(
            yesterday.date(), datetime.time(20, 0))
        relative = RelativeTimeEnum.NIGHT_BEFORE
        #
        subscription = Subscription({Subscription.SUBCRIBED_KEY: True,
                                     Subscription.RELATIVE_TIME_KEY: relative})
        # current and tomorrow are not within range
        self.assertFalse(subscription.should_send_reminder(current))
        print(tomorrow, current)
        self.assertFalse(subscription.should_send_reminder(tomorrow))

        # if comparison is night before then we should send a reminder
        value = subscription.should_send_reminder(current,
                                                  comparison=night_before)
        self.assertTrue(value)

    def testSetRelativeTime(self):
        """Test the setter of relative time takes only a relative time"""
        subscription = Subscription()
        try:
            subscription.set_relative_time("")
            self.assertFalse(True, "Expecting an exception")
        except InvalidSubscription:
            pass
        subscription.set_relative_time(RelativeTimeEnum.MORNING)

    def testSetTime(self):
        """Test the setter of time takes only datetime or time"""
        subscription = Subscription()
        try:
            subscription.set_time("")
            self.assertFalse(True, "Expecting an exception")
        except InvalidSubscription:
            pass
        subscription.set_time(datetime.time(0, 0))
        subscription.set_time(datetime.datetime.now())


class TestSubscriptions(unittest.TestCase):

    def testEmptyConstructor(self):
        """Test the default Subscriptions"""
        subscriptions = Subscriptions()
        self.assertTrue(subscriptions.is_subscribed_to_league())
        self.assertFalse(subscriptions.is_subscribed_to_team(-1))

    def testConversion(self):
        """Test able to construct from dictionary and export"""
        dictionary = {"league": False, "1": Subscription().to_dictionary()}
        subscriptions = Subscriptions(dictionary=dictionary)
        self.assertFalse(subscriptions.is_subscribed_to_league())
        self.assertTrue(subscriptions.is_subscribed_to_team(1))
        subscriptions = Subscriptions(dictionary=subscriptions.to_dictionary())
        self.assertFalse(subscriptions.is_subscribed_to_league())
        self.assertTrue(subscriptions.is_subscribed_to_team(1))

    def testConversionUsingObject(self):
        """Test able conversion where subscription is object not dict"""
        dictionary = {"league": False, "1": Subscription()}
        subscriptions = Subscriptions(dictionary=dictionary)
        self.assertFalse(subscriptions.is_subscribed_to_league())
        self.assertTrue(subscriptions.is_subscribed_to_team(1))
        subscriptions = Subscriptions(dictionary=subscriptions.to_dictionary())
        self.assertFalse(subscriptions.is_subscribed_to_league())
        self.assertTrue(subscriptions.is_subscribed_to_team(1))

    def testSubscribeToTeam(self):
        """Test able to subscribe to team"""
        subscriptions = Subscriptions()
        subscriptions.subscribe_to_team(1)
        self.assertTrue(subscriptions.is_subscribed_to_team(1))
        self.assertTrue(subscriptions.is_subscribed_to_team("1"))

        # string or number should work
        subscriptions.subscribe_to_team("2")
        self.assertTrue(subscriptions.is_subscribed_to_team(2))
        self.assertTrue(subscriptions.is_subscribed_to_team("2"))

    def testUnsubscribeToTeam(self):
        """Test able to unsubscribe to team"""
        subscribed_teams = {"1": Subscription().to_dictionary(),
                            "2": Subscription().to_dictionary()}
        subscriptions = Subscriptions(dictionary=subscribed_teams)
        subscriptions.unsubscribe_from_team(1)
        self.assertFalse(subscriptions.is_subscribed_to_team(1))
        self.assertFalse(subscriptions.is_subscribed_to_team("1"))

        # string or number should work
        subscriptions.unsubscribe_from_team("2")
        self.assertFalse(subscriptions.is_subscribed_to_team(2))
        self.assertFalse(subscriptions.is_subscribed_to_team("2"))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
