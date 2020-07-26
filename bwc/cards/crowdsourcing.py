from bwc.objects import Card, AreaFlag


class Crowdsourcing(Card):
    def init(self):
        self.val = 400
        self.name = 'Crowdsourcing'
        self.image = 'Crowdsourcing.png'
        self.active = False
        self.done_players = []
        self.flags = set()
        self.tags = set()

    def on_play(self, kernel, gamestate, player):
        self.active = True
        # kernel.change_play_limit(self, gamestate.max_cards_played_this_turn + 1)

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        if self.active:
            if AreaFlag.HAND_AREA in from_area.flags and to_area == gamestate.center:
                if player not in self.done_players:
                    self.done_players.append(player)
                    return True

    def handle_end_turn(self, kernel, player, gamestate):
        if self.active:
            if len(self.done_players) + self.count_empty_hands(gamestate) < \
                    len(gamestate.players):
                return False
            else:
                self.active = False
                return True

    def count_empty_hands(self, gamestate):
        n = 0
        for player in gamestate.players.values():
            if len(player.hand.contents) == 0:
                n += 1
        return n
