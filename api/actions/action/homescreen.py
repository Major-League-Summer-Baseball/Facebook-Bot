'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: homescreen, displays the base options and handles selection of option
'''
from typing import List, Tuple
from api.logging import LOGGER
from api.message import Option, Payload, Message
from api.message.format import LeagueLeaderFormatter, EventFormatter,\
    GameFormatter
from api.helper import random_emoji, random_fun_comment
from api.settings.message_strings import HomescreenComments, MainMenu
from api.players.player import Player
from api.actions import ActionKey
from api.actions.action import Action
from api.variables import SECRET_CONVENOR_CODE


class Homescreen(Action):
    UPCOMING_GAMES_PAYLOAD = "upcoming"
    LEAGUE_LEADERS_PAYLOAD = "leaders"
    EVENTS_PAYLOAD = "events"
    FUN_PAYLOAD = "fun"
    SUBMIT_SCORE_PAYLOAD = "score"

    def process(self, player: Player, message: Message,
                buttons: bool = True) -> Tuple[Player, List[Message],
                                               ActionKey]:
        """Process the action for the given player and message"""
        self.buttons = buttons
        messenger_id = message.get_sender_id()
        player = self.database.get_player(messenger_id)

        # if they sent a message try to process it
        messages = []
        next_action = None
        if message.get_message() is not None:
            (player, messages,
                next_action) = self.parse_message(player, message,
                                                  message.get_message())
        if message.get_payload() is not None:
            # if they sent a payload try to process it
            for option in message.get_payload().get_options():
                content = option.get_data()
                (player, tmp_msgs,
                    tmp_action) = self.parse_message(player, message, content)
                messages = messages + tmp_msgs
                next_action = (tmp_action
                               if tmp_action is not None else next_action)
        if len(messages) == 0 and next_action is None:
            messages = self.display_base_options(player, message)
        return (player, messages, next_action)

    def parse_message(self, player: Player, message: Message,
                      message_string: str) -> Tuple[List[Message], ActionKey]:
        """Parses the given message to determine next action and messages

        Args:
            player (Player): the player who sent the message
            message (Message): the message sent by the player
            message_string (str): the string or payload selected by the player

        Returns:
            Tuple[List[Message], ActionKey]: messages to send back
                                             and next action
        """
        message_string = message_string.lower()
        if (message_string in
            [Homescreen.UPCOMING_GAMES_PAYLOAD.lower(),
             MainMenu.UPCOMING_GAMES_TITLE.value.lower()]):
            return (player, self.display_upcoming_games(player, message), None)
        elif (message_string in
              [Homescreen.LEAGUE_LEADERS_PAYLOAD.lower(),
               MainMenu.LEAGUE_LEADERS_TITLE.value.lower()]):
            return (player, self.display_league_leaders(message), None)
        elif (message_string in
              [Homescreen.EVENTS_PAYLOAD.lower(),
               MainMenu.EVENTS_TITLE.value.lower()]):
            return (player, self.display_events(message), None)
        elif (message_string in
              [Homescreen.FUN_PAYLOAD.lower(),
               MainMenu.FUN_TITLE.value.lower()]):
            return (player, self.display_fun_meter(message), None)
        elif (message_string in
              [Homescreen.SUBMIT_SCORE_PAYLOAD.lower(),
               MainMenu.SUBMIT_SCORE_TITLE.value.lower()]):
            if player.is_captain() or player.is_convenor():
                return (player, [], ActionKey.SUBMIT_SCORE_KEY)
            else:
                content = HomescreenComments.NOT_CAPTAIN.value
                return (player, [Message(message.get_sender_id(),
                                 recipient_id=message.get_recipient_id(),
                                 message=content)], None)
        elif (message_string == SECRET_CONVENOR_CODE.lower()):
            player.make_convenor()
            convenor = HomescreenComments.WELCOME_CONVENOR.value
            return (player, [Message(message.get_sender_id(),
                             recipient_id=message.get_recipient_id(),
                             message=convenor)], None)
        return (player, [], None)

    def display_base_options(self, player: Player,
                             message: Message) -> List[Message]:
        """Returns a list of options that form homescreen

        Args:
            player (Player): the player who sent the message
            message (Message): the message the player sent

        Returns:
            List[Message]: a list of options (either buttons or quick type)
        """
        # create the option
        options = [Option(MainMenu.UPCOMING_GAMES_TITLE.value,
                          Homescreen.UPCOMING_GAMES_PAYLOAD),
                   Option(MainMenu.LEAGUE_LEADERS_TITLE.value,
                          Homescreen.LEAGUE_LEADERS_PAYLOAD),
                   Option(MainMenu.EVENTS_TITLE.value,
                          Homescreen.EVENTS_PAYLOAD),
                   Option(MainMenu.FUN_TITLE.value,
                          Homescreen.FUN_PAYLOAD)]

        # if captain then need option for submitting score
        if player.is_captain() or player.is_convenor():
            options.append(
                Option(MainMenu.SUBMIT_SCORE_TITLE.value,
                       Homescreen.SUBMIT_SCORE_PAYLOAD))

        # determine if using buttons of quick reply
        payload_type = Payload.BUTTON_TYPE
        if not self.buttons:
            payload_type = Payload.QUICK_REPLY_TYPE

        # create the payload with all the options
        payload = Payload(payload_type=payload_type, options=options)

        # create the message and send it
        return [Message(message.get_sender_id(),
                        recipient_id=message.get_recipient_id(),
                        message=HomescreenComments.OPTION_PROMPT.value,
                        payload=payload)]

    def display_events(self, message: Message) -> List[Message]:
        """Returns a list of messages representing the upcoming events

        Args:
            message (Message): the message received asking for league events

        Returns:
            List[Message]: a message with the event details like date
        """
        events = self.platform.get_events()
        event_messages = []
        for event, date in events.items():
            event_messages.append(EventFormatter(
                {"event": event, "date": date}).format())

        # create the message and send it
        return [Message(message.get_sender_id(),
                        recipient_id=message.get_recipient_id(),
                        message="\n".join(event_messages))]

    def display_upcoming_games(self, player: Player,
                               message: Message) -> List[Message]:
        """Returns a list of messages representing the upcoming games

        Args:
            player (Player): the player to display games for
            message (Message): the message received asking for upcoming games

        Returns:
            List[Message]: a message with the upcoming games
        """
        games = self.platform.get_upcoming_games(player)
        game_entries = []
        for game in games:
            game_entries.append(GameFormatter(game).format())
        if len(games) == 0:
            content = HomescreenComments.NO_UPCOMING_GAMES.value
            message = Message(message.get_sender_id(),
                              recipient_id=message.get_recipient_id(),
                              message=content)
            return [message]
        else:
            message = Message(message.get_sender_id(),
                              recipient_id=message.get_recipient_id(),
                              message="\n\n".join(game_entries))
            return [message]

    def display_league_leaders(self, message: Message) -> List[Message]:
        """Returns a list of messages representing the league leaders

        Args:
            message (Message): the message asking for the league leaders

        Returns:
            List[Message]: the league leaders message
        """

        # get the league leaders from platform
        hr_leaders = self.platform.league_leaders("hr")
        ss_leaders = self.platform.league_leaders("ss")

        # create message for each type of leader
        hr_leaders_message = [MainMenu.HR_TITLE.value]
        ss_leaders_message = [MainMenu.SS_TITLE.value]
        for leader in hr_leaders:
            hr_leaders_message.append(LeagueLeaderFormatter(leader).format())
        for leader in ss_leaders:
            ss_leaders_message.append(LeagueLeaderFormatter(leader).format())
        LOGGER.debug(str(hr_leaders) + " and " + str(ss_leaders))
        # create a message for each type of leader and send both of them
        m1 = Message(message.get_sender_id(),
                     recipient_id=message.get_recipient_id(),
                     message="\n".join(ss_leaders_message))
        m2 = Message(message.get_sender_id(),
                     recipient_id=message.get_recipient_id(),
                     message="\n".join(hr_leaders_message))
        return [m1, m2]

    def display_fun_meter(self, message: Message) -> List[Message]:
        """Returns a list of messages for the fun meter

        Args:
            message (Message): the message received asking for the fun meter

        Returns:
            List[Message]: the fun meter message
        """
        fun = self.platform.fun_meter()
        fun_count = 0 if len(fun) < 1 else fun[0].get("count", 0)
        fun_message = HomescreenComments.FUN_TOTAL.value
        content = "\n".join([fun_count * random_emoji(),
                             random_fun_comment(),
                             fun_message.format(fun_count)])
        return [Message(message.get_sender_id(),
                        recipient_id=message.get_recipient_id(),
                        message=content)]
