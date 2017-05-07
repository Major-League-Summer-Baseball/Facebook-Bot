'''
Created on May 3, 2017

@author: d6fraser
'''
from base64 import b64encode
import os
if os.environ.get("LOCAL", "TRUE") == "FALSE":
    URL = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/rest")
    BASEURL = os.environ.get("PLATFORM",
                             "http://mlsb-dallas-branch.herokuapp.com/")
    ADMIN = os.environ.get("ADMIN", "mlsb-scores")
    PASSWORD = os.environ.get("PASSWORD", "fun")
    PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN",
                                       "EAABrxzY0HL4BADKTzPtw3xmcgxDZBjrmYxQPcZAYhLpAgxJga2fMTiSDvffHY3WmoICxgCZA1VYKDjycOwkBmhlYoYZA720SqupxFYEDHZC5AzQztm1iAbGyFIzTYMzXZAq01I6jqHxLd1gIJbAEZAnDLcu5w2vtJh2USjBUXlzsiU7GlqSj9OW")
    VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "908sdamnsclk2190KSDJI")
else:
    from api.credentials import BASEURL, URL, ADMIN, PASSWORD,\
                                PAGE_ACCESS_TOKEN, VERIFY_TOKEN
HEADERS = {
    'Authorization': 'Basic %s' % b64encode(bytes(ADMIN + ':' +
                                                  PASSWORD, "utf-8")
                                            ).decode("ascii")
}
# main menu title
UPCOMING_TITLE = "Upcoming Games"
LEAGUE_LEADERS_TITLE = "League Leaders"
EVENTS_TITLE = "Events"
FUN_TITLE = "Fun Meter"
SUBMIT_SCORE_TITLE = "Submit Score"
SUBMIT_TITLE = "Submit"
HR_TITLE = "HR Leaders:"
SS_TITLE = "SS Leaders:"
# random comments
FUN_TOTAL_COMMENT = "Total fun: {}"
WELCOME_LEAGUE = "Welcome to the league: {}"
PICKBATTER_COMMENT = "'Pick a batter \n who hit a {}:'"
HELP_COMMENT = "If you ever need help just type: HELP"
DONE_COMMENT = "Done"
CANCEL_COMMENT = "Cancel"
NOGAMES_COMMENT = "No upcoming games"
PICKGAME_COMMENT = "Pick a game to submit score for"
FALLBACK = "Try sending an email, if you have a question the bot cant handle"
NO_EMAIL_GIVEN_COMMENT = "No email was given, (looking for @)"
ASK_EMAIL_COMMENT = "What's your email associated with the league"
SCORE_COMMENT = "How many runs did you score? \n Just type a number Eg. 1"
HIT_NUM_COMMENT = "How many {}  did {}  hit?"
CANCELING_COMMENT = "Canceling"
USE_QUICK_REPLIES_COMMENT = "Need to use the quick replies"
NEED_GAME_NUMBER_COMMENT = "Couldnt find the game number in repsonse"
GAME_SUBMITTED_COMMENT = "Game submitted"
# error comments
INVALID_GAME_COMMENT = "The game was not valid"
INVALID_BATTER_COMMENT = "Batter was not on teamroster"
IDENTITY_STOLEN_COMMENT = "Someone already appears to be you, contact admin"
NOT_FOUND_COMMENT = "Looks like your email is not recorded, contact admin"
TOO_MANY_HR_COMMENT = "More hr(s) than runs scored"
DIDNT_UNDERSTAND_COMMENT = "Didn't understand how many"
# help comments
BASE_HELP_OPTIONS = ["Upcoming games: Find out what games you have upcoming",
                     "League leaders: who leading the league",
                     "Events: what are the events for this year",
                     "Fun meter: how much fun has this summer been",
                     "Submit score: if you are captain submit a score"]
HR_BAT_HELP_COMMENT = "Who hit a {}, \n if you dont see a player contact admin"
SS_BAT_HELP_COMMENT = "Who hit a SS (only females), \n if you don't see a player contact admin"
HR_NUM_HELP_COMMENT = "Select a batter who hit a homerun"
SS_NUM_HELP_COMMENT = "Pick a girl who hit the ball to the grass in the air (no bounce)"
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
         u'\U0001f649']
FUN_COMMENT = ["",
               "",
               "What fun",
               "Are we having too fun?"]
# the various states of the bot
# these are not displayed to the user
IGNORE = "Not part of league"
PID = "Finding player id"
EMAIL = "Ask for email"
BASE = "Display base options"
GAMES = "Asked for captain to select game"
SCORE = "Asked for score"
HR_BAT = "Asked for homerun batter"
HR_NUM = "Asked for number of homeruns"
SS_BAT = "Asked for ss batter"
SS_NUM = "Asked for number of ss"
REVIEW = "Reviewing game submit"
UPCOMING = "Upcoming events"
LEADERS = "League leaders"
EVENTS = "Events"
FUN = "Fun meter"
CANCEL = "Cancel"
