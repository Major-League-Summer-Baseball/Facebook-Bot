'''
Created on May 3, 2017

@author: d6fraser
'''
import requests
import unittest
from api.helper import log
from api.errors import FacebookException, PlatformException,\
                       PLATFORMMESSAGE, NotCaptainException, IdentityException
from api.variables import PID, HEADERS, BASEURL, PAGE_ACCESS_TOKEN


def get_user(identity, mongo):
    """ Returns if a user exists and creates one if if they dont

    Parameters:
        identity: facebook id (string)
    Returns:
        (user, created): the user and boolean to tell if created or not
    """
    created = False
    user = mongo.db.users.find_one({'fid': identity})
    if user is None:
        created = True
        # get the player's id
        url = "https://graph.facebook.com/v2.6/{}?fields=first_name,last_name&access_token={}".format(identity, PAGE_ACCESS_TOKEN)
        r = requests.get(url)
        log("Facebook profile")
        if (r.status_code) != 200:
            raise FacebookException("Facebook services not available")
        log(r.json())
        d = r.json()
        name = d['first_name'] + d['last_name']
        # now we know who this person is
        mongo.db.users.insert({"fid": identity,
                               "state": PID,
                               "name": name,
                               "pid": -1,
                               "game": {},
                               "teamroster": {},
                               "captain": -1
                               })
        user = mongo.db.users.find_one({'fid': identity})
        log("saved user")
        log(user)
    return (user, created)


def save_user(user, mongo):
    """ Save the changes of the user"""
    mongo.db.users.save({"_id": user.inserted_id}, user)
    return


def lookup_player(user):
    """Returns a lookup for the player in the league

    Parameter:
        user: a dictionary of the user (dict)
    Raises:
        PlatformException: if platform gives an error
    Returns:
        player: None if can't determine player other a player object
    """
    submission = {"player_name": user['name'], "active": 1}
    r = requests.post(BASEURL + "api/view/player_lookup",
                      params=submission,
                      headers=HEADERS)
    log("User look up")
    players = r.json()
    if (r.status_code != 200):
        raise PlatformException(PLATFORMMESSAGE)
    log(r.json())
    if len(players) == 0 or len(players) > 1:
        player = None
    else:
        # we got him
        player = players[0]
    return player


def lookup_player_email(user, email):
    """Returns a lookup for a player in the league using their email provided

    Parameters:
        user: the user dictionary (dict)
        email: the email they given (string)
    Raises:
        IdentityException: if no one is found
    Returns:
        player: the player found
    """
    submission = {"email": email}
    r = requests.post(BASEURL + "api/view/player_lookup",
                      params=submission,
                      headers=HEADERS)
    log("User look up")
    if(r.status_code != 200):
        raise PlatformException(PLATFORMMESSAGE)
    log(r.json())
    players = r.json()
    if len(players) == 0:
        raise IdentityException("Not sure who you are, ask admin")
    return players[0]


def update_player(user, player):
    """Updates a player and checks if they are a captain

    Parameters:
        user: the user dictionary
        player: the player object
    Returns:
        user: the update user
    """
    user['pid'] = player['player_id']
    params = {"player_id": user["pid"]}
    r = requests.post(BASEURL + "api/view/players/team_lookup",
                      params=params,
                      headers=HEADERS)
    if (r.status_code != 200):
        raise PlatformException(PLATFORMMESSAGE)
    # now look up teams
    captain = -1
    teams = r.json()
    for team in teams:
        if team['captain']['player_id'] == user['pid']:
            captain = team["team_id"]
    user['captain'] = captain
    return user


def get_games(user):
    """Returns the captain games they can submit

    Parameters:
        user: the dictionary object of a user (dict)
    Returns:
        games: a list of games
    """
    params = {"player_id": user['pid'], "team": user['captain']}
    r = requests.post(BASEURL + "api/bot/captain/games",
                      data=params,
                      headers=HEADERS)
    if (r.status_code == 401):
        log(r.text)
        raise NotCaptainException("Says you are not a captain, check admin")
    elif (r.status_code != 200):
        log(r.status_code)
        raise PlatformException(PLATFORMMESSAGE)
    games = r.json()
    return games


