'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: homescreen, displays the base options and handles selection of option
'''
from api.logging import LOGGER
from api.message import Option, Payload, Message, StringFormatter,\
    LeagueLeaderFormatter, EventFormatter, GameFormatter
from api.helper import random_emoji, random_fun_comment, get_this_year
from api.settings.message_strings import MAIN_MENU_EVENTS_TITLE,\
    MAIN_MENU_FUN_TITLE, MAIN_MENU_HR_TITLE, MAIN_MENU_SS_TITLE,\
    MAIN_MENU_UPCOMING_GAMES_TITLE, MAIN_MENU_LEAGUE_LEADERS_TITLE,\
    MAIN_MENU_SUBMIT_SCORE_TITLE, HR_TITLE, SS_TITLE, FUN_TOTAL_COMMENT,\
    NOGAMES_COMMENT, NOT_CAPTAIN_COMMENT, NO_UPCOMING_GAMES_COMMENT
from api.settings.action_keys import SUBMIT_SCORE_KEY
from api.actions import ActionInterface, ActionState


class HomescreenAction(ActionInterface):
    """
        The action when on the homescreen

        Notes:
            This is the main entry to the bot
                (most actions will be initiated by this action)
            It should handle basic one off tasks like display games and other
            information pulled from website
    """
    UPCOMING_GAMES_PAYLOAD = StringFormatter("upcoming")
    LEAGUE_LEADERS_PAYLOAD = StringFormatter("leaders")
    EVENTS_PAYLOAD = StringFormatter("events")
    FUN_PAYLOAD = StringFormatter("fun")
    SUBMIT_SCORE_PAYLOAD = StringFormatter("score")

    def process(self, action_map, buttons=True):
        """Process the homescreen message"""
        self.action_map = action_map
        self.buttons = buttons
        messenger_id = self.message.get_sender_id()
        player = self.database.get_player(messenger_id)

        # if they sent a message try to process it
        action_taken = False
        print(str(self.message.get_message()) +
              " " + str(self.message.get_payload()))
        if self.message.get_message() is not None:
            result = self.parse_message(self.message.get_message(),
                                        self.message.get_sender_id(),
                                        self.message.get_recipient_id(),
                                        player)
            action_taken = action_taken or result

        # if they sent a payload try to process it
        if self.message.get_payload() is not None:
            for option in self.message.get_payload().get_options():
                result = self.parse_message(option.get_data().format(),
                                            self.message.get_sender_id(),
                                            self.message.get_recipient_id(),
                                            player)
                action_taken = action_taken or result
        LOGGER.debug("Action taken on home screen: {}".format(action_taken))
        if not action_taken:
            self.display_base_options(player)

    def parse_message(self, message_string, sender_id, recipient_id, player):
        """Parses the message and performs an action if needed

            Parameters:
                message_string: the message received
                    either message or payload value (Str)
                sender_id: the id of the sender (Str)
                recipient_id: the id of the recipient (Str)
                player: the player associated with the sender (Player)
            Returns:
                None if no action was taken
                true if some action was taken
        """
        action_taken = True
        message_string = message_string.lower()
        if (message_string in
            [HomescreenAction.UPCOMING_GAMES_PAYLOAD.format().lower(),
             MAIN_MENU_UPCOMING_GAMES_TITLE.lower()]):
            self.display_upcoming_games(player)
        elif (message_string in
              [HomescreenAction.LEAGUE_LEADERS_PAYLOAD.format().lower(),
               MAIN_MENU_LEAGUE_LEADERS_TITLE.lower()]):
            self.display_league_leaders()
        elif (message_string in
              [HomescreenAction.EVENTS_PAYLOAD.format().lower(),
               MAIN_MENU_EVENTS_TITLE.lower()]):
            self.display_events()
        elif (message_string in
              [HomescreenAction.FUN_PAYLOAD.format().lower(),
               MAIN_MENU_FUN_TITLE.lower()]):
            self.display_fun_meter()
        elif (message_string in
              [HomescreenAction.SUBMIT_SCORE_PAYLOAD.format().lower(),
               MAIN_MENU_FUN_TITLE.lower()]):
            if player.is_captain():
                self.intiate_action(self.action_map,
                                    SUBMIT_SCORE_KEY, player)
            else:
                message = Message(sender_id,
                                  recipient_id=recipient_id,
                                  message=NOT_CAPTAIN_COMMENT)
                self.messenger.send_message(message)
        else:
            action_taken = False
        return action_taken

    def display_base_options(self, player):
        """Display the base options"""

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

        # determine if ussing buttons of quick reply
        payload_type = Payload.BUTTON_TYPE
        if not self.buttons:
            payload_type = Payload.QUICK_REPLY_TYPE

        # create the payload with all the options
        payload = Payload(payload_type=payload_type, options=options)

        # create the message and send it
        message = Message(self.message.get_sender_id(),
                          recipient_id=self.message.get_recipient_id(),
                          payload=payload)
        self.messenger.send_message(message)

    def display_events(self):
        """Display the league events"""
        events = self.platform.get_events()
        event_messages = []
        for event, date in events.items():
            event_messages.append(EventFormatter(
                {"event": event, "date": date}).format())

        # create the message and send it
        message = Message(self.message.get_sender_id(),
                          recipient_id=self.message.get_recipient_id(),
                          message="\n".join(event_messages))
        self.messenger.send_message(message)

    def display_upcoming_games(self, player):
        """Display the upcoming games for the user"""
        games = self.platform.get_upcoming_games(player)
        game_entries = []
        for game in games:
            game_entries.append(GameFormatter(game).format())
        if len(games) == 0:
            message = Message(self.message.get_sender_id(),
                              recipient_id=self.message.get_recipient_id(),
                              message=NO_UPCOMING_GAMES_COMMENT)
            self.messenger.send_message(message)
        else:
            message = Message(self.message.get_sender_id(),
                              recipient_id=self.message.get_recipient_id(),
                              message="\n\n".join(game_entries))
            self.messenger.send_message(message)

    def display_league_leaders(self):
        """Display the league leaders"""

        # get the league leaders from platform
        hr_leaders = self.platform.league_leaders("hr")
        ss_leaders = self.platform.league_leaders("ss")

        # create message for each type of leader
        hr_leaders_message = [HR_TITLE]
        ss_leaders_message = [SS_TITLE]
        for leader in hr_leaders:
            hr_leaders_message.append(LeagueLeaderFormatter(leader).format())
        for leader in ss_leaders:
            ss_leaders_message.append(LeagueLeaderFormatter(leader).format())
        LOGGER.debug(str(hr_leaders) + " and " + str(ss_leaders))
        # create a message for each type of leader and send both of them
        m1 = Message(self.message.get_sender_id(),
                     recipient_id=self.message.get_recipient_id(),
                     message="\n".join(ss_leaders_message))
        m2 = Message(self.message.get_sender_id(),
                     recipient_id=self.message.get_recipient_id(),
                     message="\n".join(hr_leaders_message))
        self.messenger.send_message(m1)
        self.messenger.send_message(m2)

    def display_fun_meter(self):
        """Display the fun meter"""
        fun = self.platform.fun_meter()
        count = 0
        this_year = get_this_year()
        for element in fun:
            if element['year'] == this_year:
                count = element['count']
        message = count * random_emoji()
        message += "\n" + random_fun_comment()
        message += "\n" + FUN_TOTAL_COMMENT.format(count)
        m = Message(self.message.get_sender_id(),
                    recipient_id=self.message.get_recipient_id(),
                    message=message)
        self.messenger.send_message(m)
