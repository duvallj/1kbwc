from random import choice

from objects import Card


class crayon_card(Card):
    def init(self):
        self.val = -300
        self.name = 'Crayon Card'
        self.image = 'Crayon_Card.png'
        self.flags = set()
        self.tags = set()

    def on_play(self, kernel, gamestate, player):
        self.val = -300
        kernel.send_message([self.owners[0]], "[Crayon Card] Present your crayon!")
        asked_player = choice(list(gamestate.players.values()))
        kernel.send_message([asked_player], f"[Crayon Card] Does {self.owners[0].username} have a crayon?")
        kernel.get_player_input(asked_player, ["no", "yes"], self.change_score)

    def change_score(self, answer):
        if answer == "yes":
            self.val = 500
        if answer == "no":
            self.val = -300
