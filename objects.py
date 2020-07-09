from util import immutablize
from enum import Enum

## (editable) data tied to the card itself, and not the game
class Card():
    def __init__(self):
        self.val = 0        # point value of card
        self.name = ''      # name of card
        self.image = None   # image on card
        self.flags = set()   # identifiers for card (government system, play at any time, etc.)
        ### these properties should ONLY be edited by the Kernel
        ### this card should only reference them immutably, using the @properties below
        self._owner = None   # owner of the area this card is in
        self._player = None  # person who moved this card into play
        self._area = None    # area this card resides in (hand, play, deck, etc.)
        self.init()

    def init(self):
        raise NotImplementedError("Card has no init function!")
    @property
    def owner(self):
        return immutablize(self._owner)
    @property
    def player(self):
        return immutablize(self._player)
    @property
    def area(self):
        return immutablize(self._area)

class Area():
    def __init__(self):
        self.owners = []            # players who can play from or are affected by this area
        self.viewers = self.owners  # players who can see the contents of this area
        self.contents = []          # the cards in this area
        self.flags = set()          # extra data associated with this area

class AreaFlag(Enum):       # area types
    PLAY_AREA = 'PLAY AREA'
    DRAW_AREA = 'DRAW AREA'
    HAND_AREA = 'HAND AREA'
    DISCARD_AREA = 'DISCARD AREA'

class Player():
    def __init__(self):
        self.username = ''  # the name of the player
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

        self.turn_num           # incremented each turn, mostly for use by cards w/ timers


