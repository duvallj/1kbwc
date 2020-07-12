from objects import Card

class Cryptocurrency(Card):
    def init(self):
        self.val = 600
        self.name = 'Cryptocurrency'
        self.image = 'Cryptocurrency.png'
        self.flags = set()

    def on_play(self, kernel, gamestate, player):
        self.turn_played = gamestate.turn_num

    def handle_end_turn(self, kernel, player, gamestate):
        if gamestate.turn_num == self.turn_played + 3:
            self.val = -800
