from objects import Card, CardFlag
import random

class NoahsLeftLeg(Card):
    def init(self):
        self.val = 150
        self.name = 'Noah\'s Left Leg'
        self.image = 'NoahsLeftLeft.jpg'
        self.flags = set()
        self.tags = {"Lined"}

    def on_play(self, kernel, gamestate, player):
        pass
