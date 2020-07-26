from bwc.objects import Card


class Differential_Equations(Card):
    def init(self):
        self.val = 200
        self.name = 'Differential Equations'
        self.image = 'Differential_Equations.png'
        self.active = False
        self.flags = set()
        self.tags = {"School"}

    def on_play(self, kernel, gamestate, player):
        if len(player.area.contents) > 0:
            self.active = True

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        if self.active:
            if player == self.player:
                if from_area == self.player.area:
                    if to_area == gamestate.discard:
                        self.active = False
                        return True

    def handle_end_turn(self, kernel, player, gamestate):
        if self.active:
            return False
