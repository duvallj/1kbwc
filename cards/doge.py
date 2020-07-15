from objects import Card, CardFlag


class doge(Card):
    def init(self):
        self.val = 300
        self.name = 'Doge'
        self.image = 'doge.png'
        self.flags = set()
        self.tags = {"Animal"}
