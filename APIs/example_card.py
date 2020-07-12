from objects import Card


# objects also contains CardFlag, AreaFlag, and all object definitions

class example_card(Card):
    # required:
    def init(self):  ## *NOT* __init__ !
        self.val = 300
        self.name = 'Example Card'
        self.image = 'example.png'
        self.flags = set()

    def on_play(self, kernel, gamestate, player):
        pass
