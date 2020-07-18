from objects import Card


class waffle(Card):
    def init(self):
        self.val = 300
        self.name = 'Waffle'
        self.image = 'Waffle.png'
        self.flags = set()
        self.tags = {"Food"}
