from objects import Card, CardFlag
import random

class Dog_Ate_Your_Homework(Card):
    def init(self):
        self.val = 0
        self.name = 'Dog Ate Your Homework'
        self.image = 'A_Dog_Ate_Your_Homework.png'
        self.flags = set()

    def on_play(self, kernel, gamestate, player):
        if (len(self.area.contents) > 1): # If the area is empty, or only includes this card, break
            dupl = list(self.area.contents)
            dupl.remove(self)
            rand_card = random.choice(dupl)
            kernel.move_card(self, rand_card, self.area, gamestate.discard)

