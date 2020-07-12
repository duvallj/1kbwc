from objects import Card


class ding(Card):
    def init(self):
        self.val = 100
        self.name = 'Ding'
        self.image = 'Ding.png'
        self.flags = {PLAY_ANY_TIME}
