'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Test Welcome Action
'''
from api.actions.homescreen import HomescreenAction
from api.helper import get_this_year
from api.test.testDoubles import NoAction
from api.message import Message
from api.players.player import Player
from api.test.testActions import TestActionBase
from api.actions.welcome import WelcomeAction
from api.settings.action_keys import HOME_KEY
from api.settings.message_strings import PART_OF_TEAM, ACKNOWLEDGE_CAPTAIN,\
    ACKNOWLEDGE_CONVENOR
import unittest


class TestHomescreen(TestActionBase):

    def setUp(self):
        self.action_map = {HOME_KEY: NoAction,
                           SUBMIT_SCORE_KEY: NoAction}
        super(HomescreenAction, self).setUp()
