'''
@author: Dallas Fraser
@author: 2020-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Holds functions related to parsing information from
'''
from typing import List, Tuple
from datetime import datetime, timedelta, date
import numpy as np

# how much confidence need for partial matches
MATCHING_CONFIDENCE = 0.80
NUMBER_MAP = {
    "one": 1,
    "uno": 1,
    "two": 2,
    "deuce": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20}


def parse_number(text: str) -> int:
    """Parses out the first number from the given text.

    Args:
        text (str): the text to parse the number from

    Returns:
        int: the first number encountered. otherwise
    """
    numbers = parse_numbers(text)
    return None if len(numbers) == 0 else numbers[0]


def parse_numbers(text):
    """Parses all the numbers from the given text"""
    numbers = []
    if type(text) is str:
        tokens = get_tokens(text)
        for token in tokens:
            try:
                number = NUMBER_MAP.get(token, None)
                if number is None:
                    number = int(token)
                numbers.append(number)
            except ValueError:
                pass
    else:
        try:
            numbers.append(int(text))
        except ValueError:
            pass
    return numbers


def get_tokens(text):
    """Returns a list of tokens"""
    text = text.lower().strip()
    for delim in ',;-':
        text = text.replace(delim, ' ')
    return text.split()


def parse_out_email(message_string: str) -> str:
    """Returns an email that is contained in the message.

    Parameters:
        message_string: the message that may/may not contain email
    Returns:
        the email or None if one is not found
    """
    tokens = get_tokens(message_string)
    for token in tokens:
        if "@" in token and token != "@":
            return token
    return None


def handle_common_english_dates(message_string: str) -> date:
    """Handle common phrases for

    Args:
        message_string (str): [description]

    Returns:
        date: [description]
    """
    message = message_string.lower().strip()
    if "from today" in message:
        days = parse_number(message)
        if days is not None:
            return date.today() + timedelta(days=days)
        return None
    elif "today" in message:
        return date.today()
    elif "yesterday" in message:
        return date.today() - timedelta(days=1)
    elif "days ago" in message or "day ago" in message:
        days = parse_number(message)
        if days is not None:
            return date.today() - timedelta(days=days)
        return None
    elif "tomorrow" in message:
        return date.today() + timedelta(days=1)
    return None


def parse_out_date(message_string: str) -> date:
    """Parse out a date from the given message.

    Args:
        message_string (str): a message that may contain a date

    Returns:
        datetime: the parsed date or None if None is found
    """
    message = message_string.lower().strip()

    date = handle_common_english_dates(message_string)
    if date is not None:
        return date

    # maybe given a date string
    for token in message.split():
        try:
            return datetime.strptime(token, '%Y-%m-%d').date()
        except ValueError:
            pass
    return None


def levenshtein_ratio(string_one: str, string_two: str) -> float:
    """Calculate levenshtein ratio.

    Args:
        string_one (str): the first string
        string_two (str): the second string

    Returns:
        float: a ratio betweeo 0 and 1 with 1 being highly similar
    """
    rows = len(string_one)+1
    cols = len(string_two)+1
    distance = np.zeros((rows, cols), dtype=int)

    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k

    for col in range(1, cols):
        for row in range(1, rows):
            if string_one[row-1] == string_two[col-1]:
                cost = 0
            else:
                cost = 2
            distance[row][col] = min(distance[row-1][col] + 1,
                                     distance[row][col-1] + 1,
                                     distance[row-1][col-1] + cost)
    l1 = len(string_one)
    l2 = len(string_two)
    ratio = ((l1 + l2) - distance[row][col]) / (l1 + l2)
    return ratio


def parse_out_player(message: str, players: List[dict]) -> List[dict]:
    """Parse out the player from a message.

    Args:
        message (str): a message that may contain a player
        players (List[dict]): the list of players to match to

    Returns:
        List[dict]: the players that were matched
    """
    best_match = (0, [])
    for token in get_tokens(message):
        match = match_with_player(token, players)
        if match[0] > best_match[0]:
            best_match = match
    return best_match[1]


