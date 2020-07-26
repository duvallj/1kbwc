from bwc.objects import Card


class weird_formatting(Card):
    def init(self):
        self.val = -200
        self.name = 'Weird Formatting'
        self.image = 'WeirdFormatting.png'
        self.flags = set()
        self.tags = {"Technology"}
