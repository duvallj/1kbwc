from objects import Card, CardFlag
import random

class Bakugo(Card):
    def init(self):
        self.val = 200
        self.name = 'Bakugo'
        self.image = 'Bakugo.jpg'
        self.flags = set()
        self.tags = set()

    def on_play(self, kernel, gamestate, player):
        # explode hand and play area into the discard pile
        for area in [player.hand, player.area]:
            for card in area.contents:
                if card != self:
                    print(card)
                    kernel.move_card(self, card, area, gamestate.discard)

        # Then, draw 7 new cards from the bottom of the deck
        for x in range(7):
            if len(gamestate.draw.contents) == 0:
                print("drawpile to small")
                break

            if not kernel.move_card(self, gamestate.draw.contents[-1], 
                    gamestate.draw, player.hand):
                print("wasn't allowed to move card??")
                break

        print("drew all cards")
        # You may play 1 extra card the turn you activate this
        kernel.change_play_limit(self, gamestate.max_cards_played_this_turn + 1)
