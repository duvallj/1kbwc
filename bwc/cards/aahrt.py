from random import choice

from bwc.objects import Card


class aahrt(Card):
    def init(self):
        self.val = 0
        self.name = 'AAHRT'
        self.image = 'AAHRT.png'
        self.flags = set()
        self.tags = set()

    def on_play(self, kernel, gamestate, player):
        kernel.send_message([self.owners[0]], f"[{self.name}] Yell a statement!")
        asked_player = choice(list(gamestate.players.values()))
        kernel.send_message([asked_player], f"[{self.name}] Did {self.owners[0].username} find meaning in artwork?")
        kernel.get_player_input(asked_player, ["Nooooo!", "Yaaaaasssss!"], self.change_score)

    def change_score(self, answer):
        if answer == "Yaaaaasssss!":
            self.val = 300
