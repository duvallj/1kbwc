from bwc.objects import Card, AreaFlag


class peace(Card):
    def init(self):
        self.val = 200
        self.name = 'Peace!'
        self.image = 'Peace.png'
        self.flags = set()
        self.tags = set()
        self.active = True

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        if self.active:
            if AreaFlag.PLAY_AREA not in from_area.flags and AreaFlag.PLAY_AREA in to_area.flags:  # play
                if card.val < 0:
                    return False

    def on_turn_start(self, kernel, player, gamestate):
        if player == self.player:
            self.active = False
