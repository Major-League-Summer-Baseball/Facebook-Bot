'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds the strings used
'''
from enum import Enum


ASK_FOR_EMAIL = "What's your email associated with the league"
EMAIL_NOT_FOUND = "The given email was not found, try another"
LOCKED_OUT = "You have maxed out your tries, try contacting a convenor"
IMPOSTER = ("Your player account is already used by another user,\n" +
            "contact convenors to resolve")
WELCOME_LEAGUE = "Welcome to the league: {}"
ACKNOWLEDGE_CONVENOR = ("Sounds like you are convenor so upgrading you to\n" +
                        " with this you will be able to submit scores for\n" +
                        "any team and send league updates to the whole league")
ACKNOWLEDGE_CAPTAIN = ("Sounds like you the captain of the team\n" +
                       "you will be able to submit scores for your team")
PART_OF_TEAM = ("It appears you are on: {}\n" +
                "you are now subscribed to the team and will get updates")


class Registration(Enum):
    """Strings related to registering with the bot and welcoming new users"""
    EMAIL_PROMPT = "What's your email associated with the league"
    EMAIL_NOT_FOUND = "The given email was not found, try another"
    LOCKED_OUT = "You have maxed out your tries, try contacting a convenor"
    IMPOSTER = IMPOSTER
    WELCOME = "Welcome to the league: {}"
    WELCOME_CONVENOR = ACKNOWLEDGE_CONVENOR
    WELCOME_CAPTAIN = ACKNOWLEDGE_CAPTAIN
    ON_TEAM = PART_OF_TEAM


class MainMenu(Enum):
    """Strings related to the main menu titles"""
    UPCOMING_GAMES_TITLE = "Upcoming Games"
    LEAGUE_LEADERS_TITLE = "League Leaders"
    EVENTS_TITLE = "Events"
    FUN_TITLE = "Fun Meter"
    SUBMIT_SCORE_TITLE = "Submit Score"
    HR_TITLE = "HR Leaders"
    SS_TITLE = "SS Leaders"


class HomescreenComments(Enum):
    """Strings related to the homescreen"""
    OPTION_PROMPT = "What would you like to do today?"
    FUN_TOTAL = "Total fun: {}"
    NO_GAMES = "No upcoming games"
    NOT_CAPTAIN = "Appears you are not a captain"
    NO_UPCOMING_GAMES = "There are no upcoming games"


MAIN_MENU_UPCOMING_GAMES_TITLE = "Upcoming Games"
MAIN_MENU_LEAGUE_LEADERS_TITLE = "League Leaders"
MAIN_MENU_EVENTS_TITLE = "Events"
MAIN_MENU_FUN_TITLE = "Fun Meter"
MAIN_MENU_SUBMIT_SCORE_TITLE = "Submit Score"
MAIN_MENU_HR_TITLE = "HR Leaders"
MAIN_MENU_SS_TITLE = "SS Leaders"

# titles used on homescreen
EVENTS_TITLE = "Events"
FUN_TITLE = "Fun Meter"
HR_TITLE = "HR Leaders:"
SS_TITLE = "SS Leaders:"

# Comments used on homescreen
HOMESCREEN_OPTIONS_PROMPT = "What would you like to do today?"
FUN_TOTAL_COMMENT = "Total fun: {}"
NO_GAMES_COMMENT = "No upcoming games"
NOT_CAPTAIN_COMMENT = "Appears you are not a captain"
NO_UPCOMING_GAMES_COMMENT = "There are no upcoming games"
INTROS = ["What do you want?",
          "Well, hello there",
          "DAM Daniel!!, how you doing?",
          "Next one is on me",
          "Wet and wild is my name"
          ]
SASSY_COMMENT = ["WOW, {} hit hr(s), wind must have been blowing today",
                 "{} finally bought that corked bat",
                 "League will be looking into this one: {}",
                 "Has {} been at the gym lately",
                 "Let me guess, {} is a lefty on WP2",
                 "Good for {}"
                 ]
COMPLIMENT = ["{} is my favourite player",
              "Awesome, {} might lead the league one day",
              "Tell {} to keep it up",
              "Fuck ya {}",
              "{} could be in the all-star game"]
EMOJI = [u'\U0001f37a',
         u'\U0001f600',
         u'\U0001f377',
         u'\U0001f382',
         u'\u26a0',
         u'\u26be',
         u'\U0001f649',
         u'\U0001f37a',
         u'\U0001f37b',
         u'\U0001f942'
         ]
FUN_COMMENT = ["",
               "",
               "What fun",
               "Are we having too much fun?"]


class ScoreSubmission(Enum):
    """Holds all the string related to submiting a score"""
    NO_GAMES = "There are no games to submit scores for"
    SELECT_TEAM = "Which team would you like to select team for"
    SELECT_GAME = "What game would you like to submit a score for"
    TEXT_METHOD = "just a message"
    BUTTON_METHOD = "using buttons"
    UNRECOGNIZED_GAME = "Sorry, did not recognize the game"
    UNRECOGNIZED_TEAM = "Sorry, did not recognize the team"
    NOT_CAPTAIN = "Appears you are not a captain"
    CANCEL = "Cancel"


class Facebook(Enum):
    """Holds all the strings only related to Facebook messaging"""
    NO_OPTIONS_AVAILABLE = "There are no options available"
    SCROLL_FOR_MORE_OPTIONS = "Scroll right for more options"
    EVEN_MORE_OPTIONS = " Even more options"


# comments on Submit score
NO_GAME_TO_SUBMIT = "There are no games to submit scores for"
SELECT_TEAM_TO_SUBMIT_FOR_COMMENT = (
    "Which team would you like to select team for")
SELECT_GAME_TO_SUBMIT_COMMENT = (
    "What game would you like to submit a score for")
SUBMIT_SCORE_USING_BUTTONS_TITLE = "using buttons"
SUBMIT_SCORE_BY_TEXT_TITLE = "just a message"
PLEASE_USE_BUTTONS = "Please respond using a button"
UNRECOGNIZED_GAME = "Sorry, did not recognize the game"
UNRECOGNIZED_TEAM = "Sorry, did not recognize the team"
