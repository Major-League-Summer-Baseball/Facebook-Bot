'''
@author: Dallas Fraser
@date: 2016-11-26
@organization: Fun
@summary: Holds the app
'''
import traceback
from typing import Tuple
from flask import Flask, request
from flask_pymongo import PyMongo
from api.logging import LOGGER
from api.messenger.facebook import FacebookMessenger
from api.mlsb.platform import PlatformService
from api.database.mongo import DatabaseService
from api.actions.map import ACTION_MAP
from api.actions.action_processor import ActionProcessor
from api.variables import URL, BASEURL, PAGE_ACCESS_TOKEN, HEADERS,\
    VERIFY_TOKEN

app = Flask(__name__)
app.config['MONGO_URI'] = URL
app.config.from_object(__name__)
mongo = PyMongo(app)

# these objects use for multiple requests
MESSENGER = FacebookMessenger(PAGE_ACCESS_TOKEN)
PLATFORM = PlatformService(HEADERS, BASEURL)
DATABASE = DatabaseService(mongo)
ACTION_PROCESSOR = ActionProcessor(DATABASE, PLATFORM, MESSENGER)


@app.route('/', methods=['GET'])
def verify() -> Tuple[str, int]:
    """Used to verify the bit app with the messenger.

    Returns:
        Tuple[str, int]: a success message and http status code
    """
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if (request.args.get("hub.mode") == "subscribe" and
            request.args.get("hub.challenge")):
        if (not request.args.get("hub.verify_token") == VERIFY_TOKEN):
            token = request.args.get("hub.verify_token")
            LOGGER.critical(f"Incorrect verify token: {token}")
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook() -> Tuple[str, int]:
    """The web hook for dealing with messages.

    Returns:
        Tuple[str, int]: the http message and http status code
    """
    # endpoint for processing incoming messaging events
    data = request.get_json()
    # you may not want to log every incoming message in production,
    # but it's good for testing
    LOGGER.debug(f"Incoming message: {data}")
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                use_action_mapper(messaging_event)
    return "ok", 200


def use_action_mapper(message_event: dict) -> None:
    """Use the action mapper to respond to the given message

    Args:
        message_event (dict): a message from Facebook
    """
    try:
        message = MESSENGER.parse_response(message_event)
        ACTION_PROCESSOR.process(message, ACTION_MAP)
    except Exception:
        LOGGER.critical(str(Exception))
        traceback.print_exc()
