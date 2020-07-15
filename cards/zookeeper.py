from objects import Card, CardFlag


class zookeeper(Card):
    def init(self):
        self.val = 0
        self.name = 'Zookeeper'
        self.image = 'Zookeeper.png'
        self.flags = set()
        self.tags = set()

    def on_play(self, kernel, gamestate, player):
        for c in self.area.contents:
            if "Animal" in c.tags:
                self.val += 100

    def on_move(self, kernel, player, card, from_area, to_area, gamestate):
        if "Animal" in card.tags:
            if from_area == this.area:  # Loss of animal
                self.val -= 100
            elif to_area == this.area:  # Gain of animal
                self.val += 100