def find_names(name: str) -> Tuple[str, List[str]]:
    """Try to find a name to match against from the given name

    Args:
        name (str): a message that may contain a name, full name or t.lastname

    Returns:
        Tuple[str, List[str]]: a name to try and other tiebreaker names
    """
    names = name.split(".")
    if len(names) > 2:
        return (None, [])
    elif len(names) > 1:
        name = names[0] if len(names[0]) > len(names[1]) else names[1]
        return (name, names)
    else:
        names = name.split(" ")
        if len(names) == 2:
            name = names[0] if len(names[0]) > len(names[1]) else names[1]
            return (name, names)
        elif (len(names) == 1):
            return (names[0], names)
        return (None, names)


def handle_tie_breaker(players: List[dict],
                       names: List[str]) -> Tuple[float, List[dict]]:
    """Handle a tie breaker based upon first or last name

    Args:
        players (List[dict]): a list of players who match equally already
        names (List[str]): the list of names to match against

    Returns:
        Tuple[float, List[dict]]: the best match
    """
    use_lastname = False if len(names[1]) > len(names[0]) else True
    tiebreaker = []
    for player in players:
        p_names = player.get("player_name").split()
        if use_lastname and len(p_names) >= 2:
            if p_names[1].startswith(names[1]):
                tiebreaker.append(player)
        elif not use_lastname:
            if p_names[0].startswith(names[0]):
                tiebreaker.append(player)
    return tiebreaker


def match_with_player(name: str,
                      players: List[dict]) -> Tuple[float, List[dict]]:
    """Match the given name with someone from the list of players.

    Args:
        name (str): the name to compare
        players (List[dict]): a list of players to match with

    Returns:
        List[dict]: the match score and a list of players who equally
                    match the given name
    """
    # if name contains a dot then might need a tiebreaker
    (name, names) = find_names(name)
    if name is None:
        return (0, [])

    possible_result = (0, [])
    for player in players:
        match = levenshtein_ratio(name, player.get("player_name"))
        if match > possible_result[0]:
            possible_result = (match, [player])
        elif match == possible_result[0]:
            possible_result[1].append(player)

    if len(possible_result[1]) > 1 and len(names) == 2:
        # deal with a tiebreaker
        tiebreaker = handle_tie_breaker(possible_result[1], names)
        return (1, tiebreaker) if len(tiebreaker) > 0 else possible_result
    return possible_result


def match_with_team(name: str, team: str) -> float:
    """Returns the best match.

    Args:
        name (str): the name to try to match against the team
        team (str): the name of the team

    Returns:
        float: the best match with a ratio from 0-1
    """
    name = name.lower().strip()
    best_match = 0
    for token in get_tokens(team):
        match = levenshtein_ratio(token, name)
        if match > best_match:
            best_match = match
    return best_match


def match_game(message: str, games: List[dict]) -> dict:
    """Matches from the list of games the one that likely meant

    Args:
        message (str): the message that may contain a game
        games (List[dict]): a list of games to match with

    Returns:
        dict: the game if a decent match is determined otherwise None
    """

    # try to match based upon date
    date = parse_out_date(message)
    if date is not None:
        for game in games:
            # if get an exact match with date then it pretty obvious they
            # most likely meant this
            if date == datetime.strptime(game.get('date'), '%Y-%m-%d').date():
                return game

    # try to match with some team name
    best_match_with_team = [None, 0]
    for token in get_tokens(message):
        for game in games:
            match = max(match_with_team(token, game.get("away_team")),
                        match_with_team(token, game.get("home_team")))
            if match > best_match_with_team[1]:
                best_match_with_team[0] = game
                best_match_with_team[1] = match
    if (best_match_with_team[0] is not None and
            best_match_with_team[1] > MATCHING_CONFIDENCE):
        return best_match_with_team[0]
    return None
