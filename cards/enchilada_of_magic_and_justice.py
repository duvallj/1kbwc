from objects import Card, CardFlag


class enchilada_of_magic_and_justice(Card):
    def init(self):
        self.val = 0
        self.name = 'Enchilada of Magic and Justice'
        self.image = 'Enchilada_of_Magic_and_Justice.png'
        self.flags = {CardFlag.NO_PLAY_TO_CENTER}
        self.tags = {"Food"}

    def on_play(self, kernel, gamestate, player):
        score = kernel.score_player(self.owners[0])
        for player in list(gamestate.players.values()):
            if player != self.owners[0]:
                if score >= kernel.score_player(player):
                    return
        self.val = 500

    def on_turn_start(self, kernel, player, gamestate):
        if self.val != 500:
            self.val -= 1
