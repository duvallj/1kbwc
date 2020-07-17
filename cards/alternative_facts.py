from objects import Card


class alternative_facts(Card):
    def init(self):
        self.val = 0
        self.name = 'Alternative Facts'
        self.image = 'Alternative_Facts.png'
        self.flags = set()
        self.tags = set()

    def handle_score_player(self, kernel, player, default_score, gamestate):
        if player in self.owners:
            return -1 * kernel.score_area(gamestate.center)
