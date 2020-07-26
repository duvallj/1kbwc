from bwc.objects import Card


class NoahsRightLeg(Card):
    def init(self):
        self.val = 150
        self.name = 'Noah\'s Right Leg'
        self.image = 'NoahsRightLeg.jpg'
        self.flags = set()
        self.tags = {"Lined"}

    def on_play(self, kernel, gamestate, player):
        pass
