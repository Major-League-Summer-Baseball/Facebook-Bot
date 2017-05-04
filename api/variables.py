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
PID = -1
EMAIL = -2
IGNORE = -3
BASE = 0
GAMES = 1
SCORE = 2
HOMERUNS = 3
SPECIALS = 4
REVIEW = 5
