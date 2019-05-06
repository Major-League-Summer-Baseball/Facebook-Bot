'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Test helper functions
'''
from api.helper import difference_in_minutes_between_dates, parse_number,\
    parse_out_email
import datetime
import sys
import unittest


class TestHelperFunctions(unittest.TestCase):

    def testDifferenceInMinutesBetweenDates(self):
        now = datetime.datetime.now()
        # any case with none should be infinite difference
        self.assertEqual(difference_in_minutes_between_dates(
            None, None), sys.maxsize)
        self.assertEqual(difference_in_minutes_between_dates(
            None, now), sys.maxsize)
        self.assertEqual(difference_in_minutes_between_dates(
            now, None), sys.maxsize)

        # should be no difference between one's self
        self.assertEqual(difference_in_minutes_between_dates(now, now), 0)
        past = now - datetime.timedelta(minutes=15)

        self.assertEqual(difference_in_minutes_between_dates(now, past), 15)
        self.assertEqual(difference_in_minutes_between_dates(past, now), 15)

    def testParseNumber(self):
        self.assertEqual(parse_number(-1), -1)
        self.assertEqual(parse_number(1), 1)
        self.assertEqual(parse_number("1"), 1)
        self.assertEqual(parse_number("brad 1"), 1)
        self.assertEqual(parse_number("1 brad"), 1)
        self.assertEqual(parse_number("1 2"), 1)

    def testParseOutEmail(self):
        # normal sentence
        test = "My email is dallas.fraser.waterloo@gmail.com"
        expected = "dallas.fraser.waterloo@gmail.com"
        self.assertEqual(parse_out_email(test), expected)

        # straight forward response
        test = "dallas.fraser.waterloo@gmail.com"
        expected = "dallas.fraser.waterloo@gmail.com"
        self.assertEqual(parse_out_email(test), expected)

        # no email found
        test = "My name is trevor"
        expected = None
        self.assertEqual(parse_out_email(test), expected)

        # no email found
        test = "Where you @"
        expected = None
        self.assertEqual(parse_out_email(test), expected)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
