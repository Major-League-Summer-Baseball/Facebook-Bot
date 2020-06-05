'''
@author: Dallas Fraser
@author: 2020-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Test parser methods
'''
from api.test.testActions import TestActionBase
from datetime import date, timedelta, datetime
from api.parsers import get_tokens, levenshtein_ratio, parse_number,\
    parse_out_date, parse_out_email, match_with_team, match_game,\
    match_with_player, parse_out_player
import unittest


class TestParserFunctions(TestActionBase):
    def testGetTokens(self):
        self.assertEqual(get_tokens("brad 1"), ["brad", "1"])
        self.assertEqual(get_tokens("brad,1"), ["brad", "1"])
        self.assertEqual(get_tokens("brad-1"), ["brad", "1"])

    def testLevenshteinRatio(self):
        self.assertAlmostEqual(levenshtein_ratio("brad", "sara"), 0.5,
                               delta=5)
        self.assertAlmostEqual(levenshtein_ratio("smyth", "smith"), 0.8,
                               delta=5)
        self.assertAlmostEqual(levenshtein_ratio("christopher", "chris"), 0.62,
                               delta=5)
        self.assertAlmostEqual(levenshtein_ratio("pabst", "pabst?"),
                               0.90, delta=5)

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

    def testParseOutDate(self):
        self.assertEqual(parse_out_date("the game was six days ago"),
                         date.today() - timedelta(days=6))
        self.assertEqual(parse_out_date("the game was 6 days ago"),
                         date.today() - timedelta(days=6))
        self.assertEqual(parse_out_date("the game was yesterday"),
                         date.today() - timedelta(days=1))
        self.assertEqual(parse_out_date("Today"),
                         date.today())
        self.assertEqual(parse_out_date("the game is tomorrow"),
                         date.today() + timedelta(days=1))
        self.assertEqual(parse_out_date("the game is 5 days from today"),
                         date.today() + timedelta(days=5))
        self.assertEqual(parse_out_date("the game is 2020-10-01"),
                         datetime.strptime("2020-10-01", "%Y-%m-%d").date())
        self.assertIsNone(parse_out_date("there is no date here"))

    def testMatchTeam(self):
        self.assertAlmostEqual(match_with_team("abe", "Abe Erb Apple"), 1.0,
                               delta=3)
        self.assertAlmostEqual(match_with_team("Erb", "Abe Erb Apple"), 1.0,
                               delta=3)
        self.assertAlmostEqual(match_with_team("Apple", "Abe Erb Apple"), 1.0,
                               delta=3)
        self.assertAlmostEqual(match_with_team("Chainsaw", "Chainsaw Chives"),
                               1.0, delta=3)
        self.assertAlmostEqual(match_with_team("Becky",
                                               "Becky's Apartment Bubblegum"),
                               1.0, delta=3)
        self.assertAlmostEqual(match_with_team("Beckys",
                                               "Becky's Apartment Bubblegum"),
                               1.0, delta=3)
        self.assertAlmostEqual(match_with_team("dr", "Dr Mcgillicuddy's Mist"),
                               1, delta=3)

    def testMatchGameRandomData(self):
        # some various dates that will be used
        today = datetime.strftime(date.today(), "%Y-%m-%d")
        tomorrow = datetime.strftime(date.today() + timedelta(days=1),
                                     "%Y-%m-%d")
        last_week = datetime.strftime(date.today() - timedelta(days=7),
                                      "%Y-%m-%d")

        # no match returns None
        self.assertIsNone(match_game("today", []))

        teams = [self.random_team(),
                 self.random_team(),
                 self.random_team(),
                 self.random_team()]
        games = [self.random_game(teams[0], teams[1]),
                 self.random_game(teams[2], teams[3]),
                 self.random_game(teams[1], teams[3])]

        # match a game based upon date
        games[0]['date'] = tomorrow
        games[2]['date'] = today
        games[1]['date'] = last_week
        self.assertEqual(match_game("today", games), games[2])
        self.assertEqual(match_game(today, games), games[2])
        self.assertEqual(match_game("7 days ago", games), games[1])
        self.assertEqual(match_game(last_week, games), games[1])

        # match based upon some team name
        team_name = teams[0].get('team_name')
        self.assertEquals(match_game(f"against {team_name}", games), games[0])
        team_name = teams[2].get('team_name')
        self.assertEquals(match_game(f"against {team_name}", games), games[1])

    def testMatchGameRealData(self):
        # some various dates that will be used
        today = datetime.strftime(date.today(), "%Y-%m-%d")
        tomorrow = datetime.strftime(date.today() + timedelta(days=1),
                                     "%Y-%m-%d")
        last_week = datetime.strftime(date.today() - timedelta(days=7),
                                      "%Y-%m-%d")

        # create three teams
        sportzone = self.random_team()
        sportzone["team_name"] = "SportsZone Pink"
        sportzone["color"] = "Pink"
        kik = self.random_team()
        kik["team_name"] = "Kik Kryptonite"
        kik["color"] = "Kryptonite"
        pabst = self.random_team()
        pabst["team_name"] = "Pabst Blue"
        pabst["color"] = "Blue"
        rwb = self.random_team()
        rwb["team_name"] = "RWB Red"
        rwb["color"] = "Red"

        games = [self.random_game(kik, sportzone),
                 self.random_game(pabst, rwb),
                 self.random_game(sportzone, pabst)]

        # match a game based upon date
        games[0]['date'] = tomorrow
        games[2]['date'] = today
        games[1]['date'] = last_week
        self.assertEqual(match_game("the game was today", games), games[2])
        self.assertEqual(match_game(today, games), games[2])
        self.assertEqual(match_game("the game 7 days ago", games), games[1])
        self.assertEqual(match_game(last_week, games), games[1])

        # match based upon some team name
        self.assertEquals(match_game("kik", games), games[0])
        self.assertEquals(match_game("the game against kik", games), games[0])
        self.assertEquals(match_game("pabsts", games), games[1])
        self.assertEquals(match_game("I believe pabsts?", games), games[1])

    def testMatchWithPlayer(self):
        # a simple test
        test_player = self.random_player()
        test_player["player_name"] = "test player"
        players = [self.random_player(),
                   self.random_player(),
                   test_player,
                   self.random_player()]
        self.assertEquals(match_with_player("player", players)[1],
                          [test_player])

        # a case where need a tie breaker
        west_player = self.random_player()
        west_player["player_name"] = "west player"
        players.append(west_player)
        self.assertEquals(match_with_player("player", players)[1],
                          [test_player, west_player])
        self.assertEquals(match_with_player("t.player", players)[1],
                          [test_player])

        # able to match the whole name
        self.assertEquals(match_with_player("test player", players)[1],
                          [test_player])

    def testParseOutPlayer(self):
        # a simple test
        test_player = self.random_player()
        player_name = "test player"
        test_player["player_name"] = player_name
        players = [self.random_player(),
                   self.random_player(),
                   test_player,
                   self.random_player()]
        message = f"the player is {player_name}"
        self.assertEquals(parse_out_player(message, players), [test_player])

        # a case where need a tie breaker
        west_player = self.random_player()
        west_player["player_name"] = "west player"
        players.append(west_player)
        message = "the player"
        self.assertEquals(parse_out_player(message, players),
                          [test_player, west_player])
        self.assertEquals(parse_out_player("sorry i meant t.player", players),
                          [test_player])

        # able to match the whole name
        self.assertEquals(match_with_player("test player", players)[1],
                          [test_player])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
