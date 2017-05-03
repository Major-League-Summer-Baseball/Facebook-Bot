'''
Created on May 3, 2017

@author: d6fraser
'''
import requests
from app import app, mongo, log, BASEURL, HEADERS
from states import INITIAL, SCORE


def get_user(identity):
    created = False
    user = mongo.db.users.find_one({'fid': identity})
    if user is None:
        created = True
        # get the player's id
        submission = user['data']
        r = requests.post(BASEURL + "kik/submit_score",
                      params=submission,
                      headers=HEADERS)
        log(r.json())
        mongo.db.users.insert({"fid": identity,
                               "state": INITIAL,
                               "pid": 
                               "data": {}
                               })
        user = mongo.db.users.find_one({'fid': identity})
    return (user, created)


def get_games(user):
    

def submit_score(user):
    submission = user['data']
    r = requests.post(BASEURL + "kik/submit_score",
                      params=submission,
                      headers=HEADERS)
    log(r.json())
    # remove the data since not relevant
    user['data'] = {}
    mongo.db.users.save({"_id": user.inserted_id}, user)
    return


def add_game(user, game_id):
    user['data'] = {"game_id": game_id,
                    "score": 0,
                    "hr": [],
                    "ss": []}
    mongo.db.users.save({"_id": user.inserted_id}, user)
    return


def add_score(user, score):
    user['data']['score'] = SCORE
    mongo.db.users.save({"_id": user.inserted_id}, user)


def add_homeruns(user, player_id, hrs):
    for __ in range(0, hrs):
        user['data']['hr'].append(player_id)
    mongo.db.users.save({"_id": user.inserted_id}, user)


def add_ss(user, player_id, ss):
    for __ in range(0, ss):
        user['data']['ss'].append(player_id)
    mongo.db.users.save({"_id": user.inserted_id}, user)

