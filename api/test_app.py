'''
Created on May 6, 2017

@author: Dallas
'''
import unittest
from datetime import datetime
import requests
from api import get_postback_payload, get_payload, format_game,\
                random_fun_comment, random_emoji, random_intro,\
                random_sass, random_compliment, base_options,\
                display_homeruns, display_ss, display_upcoming_games,\
                display_league_leaders, display_fun, display_summary,\
                determine_player, check_email, help_user, parse_number,\
                update_payload, figure_out, mongo, change_mongo
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
        print(found)
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
                              'hr': [2, 2, 6],
                              'ss': [3],
                              'score': 4},
                     'pid': 2,
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
                           'title': UPCOMING_TITLE,
                           'type': 'postback'},
                          {'payload': 'League leaders',
                           'title': LEAGUE_LEADERS_TITLE,
                           'type': 'postback'},
                          {'payload': 'Events',
                           'title': EVENTS_TITLE,
                           'type': 'postback'},
                          {'payload': 'Fun meter',
                           'title': FUN_TITLE,
                           'type': 'postback'},
                          {'payload': 'Asked for captain to select game',
                           'title': SUBMIT_SCORE_TITLE,
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
        # no jack and dallas since they hit hr
        display_homeruns(self.user, "", mockCallback)
        expect_buttons = [{'payload': 3,
                           'title': 'Dream Girl',
                           'type': 'postback'},
                          {'payload': 'done',
                           'title': DONE_COMMENT,
                           'type': 'postback'},
                          {'payload': 'cancel',
                           'title': CANCEL_COMMENT,
                           'type': 'postback'}]
        expect_quick = []
        self.assertEqual(MESSAGE, PICKBATTER_COMMENT.format("hr"))
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)

    def testDisplaySS(self):
        # no dream girl since she has been recorded
        display_ss(self.user, "", mockCallback)
        expect_buttons = [{'payload': 'done',
                           'title': DONE_COMMENT,
                           'type': 'postback'},
                          {'payload': 'cancel',
                           'title': CANCEL_COMMENT,
                           'type': 'postback'}]
        expect_quick = []
        self.assertEqual(MESSAGE, PICKBATTER_COMMENT.format("ss"))
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)
        self.user['game']['ss'] = []
        display_ss(self.user, "", mockCallback)
        expect_buttons = [{'payload': 3,
                           'title': 'Dream Girl',
                           'type': 'postback'},
                          {'payload': 'done',
                           'title': DONE_COMMENT,
                           'type': 'postback'},
                          {'payload': 'cancel',
                           'title': CANCEL_COMMENT,
                           'type': 'postback'}]
        expect_quick = []
        self.assertEqual(MESSAGE, PICKBATTER_COMMENT.format("ss"))
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)

    def testDisplayUpcomingGames(self):
        # no games
        display_upcoming_games(self.user, "", mockCallback)
        expect_buttons = []
        expect_quick = []
        self.assertEqual(MESSAGE, NOGAMES_COMMENT)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)

    def testDisplayLeagueLeaders(self):
        # multiple messages should be displayed
        display_league_leaders(self.user, "", mockCallback)
        expect_buttons = []
        expect_quick = []
        m = 'SS Leaders:\nDream Girl (CaliBurger Test): 1'
        self.assertEqual('SS Leaders:\nDream Girl (CaliBurger Test): 1',
                         MESSAGE)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)

    def testDisplayFun(self):
        # dont check the message since it is complex (unicode)
        display_fun(self.user, "", mockCallback)
        expect_buttons = []
        expect_quick = []
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)

    def testDisplaySummary(self):
        display_summary(self.user, "", mockCallback)
        expect_buttons = []
        expect_quick = [{'content_type': 'text',
                         'image_url': 'http://www.clker.com/cliparts/Z/n/g/w/C/y/green-dot-md.png',
                         'payload': 'submit',
                         'title': SUBMIT_TITLE},
                        {'content_type': 'text',
                         'image_url': 'http://www.clker.com/cliparts/T/G/b/7/r/A/red-dot-md.png',
                         'payload': 'cancel',
                         'title': CANCEL_COMMENT}]
        message = 'Score: 4\nHR:\nDallas Fraser - 2\nJack Romano - 1\nSS:\nDream Girl - 1'
        self.assertEqual(message, MESSAGE)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)

    def testParseNumber(self):
        self.assertEqual(parse_number(1), 1)
        self.assertEqual(parse_number("1"), 1)
        self.assertEqual(parse_number("ajsbasjkd"), -1)
        self.assertEqual(parse_number("Score was 1"), 1)
        self.assertEqual(parse_number("Score was 1 to 2"), 1)


