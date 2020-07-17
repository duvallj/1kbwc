from objects import Card, CardFlag
import random

class NoahsRightLeg(Card):
    def init(self):
        self.val = 150
        self.name = 'Noah\'s Right Leg'
        self.image = 'NoahsRightLeg.jpg'
        self.tags = {"Lined"}
        self.flags = set()

    def on_play(self, kernel, gamestate, player):
        pass
