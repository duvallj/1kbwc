from objects import Card


class Composite_Gang(Card):
    def init(self):
        self.val = 0
        self.name = 'Composite Gang'
        self.image = 'Composite_Gang.png'
        self.flags = set()
        self.tags = {"School"}

    def handle_score_player(self, kernel, player, default_score, gamestate):
        if player in self.owners:
            return default_score # return score, resulting in score doubling
