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
from flask import Flask, request
from random import randint
from apis.trump import trump_response
from apis.memes import meme_response
app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    try:
                        parse_message(message_text, send_message, sender_id)
                        parse_meme(message_text, send_meme, id)
                    except Exception as e:
                        print(str(e))
                        send_message("Not sure what you mean", recipient_id)
                    
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass
                if messaging_event.get("optin"):  # optin confirmation
                    pass
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass
    return "ok", 200

def parse_message(message, callback, id):
    message = message.lower()
    basic_response(message, callback, id)
    trump_response(message, callback, id)

def parse_meme(message, callback, id):
    message = message.lower()
    meme_response(message, callback, id)

def basic_response(message, callback, id):
    if re.search("who(\s?)('s)*the(\s?)best", message):
        response = "Obviously the Maple Leafs"
        callback(response.strip(), id)
    elif re.search(r"would(\s?)you(\s?)rather", message):
        message = re.sub(r'[^a-zA-Z0-9_\s]', '', message)
        clause = message.split("rather")[1]
        proposition = clause.split(" or ")
        pick_proposition = proposition[randint(0, len(proposition) - 1)]
        response = pick_proposition
        callback(response.strip(), id)
    
def send_message(message_text, recipient_id):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_meme(message_text, meme, recipient_id):
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text,
             "attachment":{
                            "type":"image",
                            "payload":{
                                "url":meme,
                            "is_reusable":True
                            }
                    }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
    
def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
