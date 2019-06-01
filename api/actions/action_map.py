from api.actions.identify_user import IdentifyUser
from api.actions.welcome import WelcomeAction
from api.actions.homescreen import HomescreenAction
from api.actions.submit_score import SubmitScoreAction
from api.settings.action_keys import WELCOME_KEY, IDENTIFY_KEY, HOME_KEY,\
    SUBMIT_SCORE_KEY

ACTION_MAP = {WELCOME_KEY: WelcomeAction,
              IDENTIFY_KEY: IdentifyUser,
              HOME_KEY: HomescreenAction,
              SUBMIT_SCORE_KEY: SubmitScoreAction}
