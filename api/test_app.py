'''
Created on May 6, 2017

@author: Dallas
'''
import unittest
from api import get_postback_payload, get_payload, format_game,\
                random_fun_comment, random_emoji, random_intro,\
                random_sass, random_compliment, base_options,\
                display_homeruns, display_ss, display_upcoming_games,\
                display_league_leaders, display_fun, display_summary,\
                determine_player, check_email, help_user, parse_number,\
                update_payload, figure_out, mongo
from pprint import PrettyPrinter
from api.variables import *


class userMock():
    def __init__(self):
        self.users = []

    def find_one(self, search):
        key = None
        value = None
        for k, v in search.items():
            key = k
            value = v
        found = None
        for user in self.users:
            if user[key] == value:
                found = user
        return found

    def insert_one(self, user):
        self.users.append(user)

    def save(self, user):
        pos = -1
        for i, check in enumerate(self.users):
            if check["fid"] == user["fid"]:
                pos = i
        if pos != -1:
            self.users.pop(pos)
            self.users.append(user)


class dbMock():
    def __init__(self):
        self.users = userMock()


class mongoMock():
    def __init__(self):
        self.db = dbMock()


class TestMock(unittest.TestCase):

    def setUp(self):
        global mongo
        mongo = mongoMock()
        self.mongo = mongo

    def tearDown(self):
        pass

    def testInsertOne(self):
        self.mongo.db.users.insert_one({"fid": 1})
        self.assertEqual(self.mongo.db.users.users, [{"fid": 1}])

    def testFindOne(self):
        self.mongo.db.users.users = [{"fid": 1}, {"fid": 2}, {"fid": 3}]
        for i in range(1, 4):
            result = self.mongo.db.users.find_one({"fid": i})
            self.assertEqual(result, {"fid": i})
        result = self.mongo.db.users.find_one({"fid": -1})
        self.assertEqual(result, None)

    def testSave(self):
        self.mongo.db.users.users = [{"fid": 1}, {"fid": 2}, {"fid": 3}]
        self.mongo.db.users.save({"fid": 1, "game": 1})
        self.mongo.db.users.save({"fid": 2, "game": 2})
        self.mongo.db.users.save({"fid": 3, "game": 3})
        self.assertEqual(self.mongo.db.users.users,
                         [{"fid": 1, "game": 1},
                          {"fid": 2, "game": 2},
                          {"fid": 3, "game": 3}])


def mockCallback(message, sender_id, buttons=[], quick_replies=[]):
    global MESSAGE, BUTTONS, QUICK_REPLIES
    MESSAGE = message
    BUTTONS = buttons
    QUICK_REPLIES = quick_replies
    if SHOW_RESULTS:
        pp = PrettyPrinter(indent=1)
        pp.pprint(message)
        pp.pprint(buttons)
        pp.pprint(quick_replies)


BUTTONS = None
QUICK_REPLIES = None
MESSAGE = None
SHOW_RESULTS = True


class TestFunctions(unittest.TestCase):
    def setUp(self):
        global mongo
        mongo = mongoMock()
        self.mongo = mongo
        self.pp = PrettyPrinter(indent=4)
        self.user = {'captain': 1,
                     'teamroster': {'2': {'gender': 'm',
                                          'player_name': 'Dallas Fraser',
                                          'player_id': 2},
                                    '3': {'gender': 'f',
                                          'player_name': 'Dream Girl',
                                          'player_id': 3},
                                    '6': {'gender': 'm',
                                          'player_name': 'Jack Romano',
                                          'player_id': 6}},
                     'game': {'game_id': 1,
                              'hr': [],
                              'ss': [],
                              'score': 0},
                     'pid': 1,
                     'fid': '1317620808322887',
                     'name': 'Drey Fraser',
                     'batter': -1,
                     'state': BASE}
        self.message = None

    def tearDown(self):
        pass

    def show_result(self):
        global SHOW_RESULTS
        SHOW_RESULTS = True

    def testRandomFunctions(self):
        self.assertEqual(random_emoji() in EMOJI, True)
        self.assertEqual(random_fun_comment() in FUN_COMMENT, True)
        self.assertEqual(random_intro() in INTROS, True)
        self.assertEqual(random_sass() in SASSY_COMMENT, True)
        self.assertEqual(random_compliment() in COMPLIMENT, True)

    def testGetPostbackPayload(self):
        message = {'recipient': {'id': '204216316752639'},
                   'sender': {'id': '1317620808322887'},
                   'timestamp': 1494094553953,
                   'postback': {'payload': '8'}}
        pay = get_postback_payload(message)
        self.assertEqual(pay, "8")

    def testGetPayload(self):
        message = {'message': {'mid': 'mid.$cAADjTSykfvliEEJ371b3v03dQxf9',
                               'seq': 1336,
                               'quick_reply': {'payload': '1'},
                               'text': '2017-05-03: CaliBurg...'},
                   'recipient': {'id': '204216316752639'},
                   'sender': {'id': '1317620808322887'},
                   'timestamp': 1494094786543}
        pay = get_payload(message)
        self.assertEqual(pay, "1")
        message = {'message': {'mid': 'mid.$cAADjTSykfvliEEPcolb3v6cAvl1o',
                               'seq': 1340,
                               'text': 'hey'},
                   'recipient': {'id': '204216316752639'},
                   'sender': {'id': '1317620808322887'},
                   'timestamp': 1494094877858}
        pay = get_payload(message)
        self.assertEqual(pay, None)

    def testFormatGame(self):
        game = {'league_id': 1,
                'home_team_id': 1,
                'home_team': 'CaliBurger Test',
                'status': '',
                'game_id': 1,
                'time': '10:00',
                'away_team': 'CaliBurger Test2',
                'date': '2017-05-03',
                'away_team_id': 2,
                'field': 'WP1'}
        expect = "2017-05-03: CaliBurger Test vs CaliBurger Test2 @ 10:00 on WP1"
        self.assertEqual(format_game(game), expect)

    def testBaseOptions(self):
        base_options(self.user, "", mockCallback)
        expect_buttons = [{'payload': 'Upcoming events',
                           'title': 'Upcoming Games',
                           'type': 'postback'},
                          {'payload': 'League leaders',
                           'title': 'League Leaders',
                           'type': 'postback'},
                          {'payload': 'Events',
                           'title': 'Events',
                           'type': 'postback'},
                          {'payload': 'Fun meter',
                           'title': 'Fun Meter',
                           'type': 'postback'},
                          {'payload': 'Asked for captain to select game',
                           'title': 'Submit Score',
                           'type': 'postback'}]
        expect_quick = []
        self.assertEqual(MESSAGE in INTROS, True)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)
        # now test for a non captain
        self.user['captain'] = -1
        expect_buttons.pop()
        base_options(self.user, "", mockCallback)
        self.assertEqual(MESSAGE in INTROS, True)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)

    def testDisplayHomeruns(self):
        display_homeruns(self.user, "", mockCallback)
        expect_buttons = [{'payload': 'Upcoming events',
                           'title': 'Upcoming Games',
                           'type': 'postback'},
                          {'payload': 'League leaders',
                           'title': 'League Leaders',
                           'type': 'postback'},
                          {'payload': 'Events',
                           'title': 'Events',
                           'type': 'postback'},
                          {'payload': 'Fun meter',
                           'title': 'Fun Meter',
                           'type': 'postback'},
                          {'payload': 'Asked for captain to select game',
                           'title': 'Submit Score',
                           'type': 'postback'}]
        expect_quick = []
        self.assertEqual(MESSAGE, "'Pick a batter \n who hit a hr:'")
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
