from objects import Card
from random import choice


class Three_Star_Review(Card):
    def init(self):
        self.val = 0
        self.name = '3-Star Review'
        self.image = '3-Star_Review.png'
        self.flags = set()
        self.tags = set()

    def on_play(self, kernel, gamestate, player):
        kernel.send_message([self.owners[0]], "[3-Star Review] Go read a review!")
        asked_player = choice(list(gamestate.players.values()))
        kernel.send_message([asked_player], f"[3-Star Review] What did {self.owners[0].username} read?")
        kernel.get_player_input(asked_player, ["No review", "3-star review", "0-star review"], self.change_score)

    def change_score(self, answer):
        if answer == "3-star review":
            self.val = 300
        if answer == "0-star review":
            self.val = 350