def submit_score(user):
    """Submits a score and wipes the data

    Parameters:
        user: the dictionary object
    Returns:
        user: the update user
    """
    submission = user['game']
    submission['player_id'] = user['pid']
    r = requests.post(BASEURL + "api/bot/submit_score",
                      params=submission,
                      headers=HEADERS)
    if (r.status_code == 401):
        raise NotCaptainException("Says you are not the captain, ask admin")
    elif (r.status_code != 200):
        raise PlatformException(PLATFORMMESSAGE)
    # remove the data since not relevant
    user['game'] = {}
    return user


def add_game(user, game_id):
    """add a game to the user
    """
    user['game'] = {"game_id": game_id,
                    "score": 0,
                    "hr": [],
                    "ss": []}
    # update the team roster
    user['teamroster'] = {}
    r = requests.get(BASEURL + "api/teamroster/{}".format(user['captain']))
    if (r.status_code != 200):
        raise PlatformException(PLATFORMMESSAGE)
    players = r.json()['players']
    for player in players:
        user['teamroster'][player['player_id']] = player['player_name']
    log(user['teamroster'])
    return user


def add_score(user, score):
    """Add a score of the game

    Parameters:
        user: the dictionary of the user (dict)
        score: the score of the game (int)
    Returns:
        user: the update user (dict)
    """
    user['game']['score'] = score
    return user


def add_homeruns(user, player_id, hrs):
    """Add a hr by a player

    Parameters:
        user: the dictionary of the user (dict)
        player_id: the player id (int)
        hrs: the number of hr hit (int)
    Returns:
        user: the update user (dict)
    """
    for __ in range(0, hrs):
        user['game']['hr'].append(player_id)
    return user


def add_ss(user, player_id, ss):
    """Add a ss by a player

    Parameters:
        user:  a user dictionary (dict)
        player_id: the player id of the batter (int)
        ss: the number of ss (int)
    Returns:
        user: the update user
    """
    for __ in range(0, ss):
        user['game']['ss'].append(player_id)
    return user


def game_summary(user):
    """Returns a game summary

    Parameters:
        user: the with the game to profile
    Returns:
        summary: a list of the summary (list of strings)
    """
    summary = []
    summary.append("Score: {}".format(user['game']['score']))
    # pair hrs with their names and count
    hrs = {}
    for pid in user['game']['hr']:
        if pid not in hrs.keys():
            hrs[pid] = {"count": 1, "name": user['teamroster'][pid]}
        else:
            hrs[pid]['count'] += 1
    # pair ss with their names and count
    ss = {}
    for pid in user['game']['ss']:
        if pid not in hrs.keys():
            ss[pid] = {"count": 1, "name": user['teamroster'][pid]}
        else:
            ss[pid]['count'] += 1
    summary.append("HR:")
    for __, bat in hrs.items():
        summary.append("{} - {:d}".format(bat['name'], bat['count']))
    summary.append("SS:")
    for __, bat in ss.items():
        summary.append("{} - {:d}".format(bat['name'], bat['count']))
    return summary


