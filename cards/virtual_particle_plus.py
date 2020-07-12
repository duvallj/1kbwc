from objects import Card, CardFlag


class virtual_particle_plus(Card):
    def init(self):
        self.val = 200
        self.name = 'Virtual Particle +'
        self.image = 'virtual_particle_plus.png'
        self.flags = {CardFlag.PLAY_ANY_TIME}

    def on_play(self, kernel, gamestate, player):
        pass
