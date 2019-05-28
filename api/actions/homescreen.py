'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: homescreen, displays the base options and handles selection of option
'''
from api.message import Option, Payload, Message
from api.message import NormalStringData as Formatter
from api.settings.message_strings import MAIN_MENU_EVENTS_TITLE,\
    MAIN_MENU_FUN_TITLE, MAIN_MENU_HR_TITLE, MAIN_MENU_SS_TITLE,\
    MAIN_MENU_UPCOMING_GAMES_TITLE, MAIN_MENU_LEAGUE_LEADERS_TITLE,\
    MAIN_MENU_SUBMIT_SCORE_TITLE
from api.actions import ActionInterface


class HomescreenAction(ActionInterface):
    UPCOMING_GAMES_PAYLOAD = Formatter("upcoming")
    LEAGUE_LEADERS_PAYLOAD = Formatter("leaders")
    EVENTS_PAYLOAD = Formatter("events")
    FUN_PAYLOAD = Formatter("fun")
    SUBMIT_SCORE_PAYLOAD = Formatter("score")

    def process(self, action_map, buttons=True):
        self.action_map = action_map
        self.buttons = buttons
        messenger_id = self.message.get_sender_id()
        player = self.database.get_player(messenger_id)
        self.display_base_options(player)

    def display_base_options(self, player):

        # create the option
        options = [Option(MAIN_MENU_UPCOMING_GAMES_TITLE,
                          HomescreenAction.UPCOMING_GAMES_PAYLOAD),
                   Option(MAIN_MENU_LEAGUE_LEADERS_TITLE,
                          HomescreenAction.LEAGUE_LEADERS_PAYLOAD),
                   Option(MAIN_MENU_EVENTS_TITLE,
                          HomescreenAction.EVENTS_PAYLOAD),
                   Option(MAIN_MENU_FUN_TITLE,
                          HomescreenAction.FUN_PAYLOAD)]

        # if captain then need option for submitting score
        if player.is_captain() or player.is_convenor():
            options.append(
                Option(MAIN_MENU_SUBMIT_SCORE_TITLE,
                       HomescreenAction.SUBMIT_SCORE_PAYLOAD))

        payload_type = Payload.BUTTON_TYPE
        if not self.buttons:
            payload_type = Payload.QUICK_REPLY_TYPE
        payload = Payload(payload_type=payload_type, options=options)
        sender_id = self.message.get_sender_id()
        recipient_id = self.message.get_recipient_id()
        message = Message(sender_id,
                          recipient_id=recipient_id,
                          payload=payload)
        self.messenger.send_message(message)
