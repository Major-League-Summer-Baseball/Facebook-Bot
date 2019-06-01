from api.actions.identify_user import IdentifyUser
from api.actions.welcome import WelcomeUser
from api.actions.homescreen import Homescreen
from api.actions.submit_score import SubmitScore
from api.settings.action_keys import WELCOME_KEY, IDENTIFY_KEY, HOME_KEY,\
    SUBMIT_SCORE_KEY

ACTION_MAP = {WELCOME_KEY: WelcomeUser,
              IDENTIFY_KEY: IdentifyUser,
              HOME_KEY: Homescreen,
              SUBMIT_SCORE_KEY: SubmitScore}
