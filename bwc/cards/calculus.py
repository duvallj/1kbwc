from bwc.objects import Card


class Calculus(Card):
    def init(self):
        self.val = 300
        self.name = 'Calculus'
        self.image = 'Calculus.png'
        self.flags = set()
        self.tags = {"School"}
