from api.actions import ActionInterface


class WelcomeAction(ActionInterface):
    ACTION_IDENTIFIER = "Welcome screen"

    def process(self):
        pass
