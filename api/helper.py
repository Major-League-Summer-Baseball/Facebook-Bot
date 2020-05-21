'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds basic function that are helpful across packages
'''
from api.settings.message_strings import SASSY_COMMENT, FUN_COMMENT, EMOJI,\
    COMPLIMENT, INTROS
from json import loads as loader
from datetime import datetime
from random import randint
import sys


def parse_out_email(message_string):
    """Returns an email that is contained in the message
    Parameters:
        message_string: the message that may/may not contain email
    Returns:
        the email or None if one is not found
    """
    tokens = message_string.split(" ")
    for token in tokens:
        if "@" in token and token != "@":
            return token
    return None


def difference_in_minutes_between_dates(d1, d2):
    """Returns the absolute difference between the two datetime objects"""
    if d1 is None or d2 is None:
        # none is treated like infinity
        return sys.maxsize
    return abs((d1 - d2).total_seconds() / 60.0)


def convert_to_int(token):
    """Returns whether the given token is an integer or not"""
    try:
        return int(token)
    except ValueError:
        pass
    return None


def parse_number(text):
    """Returns the first number in the text"""
    if type(text) is str:
        tokens = text.split(" ")
        number = -1
        for token in tokens:
            try:
                number = int(token)
                break
            except ValueError:
                pass
    else:
        number = -1
        try:
            number = int(text)
        except ValueError:
            pass
    return number


def is_game_in_list_of_games(game_id, games):
    """Returns whether the given game id is in the list of games"""
    for game in games:
        if str(game_id) == str(game.get("game_id", "")):
            return True
    return False


def get_this_year():
    """Return the current year"""
    return datetime.now().year


def random_fun_comment():
    """Returns a random fun comment
    """
    return FUN_COMMENT[randint(0, len(FUN_COMMENT) - 1)]


def random_emoji():
    """Returns a random emoji
    """
    return EMOJI[randint(0, len(EMOJI) - 1)]


def random_intro():
    """Returns a random intro
    """
    return INTROS[randint(0, len(INTROS) - 1)]


def random_sass():
    """Returns a random sassy comment
    """
    return SASSY_COMMENT[randint(0, len(SASSY_COMMENT) - 1)]


def random_compliment():
    """Returns a random compliment
    """
    return COMPLIMENT[randint(0, len(COMPLIMENT) - 1)]


def loads(data):
    try:
        data = loader(data)
    except Exception:
        data = loader(data.decode('utf-8'))
    return data


def log(message):
    # simple wrapper for logging to stdout on heroku
    try:
        print(str(message))
        sys.stdout.flush()
    except Exception as e:
        print(str(e))
        pass
