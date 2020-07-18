from objects import Card, CardFlag


class angry_cat(Card):
    def init(self):
        self.val = 300
        self.name = 'Angry Cat'
        self.image = 'Angry_Cat.png'
        self.flags = {CardFlag.ALWAYS_GET_EVENTS}
        self.tags = {"Animal", "Cat"}
        self.target = None

	
    def on_play_move(self, kernel, player, card, from_area, to_area, gamestate):
        if card != self:
            self.target = card

    def on_play(self, kernel, gamestate, player):
        if kernel.move_card(self, self.target, self.target.area, gamestate.discard):
            kernel.send_message(self.target.owners, f"[{self.name}] *angry cat noises*")

