from util import immutablize, random_id
from enum import Enum


# (editable) data tied to the card itself, and not the game
class Card:
    def __init__(self):
        self.val = 0  # point value of card
        self.name = ''  # name of card
        self.image = None  # image on card
        self.flags = set()  # identifiers for card (government system, play at any time, etc.)
        # !!! these properties should ONLY be edited by the Kernel
        # !!! this card should only reference them immutably, using the @properties below
        self._owners = []  # owners of the area this card is in
        self._player = None  # person who moved this card into play
        self._area = None  # area this card resides in (hand, play, deck, etc.)
        self.init()

    def __eq__(self, other):
        if not isinstance(other, Player):
            return NotImplemented
        return all(getattr(self, x) == getattr(other, x) for x in ('owners', 'viewers', 'contents', 'flags'))

    def init(self):
        """
        Function that is called when initializing a new card.  When you subclass Card to make your own card, you
        should set the following attributes:
         - self.val: int
         - self.name: str
         - self.image: str
         - self.flags: set of CardFlag options that apply to this card

         This is the only function that is REQUIRED to be implemented by subclasses.
        """
        raise NotImplementedError("Card has no init function!")

    @property
    def owners(self):
        return immutablize(self._owners)

    @property
    def player(self):
        return immutablize(self._player)

    @property
    def area(self):
        return immutablize(self._area)

    def handle_look(self, kernel, player, area, gamestate):
        """
        This handler is called whenever a player tries to examine ANY area.
        return True to allow the action, False to deny it, or None if you don't care.

        :param kernel: the game's Kernel object
        :param player: the player who's trying to look
        :param area: the Area they're trying to look at
        :param gamestate: the entire state of the game
        :return: True to allow the action, False to deny it, or None if you don't care.
        """
        pass

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        """
        This handler is called whenever a card is moved between ANY Area object in the game.
        This includes drawing, playing, discarding, or moving cards between hands.
        return True to allow the action, False to deny it, or None if you don't care.

        :param kernel: the game's Kernel object
        :param player: the player that's trying to perform the move
        :param card: the card being moved
        :param from_area: the area the card is coming from
        :param to_area: the area the card is heading to
        :param gamestate: the entire state of the game
        :return: True to allow the action, False to deny it, or None if you don't care.
        """
        pass

    def handle_end_turn(self, kernel, player, gamestate):
        """
        This handler is called when ANY player attempts to end their turn.
        Use this to allow a player's turn to end before they draw and play, or cancel their
        turn end so they can do more actions.
        return True to allow the action, False to deny it, or None if you don't care.

        :param kernel: the game's Kernel object
        :param player: the player whose turn is ending
        :param gamestate: the entire state of the game
        :return: True to allow the action, False to deny it, or None if you don't care.
        """
        pass

    def handle_score_area(self, kernel, area, gamestate):
        """
        This handler is called when the score of ANY Area is calculated.  Use it
        to modify what an area's score should be.
        return the score, or None if you don't wish to modify it.

        :param kernel: the game's Kernel object
        :param area: the Area whose score is being calculated
        :param gamestate: the entire state of the game
        :return: the score, or None if you don't wish to modify it
        """
        pass

    def handle_score_card(self, kernel, card, gamestate):
        """
        This handler is called when the score of ANY Card is calculated.
        This can be used to temporarily mask the score of a card.  If you want to
        make a permanent change, see Kernel#get_mutable_card

        :param kernel: the game's Kernel object
        :param card: the Card whose score is being calucalted
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def handle_get_mutable_card(self, kernel, player, card, gamestate):
        """
        This handler is called when ANY card requests ANY mutable (editable) version
        of another card.  Use this to prevent cards from being edited, but note that
        this doesn't prevent other cards from masking this card's true point value
        through other handlers like get_score or score_area.
        return True to allow the action, False to deny it, or None if you don't care

        :param kernel: the game's Kernel object
        :param player: the player that requested the mutable card
        :param card: the card requested
        :param gamestate: the entire state of the game
        :return: True to allow the action, False to deny it, or None if you don't care
        """
        pass

    def handle_end_game(self, kernel, gamestate):
        """
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        :param kernel: the game's Kernel object
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def on_play(self, kernel, gamestate, player):
        pass

    def on_discard(self, kernel, gamestate):
        pass


class CardFlag(Enum):
    PLAY_ANY_TIME = 'Play at any time'
    ALWAYS_GET_EVENTS = 'Get events in any area'


class Area:
    def __init__(self):
        self.owners = []  # players who can play from or are affected by this area
        self.viewers = self.owners  # players who can see the contents of this area
        self.contents = []  # the cards in this area
        self.id = random_id()
        self.flags = set()  # extra data associated with this area

    def __eq__(self, other):
        if not isinstance(other, Player):
            return NotImplemented
        return all(getattr(self, x) == getattr(other, x) for x in ('owners', 'viewers', 'contents', 'flags'))


class AreaFlag(Enum):  # area types
    PLAY_AREA = 'PLAY AREA'
    """
    This flag marks the area as a Play Area, which means that by default, cards in 
    this area will have their callbacks executed.  Also, any moves from a HAND_AREA
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
    count as a "draw", and any moves from a HAND_AREA to PLAY_AREA count as a "play".
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

    def __eq__(self, other):
        if not isinstance(other, Player):
            return NotImplemented
        return all(getattr(self, x) == getattr(other, x) for x in ('username', 'hand', 'area', 'score'))


class Game:
    def __init__(self):
        self.players = {}  # all the players

        self.center = None  # reference to the center
        self.draw = None  # reference to the draw pile
        self.discard = None  # reference to the discard pile
        self.all_areas = {}  # references to *every* area in the game
        self.all_cards = []  # references to each card in the game; as cards are played they are moved towards the front

        self.turn_order = self.players.values()  # normal turn rotation
        self.turn_q = []  # turn rotation override

        self.turn_num = 0  # incremented each turn, mostly for use by cards w/ timers
        self.current_player = None
        self.turn_order_index = 0
        self.cards_played_this_turn = 0
        self.cards_drawn_this_turn = 0
