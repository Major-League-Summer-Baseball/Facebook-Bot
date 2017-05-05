'''
@author: Dallas Fraser
@date: 2016-11-26
@organization: Fun
@summary: Holds the app
'''
import os
import sys
import json
import re
import requests
from api.helper import log
from flask import Flask, request
import random
from flask.ext.pymongo import PyMongo
from api.errors import FacebookException, IdentityException,\
    MultiplePlayersException, PlatformException, NotCaptainException
from random import randint
from base64 import b64encode
from sqlalchemy.ext.mutable import Mutable
from api.variables import PID, EMAIL, IGNORE, BASE, GAMES, SCORE, HR_BAT,\
                          REVIEW, UPCOMING, LEADERS, EVENTS, FUN,\
                          INTROS, HR_NUM, SS_BAT, SS_NUM, SASSY_COMMENT,\
                          COMPLIMENT
import unittest
from nltk.misc.sort import quick

app = Flask(__name__)
if os.environ.get("LOCAL", "TRUE") == "FALSE":
    URL = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/rest")
    BASEURL = os.environ.get("PLATFORM",
                             "http://mlsb-dallas-branch.herokuapp.com/")
    ADMIN = os.environ.get("ADMIN", "d6fraser")
    PASSWORD = os.environ.get("PASSWORD", "Test")
    PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "NONE")
    VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "NONE")
else:
    from api.credentials import BASEURL, URL, ADMIN, PASSWORD,\
                                PAGE_ACCESS_TOKEN, VERIFY_TOKEN

app.config['MONGO_URI'] = URL
app.config.from_object(__name__)
mongo = PyMongo(app)

# now can import db
from api.db import get_user, lookup_player, save_user, update_player,\
    already_in_league, lookup_player_email, add_homeruns, add_score, add_ss,\
    submit_score, get_games, get_upcoming_games, league_leaders

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if (request.args.get("hub.mode") == "subscribe" and
        request.args.get("hub.challenge")):
        if (not request.args.get("hub.verify_token") == VERIFY_TOKEN):
            log("Not right token")
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200


def send_message(message_text, sender_id, quick_replies=[]):
    log("sending message reply to {sender}: {text}".format(sender=sender_id,
                                                           text=message_text))
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    if len(quick_replies) > 0:
        data = {
                "recipient": {
                            "id": sender_id},
                "message": {
                            "text": message_text,
                            "quick_replies": quick_replies
                            }
                }
    else:
        data = {
                "recipient": {
                            "id": sender_id},
                "message": {
                            "text": message_text
                            }
                }
    print(data)
    data = json.dumps(data)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      headers=headers, data=data, params=params)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    # you may not want to log every incoming message in production,
    # but it's good for testing
    log(data)
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    # the facebook ID of the person sending you the message
                    sender_id = messaging_event["sender"]["id"]
                    # the recipient's ID, should be your page's facebook ID
                    recipient_id = messaging_event["recipient"]["id"]
                    # the message's text
                    message_text = messaging_event["message"]["text"]
                    parse_message(message_text, sender_id)
                    try:
                        (user, created) = get_user(sender_id, mongo)
                        log(user)
                        log(created)
                        if created:
                            determine_player(user, sender_id)
                        else:
                            payload = get_payload(messaging_event)
                            if payload is not None:
                                update_payload(user,
                                               message_text,
                                               payload,
                                               sender_id)
                            else:
                                figure_out(user,
                                           message_text,
                                           sender_id)
                    except FacebookException as e:
                        log(str(e))
                        send_message(str(e), sender_id)
                    except PlatformException as e:
                        log(str(e))
                        send_message(str(e), sender_id)
                    except Exception as e:
                        log(e)
                        send_message("Something fucked up, let an admin know",
                                     sender_id)
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass
                if messaging_event.get("optin"):  # optin confirmation
                    pass
                if messaging_event.get("postback"):
                    # user clicked/tapped "postback" button in earlier message
                    pass
    return "ok", 200


def get_payload(message):
    """Parses a payload from a message

    Parameters"
        message: the facebook message object (dict)
    Returns
        pay: list of payload objects (list)
    """
    pay = None
    if "quick_replies" in message.keys():
        pay = message['quick_replies']
    return pay


def format_game(game):
    """Returns a string representation of the game
    """
    return "{} vs {} @ {} on {}".format(game['home_team'],
                                        game['away_team'],
                                        game['date'] + " " + game['time'],
                                        game['field'])


def random_intro():
    """Returns a random intro
    """
    return INTROS[random.randint(0, len(INTROS) - 1)]


def random_sass():
    """Returns a random sassy comment
    """
    return SASSY_COMMENT[random.randint(0, len(SASSY_COMMENT) - 1)]


def random_compliment():
    """Returns a random compliment
    """
    return COMPLIMENT[random.randint(0, len(COMPLIMENT) - 1)]


