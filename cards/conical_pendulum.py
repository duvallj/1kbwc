from objects import Card, CardFlag


class Conical_Pendulum(Card):
    def init(self):
        self.val = 200
        self.name = 'Conical Pendulum'
        self.image = 'Conical_Pendulum.png'
        self.active = False
        self.flags = {CardFlag.NO_PLAY_TO_CENTER}

    def on_turn_start(self, kernel, player, gamestate):
        players = list(gamestate.players.values())
        index = (players.index(self.area.owners[0]) + 1) % len(gamestate.players)
        to_area = players[index].area
        self.active = True
        kernel.move_card(self.owners[0], card, self.area, to_area)
        self.active = False

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        if self.active:
            if card == self:
                return True
