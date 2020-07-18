from objects import Card


class blessed_by_the_physics_gods(Card):
    def init(self):
        self.val = 0
        self.name = 'Blessed By The Physics Gods'
        self.image = 'Blessed_By_The_Physics_Gods.png'
        self.flags = set()
        self.tags = {"School"}

    def on_play(self, kernel, gamestate, player):
        kernel.send_message(self.owners, "[Blessed By The Physics Gods] Did you have a quiz today?")
        for owner in self.owners:
            kernel.get_player_input(owner, ["yes", "no"], self.change_score)

    def change_score(self, answer):
        if answer == "yes":
            self.val = 0
        if answer == "no":
            self.val = 400

