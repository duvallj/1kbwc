from bwc.objects import Card


class red_cube(Card):
    def init(self):
        self.val = 200
        self.name = 'Red Cube'
        self.image = 'red_cube.png'
        self.flags = set()
        self.tags = set()
