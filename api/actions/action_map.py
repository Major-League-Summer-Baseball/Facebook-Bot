from api.actions.identify_user import IdentifyUser
from api.actions.welcome import WelcomeAction
from api.variables import WELCOME_KEY, IDENTIFY_KEY

ACTION_MAP = {WELCOME_KEY: WelcomeAction, IDENTIFY_KEY: IdentifyUser}
