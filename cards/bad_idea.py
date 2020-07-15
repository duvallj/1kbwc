from objects import Card, CardFlag


class Bad_Idea(Card):
    def init(self):
        self.val = -800
        self.name = 'Bad Idea'
        self.image = 'Bad_Idea.png'
        self.game_over = False
        self.flags = {CardFlag.ALWAYS_GET_EVENTS}

    def on_end_game(self, *args):
        self.game_over = True

    def handle_score_player(self, kernel, player, default_score, gamestate):
        if player in self.players and self.game_over:
            return -800


