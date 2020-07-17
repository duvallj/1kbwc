from objects import Card, CardFlag
import random

class NoahsSynergy(Card):
    def init(self):
        self.val = 200
        self.name = 'Noah\'s  Synergy'
        self.image = 'NoahsSynergy.jpg'
        self.tags = {"Lined"}
        self.flags = set()

    def on_play(self, kernel, gamestate, player):
        pass
