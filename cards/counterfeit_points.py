from objects import Card


class Counterfeit_Points(Card):
    def init(self):
        self.val = 300
        self.name = 'Counterfeit Points'
        self.image = 'Counterfeit_Points.png'
        self.flags = set()
        self.tags = set()

    def on_play(self, kernel, gamestate, player):
        kernel.add_card(self, type(self), gamestate.discard)
