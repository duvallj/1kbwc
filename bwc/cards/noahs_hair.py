import random

from bwc.objects import Card
from bwc.server_rendering import format_area_id


class NoahsHair(Card):
    def init(self):
        self.val = 200
        self.name = 'Noah\'s Hair'
        self.image = 'NoahsHair.jpg'
        self.flags = set()
        self.tags = {"Lined"}
        self.active = False

    def on_play_move(self, kernel, player, moving_card, from_area, to_area, game):
        if moving_card == self and not self.active:
            self.active = True
            do_random = random.randint(0, 1)
            if do_random:
                random_area = random.choice(list(game.all_areas.values()))
            else:
                random_area = to_area

            if random_area == to_area:
                # ended up in the correct area!
                self.val = 400
                kernel.send_message(list(game.players.values()), f"Noah's hair ended up in the correct area!")
            else:
                kernel.move_card(self, self, to_area, random_area)
                kernel.send_message(list(game.players.values()), f"Noah's hair ended up in {format_area_id(random_area)}")
