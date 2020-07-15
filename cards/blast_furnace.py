from objects import Card


class Blast_Furnace(Card):
    def init(self):
        self.val = 50
        self.name = 'Blast Furnace'
        self.image = 'Blast_Furnace.png'
        self.flags = set()
        self.active = -1
        self.tags = {'Metallurgy'}

    def on_move(self, kernel, player, card, from_area, to_area, gamestate):
        if to_area == self.area and self.active == -1:
            self.active = 1
            kernel.move_card(self.owners[0], gamestate.draw.contents[0], gamestate.draw, self.area)
        self.active = -1

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        if self.active == 1:
            if player == self.owners[0]:
                if card == gamestate.draw.contents[0]:
                    self.active += 1
                    return True
