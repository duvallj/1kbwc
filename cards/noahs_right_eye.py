from objects import Card, CardFlag
import random

class NoahsRightEye(Card):
    def init(self):
        self.val = 100
        self.name = 'Noah\'s Right Eye'
        self.image = 'NoahsRightEye.jpg'
        self.tags = {"Lined"}
        self.flags = set()

    def on_play(self, kernel, gamestate, player):
        pass
