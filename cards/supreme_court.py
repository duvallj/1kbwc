from kernel import Kernel
from objects import Card, Game


class SupremeCourt(object): # not a card
    def init(self):
        self.val = 300
        self.name = 'Supreme Court'
        self.image = "Supreme_Court.png"
        self.flags = set()
        self.tags = {"NYI"}

    def on_end_game(self, kernel: Kernel, gamestate: Game):
        raise NotImplementedError("URBAD")
        # URBAD
        scores = {name: kernel.score_player(p) for name, p in gamestate.players.values()}
        for p, score in scores.values():
            #nearby = [p for p in]
            pass
