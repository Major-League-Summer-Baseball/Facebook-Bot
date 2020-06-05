'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds basic function that are helpful across packages
'''
from typing import List
from api.settings.message_strings import SASSY_COMMENT, FUN_COMMENT, EMOJI,\
    COMPLIMENT, INTROS
from json import loads as loader
from datetime import datetime
from random import randint
import sys


def are_same_day(d1: datetime, d2: datetime) -> bool:
    """Are the two given dates the same day.

    Args:
        d1 (datetime): the first date
        d2 (datetime): the second date

    Returns:
        bool: True if the same day otherwise False
    """
    return d1.date() == d2.date()


def difference_in_minutes_between_dates(d1: datetime, d2: datetime) -> float:
    """Returns the absolute difference between the two datetime objects."""
    if d1 is None or d2 is None:
        # none is treated like infinity
        return sys.maxsize
    return abs((d1 - d2).total_seconds() / 60.0)


def is_game_in_list_of_games(game_id: int, games: List[dict]) -> bool:
    """Returns whether the given game id is in the list of games."""
    for game in games:
        if str(game_id) == str(game.get("game_id", "")):
            return True
    return False


def get_this_year() -> int:
    """Return the current year."""
    return datetime.now().year


def random_fun_comment() -> str:
    """Returns a random fun comment."""
    return FUN_COMMENT[randint(0, len(FUN_COMMENT) - 1)]


def random_emoji() -> str:
    """Returns a random emoji."""
    return EMOJI[randint(0, len(EMOJI) - 1)]


def random_intro() -> str:
    """Returns a random intro."""
    return INTROS[randint(0, len(INTROS) - 1)]


def random_sass() -> str:
    """Returns a random sassy comment."""
    return SASSY_COMMENT[randint(0, len(SASSY_COMMENT) - 1)]


def random_compliment() -> str:
    """Returns a random compliment."""
    return COMPLIMENT[randint(0, len(COMPLIMENT) - 1)]


def loads(data: any) -> dict:
    """Loads the given data as a dictionary.

    Args:
        data (any): the data to load

    Returns:
        dict: the loaded dictionary
    """
    try:
        data = loader(data)
    except Exception:
        data = loader(data.decode('utf-8'))
    return data


def log(message: any) -> None:
    """Log the given object or str.

    Args:
        message (any): the thing to log
    """
    # simple wrapper for logging to stdout on heroku
    try:
        print(str(message))
        sys.stdout.flush()
    except Exception as e:
        print(str(e))
        pass