def base_options(user, sender_id, callback=send_message):
    """Present the base options

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    quick_replies = [{"content_type": "text",
                      "title": "Upcoming Games",
                      "payload": "{}".format(UPCOMING)},
                     {"content_type": "text",
                      "title": "League Leaders",
                      "payload": "{}".format(LEADERS)},
                     {"content_type": "text",
                      "title": "Events",
                      "payload": "{}".format(EVENTS)},
                     {"content_type": "text",
                      "title": "Fun Meter",
                      "payload": "{}".format(FUN)}
                     ]
    if user['captain'] >= 0:
        quick_replies.append({"content_type": "text",
                              "title": "Submit Score",
                              "payload": "{}".format(GAMES)},)
    callback(random_intro(), sender_id, quick_replies=quick_replies)


def display_homeruns(user, sender_id, callback=send_message):
    """Display the batters for homerunes"""
    quick_replies = []
    for player in user['team_roster']:
        if player['player_id'] not in user['game']['hr']:
            quick_replies.append({'content_type': "text",
                                  "title": player['player_name'],
                                  "payload": player['player_id']})
    quick_replies.append({'content_type': "text",
                          "title": "Done",
                          "payload": "done"})
    quick_replies.append({'content_type': "text",
                          "title": "Cancel",
                          "payload": "cancel"})
    callback("Pick a batter who hit a hr:",
             sender_id,
             quick_replies=quick_replies)


def display_ss(user, sender_id, callback=send_message):
    """Display the batters for ss"""
    quick_replies = []
    for player in user['team_roster']:
        if (player['gender'].lower() == "f" and
            player['player_id'] not in user['game']['ss']):
            quick_replies.append({'content_type': "text",
                                  "title": player['player_name'],
                                  "payload": player['player_id']})
    quick_replies.append({'content_type': "text",
                          "title": "Done",
                          "payload": "done"})
    quick_replies.append({'content_type': "text",
                          "title": "Cancel",
                          "payload": "cancel"})
    callback("Pick a batter who hit a ss:",
             sender_id,
             quick_replies=quick_replies)


def display_upcoming_games(user, sender_id, callback=send_message):
    """display the upcoming games for the user

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    games = get_upcoming_games()
    quick_replies = []
    for game in games:
        quick_replies.append({'content_type': "text",
                              "title": format_game(game),
                              "payload": game['game_id']})
    quick_replies.append({'content_type': "text",
                          "title": "Cancel",
                          "payload": "cancel"})
    callback("Pick a game to submit score for",
             sender_id,
             quick_replies=quick_replies)


def display_games(user, sender_id, callback=send_message):
    """display the games to submit scores for the user

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    try:
        games = get_games(user)
        quick_replies = []
        for game in games:
            quick_replies.append({'content_type': "text",
                                  "title": format_game(game),
                                  "payload": game['game_id']})
        quick_replies.append({'content_type': "text",
                              "title": "Cancel",
                              "payload": "cancel"})
        callback("Pick a game to submit score for",
                 sender_id,
                 quick_replies=quick_replies)
    except NotCaptainException as e:
        # who is this imposter
        callback(str(e), sender_id)
        user['state'] = BASE
        save_user(user, mongo)


def display_league_leaders(user, sender_id, callback=send_message):
    """display the league leaders

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    leaders = league_leaders("hr")
    comment = ["HR Leaders:"]
    for leader in leaders:
      comment.append("{} ({}): {:d}".format(leader['name']),
                                            leader['team'],
                                            leader['hits'])
    callback("\n".join(comment), sender_id)
    leaders = league_leaders("ss")
    comment = ["SS Leaders:"]
    for leader in leaders:
      comment.append("{} ({}): {:d}".format(leader['name']),
                                            leader['team'],
                                            leader['hits'])
    callback("\n".join(comment), sender_id)


def determine_player(user, sender_id, callback=send_message):
    """Try to figure out who this person is

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    player = lookup_player(user)
    if player is None:
        log("Not sure who they are, asking for email")
        user['state'] = EMAIL
        save_user(user, mongo)
        callback("What's your email associated with the league",
                 sender_id)
    else:
        # know these person
        if already_in_league(user, player, mongo):
            # imposter or someone stole their info
            callback("Someone already appears to be you, contact admin",
                     sender_id)
            user["state"] = IGNORE
            save_user(user, mongo)
        else:
            user = update_player(user, player)
            user['state'] = BASE
            save_user(user, mongo)
            callback("Welcome to the league", sender_id)
            callback("If you ever need help just type: HELP",
                     sender_id)
            base_options(user, sender_id, callback=callback)


def check_email(user, message, sender_id, callback=send_message):
    """Try to figure out who this person is

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    tokens = message.split(" ")
    email = ""
    for token in tokens:
        if "@" in token:
            email = token
            break
    if email != "":
        try:
            player = lookup_player_email(user, email)
            if already_in_league(user, player, mongo):
                # imposter or someone stole their info
                callback("Someone already appears to be you, contact admin",
                         sender_id)
                user["state"] = IGNORE
                save_user(user, mongo)
            else:
                user = update_player(user, player)
                user['state'] = BASE
                save_user(user, mongo)
                callback("Welcome to the league", sender_id)
                callback("If you ever need help just type: HELP",
                         sender_id)
                base_options(user, sender_id, callback=callback)
        except IdentityException:
            callback("Looks like your email is not recored, contact admin",
                     sender_id)
    else:
        callback("No email was given, (looking for @)", sender_id)


