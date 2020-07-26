from objects import Card


class bad_reception(Card):
    def init(self):
        self.val = -100
        self.name = 'Bad Reception'
        self.image = 'BadReception.png'
        self.flags = set()
        self.tags = {"Technology"}
        self.turnsLeft = {}
        self.active = False

    def on_play(self, kernel, gamestate, player):
        self.turnsLeft = {}
        for p in self.owners:
            self.turnsLeft[p.username] = 2
        self.active = True

    def on_turn_start(self, kernel, player, gamestate):
        if self.active:
            if player.username in self.turnsLeft:
                if self.turnsLeft[player.username] > 0:
                    self.turnsLeft[player.username] -= 1
                    currMax = gamestate.max_cards_drawn_this_turn
                    if currMax > 0 and kernel.change_draw_limit(self, currMax - 1):
                        kernel.send_message([player], f"{self.name} prevented you from drawing a card this turn!")
