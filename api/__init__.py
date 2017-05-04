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
from flask.ext.pymongo import PyMongo
from api.errors import FacebookException, IdentityException,\
    MultiplePlayersException
from random import randint
from base64 import b64encode
from sqlalchemy.ext.mutable import Mutable
from api.variables import PID, EMAIL, IGNORE, BASE, GAMES, SCORE, HOMERUNS,\
                       SPECIALS, REVIEW
import unittest

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
from api.db import get_user, lookup_player

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
                    parse_message(message_text, send_message, sender_id)
                    try:
                        (user, created) = get_user(sender_id, mongo)
                        log(user)
                        log(created)
                        if created:
                            determine_player(user)
                        else:
                            payload = get_payload(messaging_event)
                            if payload is not None:
                                update_payload(user, message_text, payload)
                            else:
                                figure_out(user, message_text)
                    except FacebookException as e:
                        log(str(e))
                        send_message(str(e),
                                     sender_id)
                    except Exception as e:
                        log(e)
                        send_message("Not sure what you mean", sender_id)
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass
                if messaging_event.get("optin"):  # optin confirmation
                    pass
                if messaging_event.get("postback"):
                    # user clicked/tapped "postback" button in earlier message
                    pass
    return "ok", 200


def get_payload(message):
    pay = None
    if "quick_replies" in message.keys():
        pay = message['quick_replies']
    return pay


def parse_payload(payload):
    p = payload.split(",")
    state = p[0].split(":")[1]
    value = p[1].splitt(":")[1]
    return (state, value)


def create_payload(state, value):
    return "state:{},value:{}".format(state, value)


def determine_player(user):
    pass


def update_payload(user, message_text, payload, callback):
    pass

def figure_out(user, message_text):
    pass

def parse_message(message, callback, sender_id):
    message = message.lower()
    basic_response(message, callback, sender_id)


def basic_response(message, callback, sender_id):
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


def send_message(message_text, sender_id, quick_replies=[]):
    log("sending quick reply to {sender}: {text}".format(sender=sender_id,
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


def mock_callback(message_text, sender_id, quick_replies=[]):
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
