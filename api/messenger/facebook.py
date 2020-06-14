'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: The facebook messenger implementation
'''
import json
import requests
from api.logging import LOGGER
from api.message import Message, Payload, Option, StringFormatter
from api.messenger import Messenger
from api.errors import UnableToLookupUserInformation, UnableToSendMessage,\
    UnableToFindSender
from api.messenger.user import User
from api.settings.message_strings import Facebook
from api.variables import PAGE_ACCESS_TOKEN


class FacebookMessenger(Messenger):
    URL = "https://graph.facebook.com"
    VERSION = "v3.3"
    MALES = ["male", "m"]
    FIELDS = "fields=id,name,gender,email"

    def __init__(self, token):
        self.token = token
        self.headers = {"Content-Type": "application/json"}

    def lookup_user_id(self, user_id):
        """Looks up some information from facebook about the given user
        Parameters:
            user_id: the id of the user
        Returns:
            user: the user (User)
        """

        # using the messenger id try find information about them
        # this information then will be used to compare to the league info
        LOGGER.debug(
            "Trying to identify facebook id {}".format(user_id))
        url = ("{}/{}/{}?{}&access_token={}".format(
            FacebookMessenger.URL,
            FacebookMessenger.VERSION,
            user_id,
            FacebookMessenger.FIELDS,
            PAGE_ACCESS_TOKEN))
        request_response = requests.get(url)

        # an unsuccessful request would most likely be due to an invalid token
        if request_response.status_code != 200:
            LOGGER.critical("Facebook services not available")
            LOGGER.critical(str(request_response.json()))
            error_message = "Facebook services not available"
            raise UnableToLookupUserInformation(error_message)

        # now we know the person's facebook name and hopefully some other info
        data = request_response.json()
        LOGGER.debug("Data from looking up user" + str(data))
        name = data['name']
        email = data.get("email", None)
        gender = None
        if "gender" in data.keys():
            gender = ("m"
                      if data["gender"].lower() in FacebookMessenger.MALES
                      else "f")

        # return an object with the information found by the Facebook
        user = User(user_id, name=name, email=email, gender=gender)
        return user

    def send_message(self, message):
        """Sends the given message.
        Parameters:
            message: the message to send (Message)
        """
        if message.get_payload() is None and message.get_message() is not None:
            self._send_message(message.get_message(), message.get_sender_id())
        if message.get_payload() is not None:
            self._send_payload(message)

    def parse_response(self, response):
        """Parse the message from the response given by the messenger.
        Parameters:
            response: response object (dependent upon messenger)
        Returns:
            message: the message parsed from the response (Message)
        """

        sender_id = (None
                     if response.get("sender") is None
                     else response["sender"]["id"])
        if sender_id is None:
            LOGGER.error("Unable to get sender id")
            LOGGER.error(str(response))
            raise UnableToFindSender("Unable to get sender id")

        LOGGER.debug(response)
        # assume both the payload and message text are None
        payload = None
        message_text = None
        if "postback" in response.keys():
            if "payload" in response["postback"].keys():
                temp = response["postback"]
                data = StringFormatter(temp.get("payload", None))
                option = Option(temp.get("title", None), data)
                payload = Payload(payload_type=Payload.BUTTON_TYPE,
                                  options=[option])
        elif "message" in response.keys():
            if "text" in response["message"].keys():
                message_text = response["message"]["text"]
            if "quick_reply" in response["message"].keys():
                if "payload" in response["message"]["quick_reply"].keys():
                    quick_reply = response['message']['quick_reply']
                    message_text = quick_reply['payload']

        if response.get("recipient"):
            recipient_id = response["recipient"]["id"]
        return Message(sender_id,
                       recipient_id=recipient_id,
                       message=message_text,
                       payload=payload)

    def _send_message(self, message_text, sender_id):
        """Sends the given message to the given id"""
        message_data = {
            "recipient": {"id": sender_id},
            "message": {"text": message_text}
        }
        self._send_data(message_data)

    def _send_payload(self, message):
        """Sends the given payload with the message as the title
        Parameters:
            message: the message object (Message)
        """
        if message.get_payload().is_button_reply():
            self._send_buttons(message)
        elif message.get_payload().is_quick_reply():
            quick_replies = message.get_payload().get_payload_response()
            message_data = {"recipient":
                            {"id": message.get_sender_id()},
                            "message": {
                                "text": message.get_message(),
                                "quick_replies": quick_replies}}
            self._send_data(message_data)

    def _send_buttons(self, message):
        """Sends the buttons
        Parameters:
            message: where each option is a button response (Message)
        """
        buttons = message.get_payload().get_payload_response()
        if len(buttons) <= 0:
            self._send_message(message.get_message() +
                               " \n " + Facebook.NO_OPTIONS_AVAILABLE)
        elif len(buttons) <= 3:
            data = {"recipient": {
                "id": message.get_sender_id()},
                "message": {
                "attachment": {
                    "type": "template",
                            "payload": {
                                "template_type": "button",
                                "text": message.get_message(),
                                "buttons": buttons}
                }
            }
            }
            self._send_data(data)
        elif len(buttons) <= 29:
            self._send_buttons_aux(message.get_sender_id(),
                                   message,
                                   buttons)
        else:
            # split into two messages
            m1 = Message(message.get_sender_id(),
                         message=message.get_message(), payload=buttons[0:29])
            m2 = Message(message.get_sender_id(),
                         message=Facebook.EVEN_MORE_OPTIONS,
                         payload=buttons[29:])
            self._send_buttons(m1)
            self._send_buttons(m2)

    def _send_buttons_aux(self, sender_id, message, buttons):

        message_text = Facebook.SCROLL_FOR_MORE_OPTIONS.value
        if message is not None:
            message_text += " \n " + message.get_message()
        elements = [
            {"title": "Friendly Sports Bot",
             "subtitle": message_text,
             "buttons": buttons[0:3]
             }
        ]
        i = 3
        while i < len(buttons):
            elements.append({"title": "More Options",
                             "buttons": buttons[i: i + 3]})
            i += 3
        data = {"recipient": {"id": sender_id},
                "message": {
            "attachment": {
                "type": "template",
                        "payload": {
                            "template_type": "generic",
                            "elements": elements
                        }
            }
        }
        }
        self._send_data(data)

    def _send_data(self, data):
        """Sends the data response
        Parameters:
            data: the data to send back (message, quick replies, buttons)
        """
        params = {"access_token": self.token}
        LOGGER.debug(data)
        data = json.dumps(data)
        request_url = "{}/{}/me/messages".format(self.URL, self.VERSION)
        request_response = requests.post(request_url,
                                         headers=self.headers,
                                         data=data,
                                         params=params)
        if request_response.status_code != 200:
            LOGGER.critical("Unable to send response using Facebook")
            LOGGER.error(str(request_response.json()))
            raise UnableToSendMessage("Unable to send message using Facebook")
