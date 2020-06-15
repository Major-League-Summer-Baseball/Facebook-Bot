'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Test message package
'''
from api.message import Option, Message
from api.message.format import StringFormatter, EventFormatter
from api.errors import OptionException
import unittest


class TestMessageAndOption(unittest.TestCase):

    def testMessage(self):
        message = Message("sender_id", message="message", payload="payload")
        self.assertEqual(message.get_sender_id(), "sender_id")
        self.assertEqual(message.get_message(), "message")
        self.assertEqual(message.get_payload(), "payload")

    def testOption(self):
        try:
            option = Option("title", ["data"])
            self.assertTrue(False, "Expecting OptionException")
        except OptionException:
            pass

        # data formatter
        option = Option("title", StringFormatter("data"))
        self.assertEqual(str(option.get_data()), "data")
        self.assertEqual(option.get_title(), "title")

        # event formatter
        event_formatter = EventFormatter({"event": "beerfest",
                                          "date": "June 7th"})
        option = Option("title", event_formatter)
        self.assertEqual(str(option.get_data()), "beerfest - June 7th")
        self.assertEqual(option.get_title(), "title")

        # no formatter but using string
        option = Option("title", "data")
        self.assertEqual(str(option.get_data()), "data")
        self.assertEqual(option.get_title(), "title")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
