from api.actions import ActionInterface


class WelcomeAction(ActionInterface):

    def process(self, action_map):
        self.action_map = action_map
