from objects import Card, CardFlag
import random

class NoahsLeftLeg(Card):
    def init(self):
        self.val = 150
        self.name = 'Noah\'s Left Leg'
        self.image = 'NoahsLeftLeft.jpg'
        self.tags = {"Lined"}
        self.flags = set()

    def on_play(self, kernel, gamestate, player):
        pass
