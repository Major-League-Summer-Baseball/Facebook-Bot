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
from datetime import date
from api.helper import log
from flask import Flask, request
import random
import traceback
from flask_pymongo import PyMongo
from api.errors import FacebookException, IdentityException,\
    MultiplePlayersException, PlatformException, NotCaptainException,\
    BatterException
from random import randint
from base64 import b64encode
from api.variables import *
import unittest

app = Flask(__name__)
app.config['MONGO_URI'] = URL
app.config.from_object(__name__)
mongo = PyMongo(app)

# now can import db
from api.db import get_user, lookup_player, save_user, update_player,\
    already_in_league, lookup_player_email, add_homeruns, add_score, add_ss,\
    submit_score, get_games, get_upcoming_games, league_leaders, add_game,\
    change_batter, fun_meter, get_events, game_summary


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


def typing_on(sender_id):
    """Lets the user know the bot is processing
    """
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = {
            "recipient": {
                         "id": sender_id},
            "sender_action": "typing_on"
        }
    data = json.dumps(data)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      headers=headers, data=data, params=params)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def typing_off(sender_id):
    """Lets the user know the bot is processing
    """
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = {
            "recipient": {
                         "id": sender_id},
            "sender_action": "typing_off"
        }
    data = json.dumps(data)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      headers=headers, data=data, params=params)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def punch_it(data):
    """Sends the message to the user
    """
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    log(data)
    data = json.dumps(data)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      headers=headers, data=data, params=params)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def send_buttons(message_text, sender_id, buttons):
    """Send the user some buttons

    Parameters:
        message_text: the message (subheader) (string)
        sender_id: the facebook id (?)
        buttons: the list of buttons
    """
    if len(buttons) > 0 and len(buttons) <= 3:
        b = "button"
        data = {
                "recipient": {
                            "id": sender_id},
                "message": {
                            "attachment": {
                                           "type": "template",
                                           "payload": {
                                                      "template_type": b,
                                                      "text": message_text,
                                                      "buttons": buttons
                                                      }
                                           }
                             }
                }
        punch_it(data)
    elif len(buttons) > 0 and len(buttons) <= 29:
        b = "generic"
        # uncomment and add if you want add a url
        # url = BASEURL + "logo"
        message_text = "Scroll right for more \n" + message_text
        elements = [
                   {
                    "title": "Friendly Sports Bot",
#                     "image_url": url,
                    "subtitle": message_text,
                    "buttons": buttons[0:3]
                    }
                   ]
        i = 3
        while i < len(buttons):
            elements.append({
                    "title": "More options",
                    "buttons": buttons[i:i+3]
                    })
            i += 3
        data = {
                "recipient": {
                             "id": sender_id},
                "message": {
                            "attachment": {
                                           "type": "template",
                                           "payload": {
                                                      "template_type": b,
                                                      "elements": elements
                                                      }
                                           }
                             }
                }
        punch_it(data)
    else:
        # split into two messages
        send_buttons(message_text, sender_id, buttons=buttons[0:29])
        send_buttons("More options", sender_id, buttons=buttons[29:])


def send_quick_replies(message_text, sender_id, quick_replies):
    """Sends some quick replies to the user

    Parameters:
        message_text: the text for the message (string)
        sender_id: the facebook id (?)
        quick_replies: list of quick replies
    """
    # there is no point of breaking up quick replies
    data = {
            "recipient": {
                        "id": sender_id},
            "message": {
                        "text": message_text,
                        "quick_replies": quick_replies
                        }
            }
    punch_it(data)


