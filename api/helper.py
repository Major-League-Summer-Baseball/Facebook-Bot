'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds basic function that are helpful across packages
'''
import sys
from json import loads as loader
from datetime import datetime


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


def get_this_year():
    """Return the current year"""
    return datetime.now().year


def loads(data):
    try:
        data = loader(data)
    except Exception as e:
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
