from objects import Card


class button_muffin(Card):
    def init(self):
        self.val = 300
        self.name = 'Press Button Get Muffin'
        self.image = 'PressButtonGetMuffin.png'
        self.flags = set()
        self.tags = {"Food"}
