from bwc.objects import Card


class slept_in(Card):
    def init(self):
        self.val = -200
        self.name = 'Slept In!'
        self.image = 'SleptIn.png'
        self.flags = set()
        self.tags = {"School"}
