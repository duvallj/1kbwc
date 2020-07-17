from objects import Card, CardFlag


class unposessed_santa_hat(Card):
    def init(self):
        self.val = 100
        self.name = 'Unposessed Santa Hat'
        self.image = 'UnposessedSantaHat.png'
        self.flags = set()
        self.tags = set()

    def on_play(self, kernel, gamestate, player):
        kernel.move_card(self, gamestate.draw.contents[0], gamestate.draw, player.hand)
