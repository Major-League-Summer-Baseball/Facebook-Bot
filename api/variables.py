'''
Created on May 3, 2017

@author: d6fraser
'''
from base64 import b64encode
import os
SUBSCRIPTION_TIME_RANGE = os.environ.get("SUBSCRIPTION_TIME_RANGE", 15)
URL = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/mlsb")
BASEURL = os.environ.get("PLATFORM",
                         "http://localhost:5000")
ADMIN = os.environ.get("ADMIN", "admin")
PASSWORD = os.environ.get("PASSWORD", "password")
PAGE_TOKEN_DEFAULT = ("EAABrxzY0HL4BADKTzPtw3xmcgxDZBjrmYxQPcZAYhLpAgxJga2fM" +
                      "TiSDvffHY3WmoICxgCZA1VYKDjycOwkBmhlYoYZA720SqupxFYEDH" +
                      "ZC5AzQztm1iAbGyFIzTYMzXZAq01I6jqHxLd1gIJbAEZAnDLcu5w2" +
                      "vtJh2USjBUXlzsiU7GlqSj9OW")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", None)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", None)
SECRET_CONVENOR_CODE = os.environ.get("CONVENOR_CODE", "⬆️⬆️⬇️⬇️⬅️⬅️➡️➡️BA")
HEADERS = {
    'Authorization': 'Basic %s' % b64encode(bytes(ADMIN + ':' +
                                                  PASSWORD, "utf-8")
                                            ).decode("ascii")
}
