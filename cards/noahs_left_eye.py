from objects import Card, CardFlag
import random

class NoahsLeftEye(Card):
    def init(self):
        self.val = -100
        self.name = 'Noah\'s Left Eye'
        self.image = 'NoahsLeftEye.jpg'
        self.tags = {"Lined"}
        self.flags = set()

    def on_play(self, kernel, gamestate, player):
        pass
