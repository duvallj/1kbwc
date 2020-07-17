## THIS API FILE IS FOR REFERENCE ONLY; it is not a full implementation

# All of the objects found in a game
# The "gamestate" object passed to cards is of type Game, found at the bottom of this file

class Card:
    def __init__(self):
        self.val = 0  # point value of card
        self.name = ''  # name of card
        self.image = None  # image on card
        self.flags = set()  # identifiers for card (government system, play at any time, etc.)
        self.tags = set()  # card identifiers for other cards to use (animal, vegetable, mineral)
        # !!! these properties should ONLY be edited by the Kernel
        # !!! this card should only reference them immutably, using the @properties below
        self.owners = []  # owners of the area this card is in
        self.player = None  # person who moved this card into play
        self.area = None  # area this card resides in (hand, play, deck, etc.)
        self.uuid = getrandbits(32)  # unique identifier to distinguish from copies
        self.init()

class CardFlag(Enum):
    PLAY_ANY_TIME = 'Play at any time'
    """
    This flag marks a card that can be played even when it isn't the player's turn,
    and whose play does not use up a turn's play action.
    """
    ALWAYS_GET_EVENTS = 'Get events in any area'
    """
    This flag marks a card that *always* has its' handlers called, even if it isn't in play
    """
    ONLY_PLAY_TO_SELF = 'Can only be played to the player'
    """
    This flag marks a card that can only be played into the play area of the player playing it
    """
    NO_PLAY_TO_SELF = "Cannot be played to the player"
    """
    This flag marks a card that cannot be played to the area of the player playing it
    """
    ONLY_PLAY_TO_CENTER = "Can only be played to the center"
    """
    this flag marks a card that can only be played to the center
    """
    NO_PLAY_TO_CENTER = "Cannot be played to the center"
    """
    This flag marks a card that cannot be played into the center area
    """

class Area:
    def __init__(self, disallowed=None):
        if disallowed is None:
            disallowed = []
        self.owners = []  # players who can play from or are affected by this area
        self.viewers = self.owners[:]  # players who can see the contents of this area
        self.contents = []  # the cards in this area
        self.id = random_id(disallowed)
        self.flags = set()  # extra data associated with this area

class AreaFlag(Enum):  # area types
    PLAY_AREA = 'PLAY AREA'
    """
    This flag marks the area as a Play Area, which means that by default, cards in 
    this area will have their callbacks executed.  Also, any moves from a non PLAY_AREA
    to a PLAY_AREA count as a "Play".
    """
    DRAW_AREA = 'DRAW AREA'
    """
    This flag marks the area as a Draw Area.  Any moves from a DRAW_AREA to a HAND_AREA
    count as a "draw".
    """
    HAND_AREA = 'HAND AREA'
    """
    This flag marks the area as a Draw Area.  Any moves from a DRAW_AREA to HAND_AREA 
    count as a "draw."
    """
    DISCARD_AREA = 'DISCARD AREA'
    """
    This flag marks the area as a Discard Area.  Any moves into a DISCARD_AREA count
    as a Discard action.
    """


class Player:
    def __init__(self):
        self.username = ''  # the name of the player
        self.hand = None  # the player's hand
        self.area = None  # the player's play area
        self.score = 0  # the player's score

class Game:
    def __init__(self):
        self.players: Dict[str, Player] = {}  # all the players

        self.center: Optional[Area] = None  # reference to the center
        self.draw: Optional[Area] = None  # reference to the draw pile
        self.discard: Optional[Area] = None  # reference to the discard pile
        self.all_areas: Dict[str, Area] = {}  # references to *every* area in the game
        self.all_cards: List[Card] = []  # references to each card in the game; as cards are played they are moved towards the front

        self.turn_order = self.players.values()  # normal turn rotation
        self.turn_q: List[Player] = []  # turn rotation override

        self.turn_num: int = 0  # incremented each turn, mostly for use by cards w/ timers
        self.current_player: Optional[Player] = None
        self.turn_order_index: int = 0
        self.max_cards_played_this_turn: int = 1
        self.cards_played_this_turn: int = 0        # keeps track of how many cards the player played under normal circumstances, cards that other players play this turn or that cards force a player to play are not counted
        self.max_cards_drawn_this_turn: int = 1
        self.cards_drawn_this_turn: int = 0
