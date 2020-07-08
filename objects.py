
class Card():
    def __init__(self):
        self.data = None    # CardData - things bound less tightly to instance

        self.owner = None   # owner of the area this card is in
        self.player = None  # person who moved this card into play
        self.area = None    # area this card resides in (hand, play, deck, etc.)

## (editable) data tied to the card itself, and not the game
class CardData():
    def __init__(self):
        self.val = 0        # point value of card
        self.name = ''      # name of card
        self.action = ''    # code on card, `eval`ed by game
        self.image = None   # image on card
        self.flags = set()   # identifiers for card (government system, play at any time, etc.)

class Area():
    def __init__(self):
        self.owners = []            # players who can play from or are affected by this area
        self.viewers = self.owners  # players who can see the contents of this area
        self.contents = []          # the cards in this area

class Player():
    def __init__(self):
        self.hand = None    # the player's hand
        self.area = None    # the player's play area
        self.score = 0      # the player's score

class Game():
    def __init__(self):
        self.players = []           # all the players
        
        self.center = None          # reference to the center
        self.draw = None            # reference to the draw pile
        self.discard = None         # reference to the discard pile
        self.all_areas = []         # references to *every* area in the game

        self.turn_order = self.players  # normal turn rotation
        self.turn_q = []                # turn rotation override


