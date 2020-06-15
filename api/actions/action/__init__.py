'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds various actions of the Facebook bot
    An actions is a combination of various states
    that together form a coherent action that user can perform
    E.g. Submit a score, Subscribe to a team
    All actions should keep track of their own state
'''
from typing import Tuple, List
from api.actions import ActionKey
from api.database import DatabaseInterface
from api.mlsb.platform import PlatformService
from api.players.player import Player
from api.message import Message


class Action():
    """
    The action interface - any action will need to implement process
    """

    def __init__(self, database: DatabaseInterface, platform: PlatformService):
        """Constructor that takes database and platform"""
        self.database = database
        self.platform = platform

    def process(self, player: Player,
                message: Message) -> Tuple[Player, List[Message],
                                           ActionKey]:
        """Process the message for the given player
        Parameters:
            player: the player related to the message
            message: the message sent by the player
        Returns:
            a tuple with the player, a list of messages to send
            and key for next action
        """
        raise NotImplementedError("Action needs to implement process method")
