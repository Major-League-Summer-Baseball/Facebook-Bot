'''
Name: Dallas Fraser
Date: 2017-05-03
Project: Facebook Bot
Purpose: To create an application to act as an api for the database
'''
import os
from api import app
if __name__ == "__main__":
    start = False
    port = os.get("BOT_PORT", 5000)
    while not start and port < 5010:
        try:
            app.run(debug=True, port=port)
            start = True
        except OSError as e:
            print(e)
            print(f"Port:{port} taken trying another")
            port += 1
