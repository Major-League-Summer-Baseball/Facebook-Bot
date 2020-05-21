'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds a map from action keys to their class the implements them.
'''
from api.actions.action.identify_user import IdentifyUser
from api.actions.action.welcome import WelcomeUser
from api.actions.action.homescreen import Homescreen
from api.actions.action.submit_score import SubmitScore
from api.actions import ActionKey


ACTION_MAP = {str(ActionKey.WELCOME_KEY): WelcomeUser,
              str(ActionKey.IDENTIFY_KEY): IdentifyUser,
              str(ActionKey.HOME_KEY): Homescreen,
              str(ActionKey.SUBMIT_SCORE_KEY): SubmitScore}
