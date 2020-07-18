from objects import Card, CardFlag


class ding(Card):
    def init(self):
        self.val = 100
        self.name = 'Ding'
        self.image = 'Ding.png'
        self.flags = {CardFlag.PLAY_ANY_TIME}
        self.tags = set()