def help_user(user, sender_id, callback=send_message):
    """Display help for the user

    Parameters:
        user: the user dictionary (dict)
        sender_id: the facebook id (?)
        callback: the thing to call with a result (function)
    """
    if user['state'] == BASE:
        options = ["Upcoming games: Find out what games you have upcoming",
                   "League leaders: who leading the league",
                   "Events: what are the events for this year",
                   "Fun meter: how much fun has this summer been",
                   "Submit score: if you are captain submit a score"]
        callback("\n".join(options), sender_id)
        figure_out(user, "", sender_id, callback=callback)
    elif user['state'] == HR_BAT:
        callback("Who hit a HR, if you dont see a player contact admin",
                 sender_id)
        display_homeruns(user, sender_id, callback=callback)
    elif user['state'] == SS_BAT:
        m = ("Who hit a SS (only females)," +
             " if you don't see a player contact admin")
        callback(m, sender_id)
        display_ss(user, sender_id, callback=callback)


def parse_number(text):
    """Returns the first number in the text
    """
    tokens = text.split(" ")
    number = 0
    for token in tokens:
        try:
            number = int(token)
            break
        except ValueError:
            pass
    return number


def update_payload(user,
                   message_text,
                   payload,
                   sender_id,
                   callback=send_message):
    """Update the states based on the given payload

    Parameters:
        user: the user dictionary (dict)
        message_text: the text message (string)
        payload: the payload attached to the message (string)
        sender_id: the facebook id (?)
        callback: the thing to call with a result (function)
    """
    if user['state'] == BASE:
        # quite a few options
        number = parse_number(payload)
        if number  == GAMES:
            display_games(user, sender_id, callback=callback)
            user['state'] = GAMES
        elif number == UPCOMING:
            display_upcoming_games(user, sender_id, callback=callback)


def figure_out(user, message_text, sender_id, callback=send_message):
    """Figure out what the user is typing

    Parameters:
        user: the user dictionary (dict)
        message_text: the text message (string)
        sender_id: the facebook id (?)
        callback: the thing to call with a result (function)
    """
    if message_text.lower() == "help":
        help_user(user, sender_id, callback=callback)
    else:
        if user['state'] == PID:
            determine_player(user, sender_id, callback=callback)
        elif user['state'] == EMAIL:
            check_email(user, message_text, sender_id, callback=callback)
        elif user['state'] == BASE:
            base_options(user, sender_id, callback=callback)
        elif user['state'] == HR_NUM:
            number = parse_number(message_text)
            if number > 0:
                add_homeruns(user, user['batter'], int(message_text))
            else:
                callback("Didn't understand how many",
                         sender_id,
                         callback=callback)
            # move back to batter
            user['state'] = HR_BAT
            save_user(user, mongo)
            display_homeruns(user, sender_id, callback=callback)
        elif user['state'] == SS_NUM:
            number = parse_number(message_text)
            if number > 0:
                add_ss(user, user['batter'], int(message_text))
            else:
                callback("Didn't understand how many",
                         sender_id,
                         callback=callback)
            # move back to batter
            user['state'] = SS_BAT
            save_user(user, mongo)
            display_ss(user, sender_id, callback=callback)
        elif user['state'] == REVIEW:
            if message_text.lower() == "yes":
                # save the score
                user = submit_score(user)
            else:
                # guess they are cancelling
                user['game'] = {}
            user['state'] = BASE
            save_user(user, mongo)


def parse_message(message, sender_id, callback=send_message):
    """Parse a basic message

    Parameters:
        message: the message received
        sender_id: the facebook id (?)
        callback: the thing to call with a result (function)
    """
    message = message.lower()
    basic_response(message, callback, sender_id)


def basic_response(message, sender_id, callback=send_message):
    """Parse a basic message

    Parameters:
        message: the message received
        sender_id: the facebook id (?)
        callback: the thing to call with a result (function)
    """
    log("basic response")
    log(message)
    if re.search("who(\s?)('s)*the(\s?)best", message):
        log("Hit")
        response = "Obviously the Maple Leafs"
        callback(response.strip(), sender_id)
    elif re.search(r"would(\s?)you(\s?)rather", message):
        message = re.sub(r'[^a-zA-Z0-9_\s]', '', message)
        clause = message.split("rather")[1]
        proposition = clause.split(" or ")
        pick_proposition = proposition[randint(0, len(proposition) - 1)]
        response = pick_proposition
        callback(response.strip(), sender_id)


def mock_callback(message_text, sender_id, quick_replies=[]):
    """Mock the callback function

    Parameters:
        message_text: the message received (string)
        sender_id: the facebook id (?)
        callback: the thing to call with a result (function)
    """
    log(message_text)
    log(quick_replies)


class TestFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass





if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
