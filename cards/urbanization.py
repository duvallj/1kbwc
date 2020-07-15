from objects import Card, CardFlag


class urbanization(Card):
    def init(self):
        self.val = 0
        self.name = 'Urbanization'
        self.image = 'Urbanization.png'
        self.flags = {CardFlag.ONLY_PLAY_TO_CENTER}
        self.tags = set()

    def handle_score_player(self, kernel, player, default_score, gamestate):
        return -100 * len(player.area.contents)
