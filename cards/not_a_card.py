from objects import Card, CardFlag

class NotACard(Card):
    def init(self):
        self.val = 0
        self.name = "CARD"
        self.image = "NotACard.png"
        self.flags = set()
        self.tags = set()

    def on_play(self, kernel, gamestate, player):
        all_players = [gamestate.players[name] for name in gamestate.players]
        kernel.send_message(all_players, "A suspicious looking card has been played...")

        for other_player in all_players:
            if other_player != player:
                kernel.get_player_input(other_player, ["yes", "no"], self.is_a_card(gamestate))

    def is_a_card(self, gamestate):
        def do(value):
            all_players = [gamestate.players[name] for name in gamestate.players]
            if value == "yes":
                self.val = 1000
                kernel.send_message(all_players, "...but it is a card, after all.")
        return do