class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.user = {"fid": 1,
                     "state": PID,
                     "name": "Dallas Fraser",
                     "pid": 2,
                     "game": {},
                     "teamroster": {},
                     "captain": 1
                     }

    def testGameSummary(self):
        self.user['teamroster'] = {2: "Dallas Fraser", 3: "Dream Girl"}
        self.user['game']['score'] = 1
        self.user['game']['hr'] = [2, 2]
        self.user['game']['ss'] = [3]
        result = game_summary(self.user)
        expect = ['Score: 1', 'HR:',
                  'Dallas Fraser - 2',
                  'SS:', 'Dream Girl - 1']
        self.assertEqual(expect, result)

    def testAddScore(self):
        user = add_score(self.user, 5)
        expect = {"fid": 1,
                  "state": PID,
                  "name": "Dallas Fraser",
                  "pid": 2,
                  "game": {"score": 5},
                  "teamroster": {},
                  "captain": 1
                  }
        self.assertEqual(user, expect)

    def testAddHomerun(self):
        self.user['game']['hr'] = []
        user = add_homeruns(self.user, 1, 2)
        expect = {"fid": 1,
                  "state": PID,
                  "name": "Dallas Fraser",
                  "pid": 2,
                  "game": {"hr": [1, 1]},
                  "teamroster": {},
                  "captain": 1
                  }
        self.assertEqual(user, expect)
        user = add_homeruns(self.user, 2, 1)
        expect = {"fid": 1,
                  "state": PID,
                  "name": "Dallas Fraser",
                  "pid": 2,
                  "game": {"hr": [1, 1, 2]},
                  "teamroster": {},
                  "captain": 1
                  }
        self.assertEqual(user, expect)

    def testAddSS(self):
        self.user['game']['ss'] = []
        user = add_ss(self.user, 1, 2)
        expect = {"fid": 1,
                  "state": PID,
                  "name": "Dallas Fraser",
                  "pid": 2,
                  "game": {"ss": [1, 1]},
                  "teamroster": {},
                  "captain": 1
                  }
        self.assertEqual(user, expect)
        user = add_ss(self.user, 2, 1)
        expect = {"fid": 1,
                  "state": PID,
                  "name": "Dallas Fraser",
                  "pid": 2,
                  "game": {"ss": [1, 1, 2]},
                  "teamroster": {},
                  "captain": 1
                  }
        self.assertEqual(user, expect)


class TestRequests(unittest.TestCase):
    # these test rely on a external platform
    # i just set up these tests if the data changes then they will break
    # need a guy (Dallas Fraser) and a girl (Dream Girl) on the team.id = 1
    def setUp(self):
        self.user = {"fid": 1,
                     "state": PID,
                     "name": "Dallas Fraser",
                     "pid": 2,
                     "game": {},
                     "teamroster": {},
                     "captain": 1
                     }

    def testAddGame(self):
        user = add_game(self.user, 1)
        expect = {'name': 'Dallas Fraser',
                  'captain': 1,
                  'state': -1,
                  'teamroster': {2: 'Dallas Fraser', 3: 'Dream Girl'},
                  'fid': 1,
                  'pid': 2,
                  'game': {'hr': [], 'ss': [], 'score': 0, 'game_id': 1}}
        self.assertEqual(expect, user)

    def testGetGames(self):
        games = get_games(self.user)
        expect = [{'league_id': 1,
                   'home_team_id': 1,
                   'home_team': 'CaliBurger Test',
                   'status': '',
                   'game_id': 1,
                   'time': '10:00',
                   'away_team': 'CaliBurger Test2',
                   'date': '2017-05-03',
                   'away_team_id': 2,
                   'field': 'WP1'}]
        self.assertEqual(expect, games)
        print(games)

    def testUpdatePlayer(self):
        # is a captain
        self.user = {'pid': -1,
                     'name': 'Dallas Fraser',
                     'state': -1,
                     'teamroster': {},
                     'game': {},
                     'fid': 1,
                     'captain': -1}
        user = update_player(self.user, {"player_id": 2})
        expect = {'pid': 2,
                  'name': 'Dallas Fraser',
                  'state': -1,
                  'teamroster': {},
                  'game': {},
                  'fid': 1,
                  'captain': 1}
        self.assertEqual(user, expect)
        # is not a captain
        self.user = {'pid': -1,
                     'name': 'Dream Girl',
                     'state': -1,
                     'teamroster': {},
                     'game': {},
                     'fid': 1,
                     'captain': -1}
        user = update_player(self.user, {"player_id": 3})
        expect = {'pid': 3,
                  'name': 'Dream Girl',
                  'state': -1,
                  'teamroster': {},
                  'game': {},
                  'fid': 1,
                  'captain': -1}
        self.assertEqual(user, expect)

    def testLookupPlayer(self):
        # is a captain
        self.user = {'pid': -1,
                     'name': 'Dallas Fraser',
                     'state': -1,
                     'teamroster': {},
                     'game': {},
                     'fid': 1,
                     'captain': -1}
        user = lookup_player(self.user)
        expect = {'player_id': 2,
                  'player_name': 'Dallas Fraser',
                  'gender': 'm'}
        self.assertEqual(user, expect)
        # is not a captain
        self.user = {'pid': -1,
                     'name': 'Dream Girl',
                     'state': -1,
                     'teamroster': {},
                     'game': {},
                     'fid': 1,
                     'captain': -1}
        user = lookup_player(self.user)
        expect = {'gender': 'f', 'player_name': 'Dream Girl', 'player_id': 3}
        self.assertEqual(user, expect)
        # nobody
        self.user = {'pid': -1,
                     'name': 'WHO THE FUCK',
                     'state': -1,
                     'teamroster': {},
                     'game': {},
                     'fid': 1,
                     'captain': -1}
        user = lookup_player(self.user)
        expect = None
        self.assertEqual(user, expect)

    def testLookupEmailPlayer(self):
        # is a captain
        self.user = {'pid': -1,
                     'name': 'Dallas Fraser',
                     'state': -1,
                     'teamroster': {},
                     'game': {},
                     'fid': 1,
                     'captain': -1}
        user = lookup_player_email(self.user, "fras2560@mylaurier.ca")
        expect = {'player_id': 2,
                  'player_name': 'Dallas Fraser',
                  'gender': 'm'}
        self.assertEqual(user, expect)
        # is not a captain
        self.user = {'pid': -1,
                     'name': 'Dream Girl',
                     'state': -1,
                     'teamroster': {},
                     'game': {},
                     'fid': 1,
                     'captain': -1}
        user = lookup_player_email(self.user, "dreamgirl@mlsb.ca")
        expect = {'gender': 'f', 'player_name': 'Dream Girl', 'player_id': 3}
        self.assertEqual(user, expect)
        # nobody
        self.user = {'pid': -1,
                     'name': 'WHO THE FUCK',
                     'state': -1,
                     'teamroster': {},
                     'game': {},
                     'fid': 1,
                     'captain': -1}
        try:
            user = lookup_player_email(self.user, "WHOTHEFUCK@mlsb.ca")
            self.assertEqual(True, False, "Should raise exception")
        except IdentityException as __:
            pass


