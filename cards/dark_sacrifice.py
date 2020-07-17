from objects import Card


class Dark_Sacrifice(Card):
    def init(self):
        self.val = 1500
        self.name = 'Dark Sacrifice'
        self.image = 'Dark_Sacrifice.png'

    def on_play(self, kernel, gamestate, player):
        for card in player.hand.contents:
            kernel.move_card(self, card, player.hand, gamestate.discard)
