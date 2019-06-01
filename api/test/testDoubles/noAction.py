'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: A fake action that does nothing, used for testing to terminate
            the action map
'''
from api.actions import Action


class Nop(Action):
    """Stub for the next action to allow testing individual actions"""

    def process(self, message, action_map):
        return