def send_message(message_text, sender_id, quick_replies=[], buttons=[]):
    """Determines how to send the message

    Parameters:
        message_text: the text for the message (string)
        sender_id: the facebook id (?)
        quick_replies: list of quick replies
        buttons: list of buttons
    """
    data = {
            "recipient": {
                        "id": sender_id},
            "message": {
                        "text": message_text
                        }
            }
    if len(quick_replies) > 0:
        # send some quick replies
        send_quick_replies(message_text,
                           sender_id,
                           quick_replies=quick_replies)
    elif len(buttons) > 0:
        # send some buttons
        send_buttons(message_text, sender_id, buttons)
    else:
        # just send the normal text
        punch_it(data)
    typing_off(sender_id)


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    # you may not want to log every incoming message in production,
    # but it's good for testing
    log("Incoming message")
    log(data)
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                try:
                    if messaging_event.get("message"):
                        # someone sent us a message
                        # the facebook ID of the person sending you the message
                        sender_id = messaging_event["sender"]["id"]
                        # the recipient's ID, should be your page's facebook ID
                        recipient_id = messaging_event["recipient"]["id"]
                        # the message's text
                        if "text" in messaging_event['message'].keys():
                            message_text = messaging_event["message"]["text"]
                        else:
                            message_text = ""
                            parse_message(message_text, sender_id)
                        typing_on(sender_id)
                        (user, created) = get_user(sender_id, mongo)
                        if created:
                            log("First Time messaged")
                            log(user)
                            determine_player(user, sender_id)
                            log(user)
                        else:
                            log(user)
                            payload = get_payload(messaging_event)
                            figure_out(user, message_text, payload, sender_id)
                            log(user)
                    if messaging_event.get("delivery"):
                        # delivery confirmation
                        pass
                    if messaging_event.get("optin"):
                        # optin confirmation
                        pass
                    if messaging_event.get("postback"):
                        # user clicked/tapped "postback"
                        # button in earlier message
                        sender_id = messaging_event["sender"]["id"]
                        # the recipient's ID, should be your page's facebook ID
                        recipient_id = messaging_event["recipient"]["id"]
                        # the message's text
                        pay = get_postback_payload(messaging_event)
                        if pay is not None:
                            (user, created) = get_user(sender_id, mongo)
                            log(user)
                            update_payload(user,
                                           pay,
                                           sender_id)
                            log(user)
                except FacebookException as e:
                    log(str(e))
                    sender_id = messaging_event["sender"]["id"]
                    send_message(str(e), sender_id)
                except NotCaptainException as e:
                    sender_id = messaging_event["sender"]["id"]
                    (user, created) = get_user(sender_id, mongo)
                    user['state'] = BASE
                    save_user(user, mongo)
                    log(str(e))
                    send_message(str(e), sender_id)
                except PlatformException as e:
                    sender_id = messaging_event["sender"]["id"]
                    (user, created) = get_user(sender_id, mongo)
                    user['state'] = BASE
                    save_user(user, mongo)
                    log(str(e))
                    send_message(str(e), sender_id)
                except Exception as e:
                    traceback.print_exc()
                    sender_id = messaging_event["sender"]["id"]
                    log(str(e))
                    user['state'] = BASE
                    save_user(user, mongo)
                    send_message("Something fucked up, let an admin know",
                                 sender_id)
    return "ok", 200


def get_postback_payload(message):
    """Returns the payload of the post
    """
    pay = None
    if "postback" in message.keys():
        if "payload" in message['postback']:
            pay = message["postback"]['payload']
    return pay


def get_payload(message):
    """Parses a payload from a message

    Parameters"
        message: the facebook message object (dict)
    Returns
        pay: list of payload objects (list)
    """
    pay = None
    if "message" in message.keys():
        if "quick_reply" in message["message"].keys():
            if "payload" in message["message"]["quick_reply"].keys():
                pay = message['message']['quick_reply']['payload']
    return pay


def format_game(game):
    """Returns a string representation of the game
    """
    return "{}: {} vs {} @ {} on {}".format(game['date'],
                                            game['home_team'],
                                            game['away_team'],
                                            game['time'],
                                            game['field'])


def random_fun_comment():
    """Returns a random fun comment
    """
    return FUN_COMMENT[random.randint(0, len(FUN_COMMENT) - 1)]


def random_emoji():
    """Returns a random emoji
    """
    return EMOJI[random.randint(0, len(EMOJI) - 1)]


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


