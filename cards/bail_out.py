from objects import Card


class Bail_Out(Card):
    def init(self):
        self.val = -200
        self.name = 'Bail-Out'
        self.image = 'Bail-Out.png'
        self.flags = set()
        self.tags = set()

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        if player in self.owners:
            if from_area == player.hand:
                if to_area == gamestate.draw:
                    return True
