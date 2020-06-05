'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Test helper functions
'''
from api.helper import difference_in_minutes_between_dates,\
    is_game_in_list_of_games
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

    def testIsGameInListOfGames(self):
        # cases where game id in list of games
        game_list = [{"game_id": 1}]
        self.assertTrue(is_game_in_list_of_games(1, game_list))

        game_list = [{"game_id": "1"}, {"game_id": 2}]
        self.assertTrue(is_game_in_list_of_games(1, game_list))

        game_list = [{"game_id": 2}, {"game_id": 1}]
        self.assertTrue(is_game_in_list_of_games("1", game_list))

        # cases where game id not in list of games
        game_list = [{"game_id": 1}]
        self.assertFalse(is_game_in_list_of_games(-1, game_list))

        game_list = [{"game_id": "1"}, {"game_id": 2}]
        self.assertFalse(is_game_in_list_of_games(-1, game_list))

        game_list = [{"game_id": 2}, {"game_id": 1}]
        self.assertFalse(is_game_in_list_of_games("-1", game_list))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
