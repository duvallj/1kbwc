from objects import Card


class Dawn_Of_The_Iron_Age(Card):
    def init(self):
        self.val = 200
        self.name = 'Dawn Of The Iron Age'
        self.image = 'Dawn_Of_The_Iron_Age.png'
        self.tags = {'Metallurgy', 'Technology'}
        self.gameover = False

    def handle_score_card(self, kernel, card, gamestate):
        if self.gameover:
            if "Metallurgy" in card.tags:
                return card.val + 600

    def on_end_game(self, kernel, gamestate):
        self.gameover = True