def base_options(user, sender_id, callback=send_message, buttons=True):
    """Present the base options

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    if buttons:
        options = [{"type": "postback",
                    "title": UPCOMING_TITLE,
                    "payload": "{}".format(UPCOMING)},
                   {"type": "postback",
                    "title": LEAGUE_LEADERS_TITLE,
                    "payload": "{}".format(LEADERS)},
                   {"type": "postback",
                    "title": EVENTS_TITLE,
                    "payload": "{}".format(EVENTS)},
                   {"type": "postback",
                    "title": FUN_TITLE,
                    "payload": "{}".format(FUN)}
                   ]
        if user['captain'] >= 0:
            options.append({"type": "postback",
                            "title": SUBMIT_SCORE_TITLE,
                            "payload": "{}".format(GAMES)},)
        callback(random_intro(), sender_id, buttons=options)
    else:
        options = [{"content_type": "text",
                    "title": UPCOMING_TITLE,
                    "payload": "{}".format(UPCOMING)},
                   {"content_type": "text",
                    "title": LEAGUE_LEADERS_TITLE,
                    "payload": "{}".format(LEADERS)},
                   {"content_type": "text",
                    "title": EVENTS_TITLE,
                    "payload": "{}".format(EVENTS)},
                   {"content_type": "text",
                    "title": FUN_TITLE,
                    "payload": "{}".format(FUN)}
                   ]
        if user['captain'] >= 0:
            options.append({"content_type": "text",
                            "title": SUBMIT_SCORE_TITLE,
                            "payload": "{}".format(GAMES)},)
        callback(random_intro(), sender_id, quick_replies=options)


def display_homeruns(user, sender_id, callback=send_message):
    """Display the batters for homerunes"""
    options = []
    for player_id, player in user['teamroster'].items():
        if player['player_id'] not in user['game']['hr']:
            options.append({"type": "postback",
                            "title": player['player_name'],
                            "payload": player['player_id']})
    options.append({"type": "postback",
                    "title": DONE_COMMENT,
                    "payload": "done"})
    options.append({"type": "postback",
                    "title": CANCEL_COMMENT,
                    "payload": "cancel"})
    callback(PICKBATTER_COMMENT.format("hr"), sender_id, buttons=options)


def display_ss(user, sender_id, callback=send_message):
    """Display the batters for ss"""
    options = []
    for player_id, player in user['teamroster'].items():
        if (player['gender'].lower() == "f" and
            player['player_id'] not in user['game']['ss']):
            options.append({"type": "postback",
                            "title": player['player_name'],
                            "payload": player['player_id']})
    options.append({"type": "postback",
                    "title": DONE_COMMENT,
                    "payload": "done"})
    options.append({"type": "postback",
                    "title": CANCEL_COMMENT,
                    "payload": "cancel"})
    callback(PICKBATTER_COMMENT.format("ss"), sender_id, buttons=options)


def display_upcoming_games(user, sender_id, callback=send_message):
    """display the upcoming games for the user

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    games = get_upcoming_games(user)
    comments = []
    for game in games:
        comments.append(format_game(game))
    if (len(comments)) > 0:
        callback("\n".join(comments), sender_id)
    else:
        callback(NOGAMES_COMMENT, sender_id)


def display_games(user, sender_id, callback=send_message):
    """display the games to submit scores for the user

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    games = get_games(user)
    quick_replies = []
    for game in games:
        quick_replies.append({'content_type': "text",
                              "title": format_game(game),
                              "payload": game['game_id']})
    quick_replies.append({'content_type': "text",
                          "title": CANCEL_COMMENT,
                          "payload": "cancel"})
    user['state'] = GAMES
    save_user(user, mongo)
    callback(PICKGAME_COMMENT, sender_id, quick_replies=quick_replies)


def display_league_leaders(user, sender_id, callback=send_message):
    """display the league leaders

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    leaders = league_leaders("hr")
    comment = [HR_TITLE]
    for leader in leaders:
        comment.append("{} ({}): {:d}".format(leader['name'],
                                              leader['team'],
                                              leader['hits']))
    callback("\n".join(comment), sender_id)
    leaders = league_leaders("ss")
    comment = [SS_TITLE]
    for leader in leaders:
        comment.append("{} ({}): {:d}".format(leader['name'],
                                              leader['team'],
                                              leader['hits']))
    callback("\n".join(comment), sender_id)


