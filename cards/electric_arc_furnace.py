from objects import Card, CardFlag


class electric_arc_furnace(Card):
    def init(self):
        self.val = 200
        self.name = 'Electric Arc Furnace'
        self.image = 'Electric_Arc_Furnace.png'
        self.flags = set()
        self.tags = {"Metallurgy", "Technology"}
        self.discarded = {}
        self.played = {}
        self.active = False

    def on_play(self, kernel, gamestate, player):
        self.discarded = {}
        self.played = {}
        for player in self.owners:
            self.discarded[player.username] = 0
            self.played[player.username] = 0
        self.active = True

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        if self.active:
            if to_area == gamestate.discard:
                if from_area == self.area:
                    if player in self.owners:
                        if self.discarded[player.username] < 2:
                            self.discarded[player.username] += 1
                            return True
            if to_area == self.area:
                if player in self.owners:
                    if from_area == player.hand:
                        if self.played[player.username] < 1:
                            self.played[player.username] += 1
                            return True

    def handle_end_turn(self, kernel, player, gamestate):
        if self.active:
            for player in self.played:
                if self.played[player] < 1:
                    return False
            for player in self.discarded:
                if self.discarded[player] < 2:
                    return False
            self.active = False