class TestDisplayUpcomingGames(unittest.TestCase):
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
                              'hr': [2, 2, 6],
                              'ss': [3],
                              'score': 4},
                     'pid': 2,
                     'fid': '1317620808322887',
                     'name': 'Drey Fraser',
                     'batter': -1,
                     'state': BASE}
        self.message = None
        self.game_id = None
        # add a random games
        self.d = datetime.today().strftime('%Y-%m-%d')
        self.params = {"home_team_id": 1,
                       "away_team_id": 2,
                       "league_id": 1,
                       "date": self.d,
                       "time": "23:59",
                       "status": "",
                       "field": "WP1"
                       }
        r = requests.post(BASEURL + "api/games",
                          headers=HEADERS, data=self.params)
        if (r.status_code != 201):
            # fuck what should i do
            print("Couldnt add game")
            pass
        self.game_id = r .json()

    def tearDown(self):
        if self.game_id is not None:
            r = requests.delete(BASEURL +
                                "api/games/{:d}".format(self.game_id),
                                headers=HEADERS)
        if (r.status_code != 200):
            # fuck what should i do
            print(r.text)
            print("Couldnt delete game")

    def testDisplayUpcomingGames(self):
        display_upcoming_games(self.user, "", mockCallback)
        expect_buttons = []
        expect_quick = []
        m = self.d + ': CaliBurger Test vs CaliBurger Test2 @ 23:59 on WP1'
        self.assertEqual(MESSAGE, m)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)


class TestDetermineCheckEmail(unittest.TestCase):
    def setUp(self):
        m = mongoMock()
        change_mongo(m)
        global mongo
        mongo = m
        self.mongo = mongo
        self.pp = PrettyPrinter(indent=4)
        self.user = {'captain': -1,
                     'teamroster': {},
                     'game': {},
                     'pid': -1,
                     'fid': '1317620808322887',
                     'name': 'Drey Fraser',
                     'batter': -1,
                     'state': PID}
        self.message = None

    def tearDown(self):
        pass

    def testDeterminePlayer(self):
        # need their email
        determine_player(self.user, "", mockCallback)
        expect_buttons = []
        expect_quick = []
        self.assertEqual(MESSAGE, ASK_EMAIL_COMMENT)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)
        self.assertEqual(self.user['state'], EMAIL)
        # a known player
        self.user['name'] = "Dallas Fraser"
        determine_player(self.user, "", mockCallback)
        expect_buttons = [{'payload': 'Upcoming events',
                           'title': UPCOMING_TITLE,
                           'type': 'postback'},
                          {'payload': 'League leaders',
                           'title': LEAGUE_LEADERS_TITLE,
                           'type': 'postback'},
                          {'payload': 'Events',
                           'title': EVENTS_TITLE,
                           'type': 'postback'},
                          {'payload': 'Fun meter',
                           'title': FUN_TITLE,
                           'type': 'postback'},
                          {'payload': 'Asked for captain to select game',
                           'title': SUBMIT_SCORE_TITLE,
                           'type': 'postback'}]
        expect_quick = []
        self.assertEqual(MESSAGE in INTROS, True)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)
        self.assertEqual(self.user['state'], BASE)
        # player who's identity is known
        self.user['pid'] = 2
        self.mongo.db.users.insert_one(self.user)
        determine_player(self.user, "", mockCallback)
        expect_buttons = []
        expect_quick = []
        self.assertEqual(MESSAGE, IDENTITY_STOLEN_COMMENT)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)
        self.assertEqual(self.user['state'], IGNORE)

    def testCheckEmail(self):
        # need their email
        check_email(self.user, "NOTEMAIL", "", mockCallback)
        expect_buttons = []
        expect_quick = []
        self.assertEqual(MESSAGE, NO_EMAIL_GIVEN_COMMENT)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)
        self.assertEqual(self.user['state'], PID)
        # cant find email
        check_email(self.user, "not@found", "", mockCallback)
        expect_buttons = []
        expect_quick = []
        self.assertEqual(MESSAGE, NOT_FOUND_COMMENT)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)
        self.assertEqual(self.user['state'], PID)
        # good email
        check_email(self.user, "fras2560@mylaurier.ca", "", mockCallback)
        expect_buttons = [{'payload': 'Upcoming events',
                           'title': UPCOMING_TITLE,
                           'type': 'postback'},
                          {'payload': 'League leaders',
                           'title': LEAGUE_LEADERS_TITLE,
                           'type': 'postback'},
                          {'payload': 'Events',
                           'title': EVENTS_TITLE,
                           'type': 'postback'},
                          {'payload': 'Fun meter',
                           'title': FUN_TITLE,
                           'type': 'postback'},
                          {'payload': 'Asked for captain to select game',
                           'title': SUBMIT_SCORE_TITLE,
                           'type': 'postback'}]
        expect_quick = []
        self.assertEqual(MESSAGE in INTROS, True)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)
        self.assertEqual(self.user['state'], BASE)
        # email has been taken
        self.mongo.db.users.insert_one(self.user)
        check_email(self.user, "fras2560@mylaurier.ca", "", mockCallback)
        expect_buttons = []
        expect_quick = []
        self.assertEqual(MESSAGE, IDENTITY_STOLEN_COMMENT)
        self.assertEqual(BUTTONS, expect_buttons)
        self.assertEqual(QUICK_REPLIES, expect_quick)
        self.assertEqual(self.user['state'], IGNORE)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