def display_fun(user, sender_id, callback=send_message):
    """display the fun meter

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    fun = fun_meter()
    count = 0
    for element in fun:
        if element['year'] == date.today().year:
            count = element['count']
    message = count * random_emoji()
    message += "\n" + random_fun_comment()
    message += "\n" + FUN_TOTAL_COMMENT.format(count)
    callback(message, sender_id)


def display_summary(user, sender_id, callback=send_message):
    """displays a submit score summary

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    summary = game_summary(user)
    replies = [{'content_type': "text",
                "title": SUBMIT_TITLE,
                "payload": "submit",
                "image_url":
                "http://www.clker.com/cliparts/Z/n/g/w/C/y/green-dot-md.png"},
               {'content_type': "text",
                "title": CANCEL_COMMENT,
                "payload": "cancel",
                "image_url":
                "http://www.clker.com/cliparts/T/G/b/7/r/A/red-dot-md.png"},
               ]
    callback("\n".join(summary), sender_id, quick_replies=replies)


def display_events(user, sender_id, callback=send_message):
    """display the events

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    events = get_events()
    message = []
    for event, date in events.items():
        message.append("{} - {}".format(event.replace("_", " "), date))
    callback("\n".join(message), sender_id)


def determine_player(user, sender_id, callback=send_message):
    """Try to figure out who this person is

    Parameters:
        user: the user dictionary (dict)
        sender_id: the sender facebook id (? something)
        callback: the thing to call with a result (function)
    """
    player = lookup_player(user)
    if player is None:
        user['state'] = EMAIL
        save_user(user, mongo)
        callback(ASK_EMAIL_COMMENT, sender_id)
    else:
        # know these person
        if already_in_league(user, player, mongo):
            # imposter or someone stole their info
            callback(IDENTITY_STOLEN_COMMENT, sender_id)
            user["state"] = IGNORE
            save_user(user, mongo)
        else:
            user = update_player(user, player)
            user['state'] = BASE
            save_user(user, mongo)
            callback(WELCOME_LEAGUE.format(user['name']), sender_id)
            callback(HELP_COMMENT, sender_id)
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
            player = lookup_player_email(user, email.lower())
            if already_in_league(user, player, mongo):
                # imposter or someone stole their info
                callback(IDENTITY_STOLEN_COMMENT, sender_id)
                user["state"] = IGNORE
                save_user(user, mongo)
            else:
                user = update_player(user, player)
                user['state'] = BASE
                save_user(user, mongo)
                callback(WELCOME_LEAGUE.format(user['name']), sender_id)
                callback(HELP_COMMENT, sender_id)
                base_options(user, sender_id, callback=callback)
        except IdentityException:
            callback(NOT_FOUND_COMMENT, sender_id)
    else:
        callback(NO_EMAIL_GIVEN_COMMENT, sender_id)


def help_user(user, sender_id, callback=send_message):
    """Display help for the user

    Parameters:
        user: the user dictionary (dict)
        sender_id: the facebook id (?)
        callback: the thing to call with a result (function)
    """
    if user['state'] == BASE:
        callback("\n".join(BASE_HELP_OPTIONS), sender_id)
        figure_out(user, "", None, sender_id, callback=callback)
    elif user['state'] == HR_BAT:
        callback(HR_BAT_HELP_COMMENT,
                 sender_id)
        display_homeruns(user, sender_id, callback=callback)
    elif user['state'] == SS_BAT:
        callback(SS_BAT_HELP_COMMENT, sender_id)
        display_ss(user, sender_id, callback=callback)
    elif user['state'] == HR_NUM:
        callback(HR_NUM_HELP_COMMENT, sender_id)
    elif user['state'] == SS_NUM:
        callback(SS_NUM_HELP_COMMENT, sender_id)


def parse_number(text):
    """Returns the first number in the text
    """
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


def update_payload(user,
                   payload,
                   sender_id,
                   callback=send_message):
    """Update the states based on the given payload

    Parameters:
        user: the user dictionary (dict)
        payload: the payload attached to the message (string)
        sender_id: the facebook id (?)
        callback: the thing to call with a result (function)
    """
    if user['state'] == BASE:
        # quite a few options
        if payload == GAMES:
            display_games(user, sender_id, callback=callback)
        elif payload == UPCOMING:
            display_upcoming_games(user, sender_id, callback=callback)
        elif payload == FUN:
            display_fun(user, sender_id, callback=callback)
        elif payload == LEADERS:
            display_league_leaders(user, sender_id, callback=callback)
        elif payload == EVENTS:
            display_events(user, sender_id, callback=callback)
    elif user['state'] == GAMES:
        game = parse_number(payload)
        if (game > 0):
            user = add_game(user, game)
            user['state'] = SCORE
            save_user(user, mongo)
            callback(SCORE_COMMENT, sender_id)
        else:
            user['state'] = BASE
            save_user(user, mongo)
            callback(INVALID_GAME_COMMENT, sender_id)
    elif user['state'] == HR_BAT:
        batter = parse_number(payload)
        if batter > 0:
            try:
                user = change_batter(user, batter)
                user['state'] = HR_NUM
                save_user(user, mongo)
                pname = user['teamroster'][str(batter)]['player_name']
                message = HIT_NUM_COMMENT.format("hr", pname)
                callback(message, sender_id)
            except BatterException:
                callback(INVALID_BATTER_COMMENT, sender_id)
                display_homeruns(user, sender_id, callback=callback)
        elif payload.lower() in ["done", "ok", DONE_COMMENT.lower()]:
            user['state'] = SS_BAT
            save_user(user, mongo)
            display_ss(user, sender_id, callback=callback)
        elif payload.lower() in ["cancel", "no", CANCEL_COMMENT.lower()]:
            user['state'] = BASE
            save_user(user, mongo)
            callback(CANCELING_COMMENT, sender_id)
        else:
            callback(INVALID_BATTER_COMMENT, sender_id)
    elif user['state'] == SS_BAT:
        batter = parse_number(payload)
        if batter > 0:
            try:
                user = change_batter(user, batter)
                user['state'] = SS_NUM
                save_user(user, mongo)
                pname = user['teamroster'][str(batter)]['player_name']
                message = HIT_NUM_COMMENT.format("ss", pname)
                callback(message, sender_id)
            except BatterException:
                callback(INVALID_BATTER_COMMENT, sender_id)
                display_ss(user, sender_id, callback=callback)
        elif payload == "done":
            user['state'] = REVIEW
            save_user(user, mongo)
            display_summary(user, sender_id, callback=callback)
        elif payload.lower() == "cancel":
            user['state'] = BASE
            save_user(user, mongo)
            callback(CANCELING_COMMENT, sender_id)
        else:
            callback(INVALID_BATTER_COMMENT, sender_id)


def figure_out(user, message_text, payload, sender_id, callback=send_message):
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
            # support if they just type of the things
            print()
            if payload is None:
                payload = ""
            options = (message_text.lower(), payload.lower())
            if (UPCOMING.lower() in options or
                UPCOMING_TITLE.lower() in options):
                update_payload(user, UPCOMING, sender_id, callback=callback)
            elif (LEADERS.lower() in options or
                  LEAGUE_LEADERS_TITLE.lower() in options):
                update_payload(user, LEADERS, sender_id, callback=callback)
            elif EVENTS.lower() in options or EVENTS_TITLE.lower() in options:
                update_payload(user, EVENTS, sender_id, callback=callback)
            elif FUN.lower() in options or FUN_TITLE.lower() in options:
                update_payload(user, FUN, sender_id, callback=callback)
            elif (SUBMIT_SCORE_TITLE.lower() in options or
                  "submit score" in options or GAMES.lower() in options):
                print("yep")
                update_payload(user, GAMES, sender_id, callback=callback)
            else:
                base_options(user, sender_id, callback=callback)
        elif user['state'] == GAMES:
            if message_text.lower() in ["cancel",
                                        "nvm",
                                        "no",
                                        CANCEL_COMMENT.lower()]:
                user['state'] = BASE
                save_user(user, mongo)
                callback(CANCELING_COMMENT, sender_id)
                base_options(user, sender_id, callback=callback)
            elif payload is None:
                user['state'] = BASE
                save_user(user, mongo)
                callback(USE_QUICK_REPLIES_COMMENT, sender_id)
                update_payload(user, GAMES, sender_id, callback=callback)
            else:
                game = parse_number(payload)
                if game > 0:
                    user = add_game(user, game)
                    user['state'] = SCORE
                    save_user(user, mongo)
                    callback(SCORE_COMMENT, sender_id)
                elif payload.lower() in ("cancel",
                                         "no",
                                         CANCEL_COMMENT.lower()):
                    user['state'] = BASE
                    save_user(user, mongo)
                    base_options(user, sender_id, callback=callback)
                else:
                    callback(NEED_GAME_NUMBER_COMMENT, sender_id)
                    user['state'] = BASE
                    save_user(user, mongo)
        elif user['state'] == SCORE:
            score = parse_number(message_text)
            if message_text.lower() in ["cancel",
                                        "nvm",
                                        "no",
                                        CANCEL_COMMENT.lower()]:
                user['state'] = BASE
                save_user(user, mongo)
                base_options(user, sender_id, callback=callback)
            elif score < 0:
                # said something random
                callback(DIDNT_UNDERSTAND_COMMENT, sender_id)
                callback(SCORE_COMMENT, sender_id)
            elif score == 0:
                # skip homeruns
                user = add_score(user, score)
                user['state'] = SS_BAT
                save_user(user, mongo)
                display_ss(user, sender_id, callback=callback)
            else:
                user = add_score(user, score)
                user['state'] = HR_BAT
                save_user(user, mongo)
                display_homeruns(user, sender_id, callback=callback)
        elif user['state'] == HR_NUM:
            number = parse_number(message_text)
            if len(user['game']['hr']) + number == user['game']['score']:
                # no more hrs can be assigned
                user = add_homeruns(user, user['batter'], number)
                user['state'] = SS_BAT
                save_user(user, mongo)
                display_ss(user, sender_id, callback=callback)
            else:
                if number < 0:
                    callback(DIDNT_UNDERSTAND_COMMENT, sender_id)
                elif len(user['game']['hr']) + number < user['game']['score']:
                    user = add_homeruns(user, user['batter'], number)
                else:
                    callback(TOO_MANY_HR_COMMENT, sender_id)
                # move back to batter
                user['state'] = HR_BAT
                save_user(user, mongo)
                display_homeruns(user, sender_id, callback=callback)
        elif user['state'] == SS_NUM:
            number = parse_number(message_text)
            if number > 0:
                user = add_ss(user, user['batter'], number)
            else:
                callback(DIDNT_UNDERSTAND_COMMENT, sender_id)
            # move back to batter
            user['state'] = SS_BAT
            save_user(user, mongo)
            display_ss(user, sender_id, callback=callback)
        elif user['state'] == REVIEW:
            if payload is None:
                payload = ""
            if (message_text.lower() in ("yes",
                                         "submit",
                                         SUBMIT_TITLE.lower(),
                                         SUBMIT_SCORE_TITLE.lower()) or
                payload.lower() in ("submit",
                                    "yes",
                                    SUBMIT_TITLE.lower(),
                                    SUBMIT_SCORE_TITLE.lower())):
                # save the score
                user = submit_score(user)
                callback(GAME_SUBMITTED_COMMENT, sender_id)
            else:
                # guess they are cancelling
                user['game'] = {}
                callback(CANCELING_COMMENT, sender_id)
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
    if re.search("who(\s?)('s)*the(\s?)best", message):
        response = "Obviously the Maple Leafs"
        callback(response.strip(), sender_id)
    elif re.search(r"would(\s?)you(\s?)rather", message):
        message = re.sub(r'[^a-zA-Z0-9_\s]', '', message)
        clause = message.split("rather")[1]
        proposition = clause.split(" or ")
        pick_proposition = proposition[randint(0, len(proposition) - 1)]
        response = pick_proposition
        callback(response.strip(), sender_id)


def change_mongo(m):
    """Used for testing
    """
    global mongo
    mongo = m


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