class TestSubmitScore(unittest.TestCase):
    # this test is a pain in the ass
    # after teardown hopefully has no errors
    def setUp(self):
        # score  =  hr so no bats are unassigned
        self.user = {'pid': 2,
                     'name': 'Dallas Fraser',
                     'state': -1,
                     'teamroster': {2: "Dallas Fraser", 3: "Dream Girl"},
                     'game': {'game_id': 1,
                              "score": 2,
                              "hr": [2, 2],
                              "ss": [3]},
                     'fid': 1,
                     'captain': 1}
        self.game_id = 1

    def tearDown(self):
        try:
            params = {'game_id': self.game_id}
            r = requests.post(BASEURL + "api/view/games",
                              data=params,
                              headers=HEADERS)
            bats = r.json()[0]['away_bats'] + r.json()[0]['home_bats']
            for bat in bats:
                r = requests.delete(BASEURL +
                                    "api/bats/{:d}".format(bat['bat_id']),
                                    headers=HEADERS)
        except Exception as e:
            print(str(e))
            print("Something bad happen, got to manual reset")

    def testSubmitScore(self):
        user = submit_score(self.user)
        params = {'game_id': self.game_id}
        r = requests.post(BASEURL + "api/view/games",
                          data=params,
                          headers=HEADERS)
        bats = r.json()[0]['home_bats']
        self.assertEqual(r.json()[0]['home_score'], 2)
        for bat in bats:
            self.assertEqual(bat['rbi'] in [0, 1], True)
            self.assertEqual(bat['hit'] in ['hr', 'ss'], True)
            self.assertEqual(bat['name'] in ['Dallas Fraser', 'Dream Girl'],
                             True)
        expect = {'captain': 1, 'pid': 2, 'state': -1,
                  'teamroster': {2: 'Dallas Fraser', 3: 'Dream Girl'},
                  'game': {}, 'name': 'Dallas Fraser', 'fid': 1}
        self.assertEqual(expect, user)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()