'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Test subscription and its functionality
'''
from api.players.subscription import Subscription, Subscriptions,\
    RelativeTimeEnum
from api.errors import SubscriptionException
import unittest
import datetime


class TestSubscription(unittest.TestCase):

    def testEmptyConstructor(self):
        subscription = Subscription()
        self.assertTrue(subscription.is_subscribed())
        dictionary = subscription.to_dictionary()
        self.assertEqual(dictionary[Subscription.SUBCRIBED_KEY], True)
        self.assertEqual(dictionary[Subscription.RELATIVE_TIME_KEY],
                         RelativeTimeEnum.MORNING)

    def testToConversion(self):
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
                         relative)
        self.assertEqual(dictionary[Subscription.TIME_KEY],
                         "0" + given_time)

    def testShouldSendReminderTime(self):
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
        self.assertFalse(subscription.should_send_reminder(tomorrow))

        # if comparison is night before then we should send a reminder
        value = subscription.should_send_reminder(current,
                                                  comparison=night_before)
        self.assertTrue(value)

    def testSetRelativeTime(self):
        subscription = Subscription()
        try:
            subscription.set_relative_time("")
            self.assertFalse(True, "Expecting an exception")
        except SubscriptionException:
            pass
        subscription.set_relative_time(RelativeTimeEnum.MORNING)

    def testSetTime(self):
        subscription = Subscription()
        try:
            subscription.set_time("")
            self.assertFalse(True, "Expecting an exception")
        except SubscriptionException:
            pass
        subscription.set_time(datetime.time(0, 0))
        subscription.set_time(datetime.datetime.now())


class TestSubscriptions(unittest.TestCase):
    pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
