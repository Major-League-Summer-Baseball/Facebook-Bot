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
FALLBACK = "Try sending an email, if you have a question the bot cant handle"
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
IGNORE = -3
PID = IGNORE + 1
EMAIL = PID + 1
BASE = EMAIL + 1
GAMES = BASE + 1
SCORE = GAMES + 1
HR_BAT = SCORE + 1
HR_NUM = HR_BAT + 1
SS_BAT = HR_NUM + 1
SS_NUM = SS_BAT + 1
REVIEW = SS_NUM + 1
UPCOMING = REVIEW + 1
LEADERS = UPCOMING + 1
EVENTS = LEADERS + 1
FUN = EVENTS + 1
CANCEL = FUN + 1
