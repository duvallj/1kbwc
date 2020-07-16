from objects import Card


class Dark_Sacrifice(Card):
    def init(self):
        self.val = 1500
        self.name = 'Dark Sacrifice'
        self.image = 'Dark_Sacrifice.png'
        self.active = False

    def on_play(self, kernel, gamestate, player):
        for card in player.hand.contents:
            self.active = True
            kernel.move_card(self.player, card, player.hand, gamestate.discard)

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        if self.active:
            self.active = False
            return True
        
