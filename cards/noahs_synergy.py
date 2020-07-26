from objects import Card


class NoahsSynergy(Card):
    def init(self):
        self.val = 200
        self.name = 'Noah\'s Synergy'
        self.image = 'NoahsSynergy.jpg'
        self.flags = set()
        self.tags = {"Lined"}

    def on_play(self, kernel, gamestate, player):
        pass
