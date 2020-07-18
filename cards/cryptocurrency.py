from objects import Card

class Cryptocurrency(Card):
    def init(self):
        self.val = 600
        self.name = 'Cryptocurrency'
        self.image = 'Cryptocurrency.png'
        self.flags = set()
        self.tags = {"Technology"}

    def on_play(self, kernel, gamestate, player):
        print(f"cryptocurrency played at {gamestate.turn_num}")
        self.turn_played = gamestate.turn_num

    def handle_end_turn(self, kernel, player, gamestate):
        print(f"cryptocurrency turn num {gamestate.turn_num}")
        if gamestate.turn_num == self.turn_played + 3:
            self.val = -800
