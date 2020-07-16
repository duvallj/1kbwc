from objects import Card


class Development_Card(Card):
    def init(self):
        self.val = 0
        self.name = 'Development Card'
        self.image = 'Development_Card.png'
        self.flags = set()

    def on_play(self, kernel, gamestate, player):
        kernel.change_play_limit(self, gamestate.max_cards_played_this_turn + 1)
        kernel.change_draw_limit(self, gamestate.max_cards_drawn_this_turn + 2)
