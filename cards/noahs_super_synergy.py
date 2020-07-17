from objects import Card, CardFlag
import random

class NoahsSuperSynergy(Card):
    def init(self):
        self.val = 200
        self.name = 'Noah\'s Super Synergy'
        self.image = 'NoahsSuperSynergy.jpg'
        self.tags = {"Lined"}
        self.flags = set()

    def on_play(self, kernel, gamestate, player):
        pass