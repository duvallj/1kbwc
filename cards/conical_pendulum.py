from objects import Card, CardFlag


class Conical_Pendulum(Card):
    def init(self):
        self.val = 200
        self.name = 'Conical Pendulum'
        self.image = 'Conical_Pendulum.png'
        self.flags = {CardFlag.NO_PLAY_TO_CENTER}
        self.tags = set()
        self.turn_starts = 0

    def on_turn_start(self, kernel, player, gamestate):
        self.turn_starts += 1
        players = list(gamestate.players.values())
        index = (players.index(self.area.owners[0]) + 1) % len(gamestate.players)
        to_area = players[index].area
