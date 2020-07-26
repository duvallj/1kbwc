from bwc.objects import Card


class Blast_Furnace(Card):
    def init(self):
        self.val = 50
        self.name = 'Blast Furnace'
        self.image = 'Blast_Furnace.png'
        self.flags = set()
        self.active = False
        self.tags = {'Metallurgy', 'Technology'}

    def on_move(self, kernel, player, card, from_area, to_area, gamestate):
        if card != self and to_area == self.area and not self.active:
            self.active = True
            if kernel.move_card(self, gamestate.draw.contents[0], gamestate.draw, self.area):
                kernel.send_message([player], "Blast Furnacing engaged!")
            self.active = False
