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

    def on_look(self, kernel, player, area, gamestate):
        """
        Called after a successful look request

        :param kernel: the game's Kernel object
        :param player: the player who's looking
        :param area: the Area they'relooking at
        :param gamestate: the entire state of the game
        :return:
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

    def on_move(self, kernel, player, card, from_area, to_area, gamestate):
        """
        Called after a card is successfully moved

        :param kernel: the game's Kernel object
        :param player: the player that's trying to perform the move
        :param card: the card being moved
        :param from_area: the area the card came from
        :param to_area: the area the card was moved to
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def on_play_move(self, kernel, player, card, from_area, to_area, gamestate):
        """
        Called after a card successfully enters play; ease-of-use wrapper called in addition
        to on_move
        * a move is considered a play if a card moves form an area NOT tagged with
        CardFlag.PLAY_AREA to one flagged with CardFlag.PLAY_AREA

        :param kernel: the game's Kernel object
        :param player: the player behind the move action
        :param card: the card that was moved
        :param from_area: the area the card was moved from
        :param to_area: the area the card was moved to
        :param from_area: the area the card was moved from
        :param gamestate: the entire state of the game
        :return:

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

    def on_end_turn(self, kernel, player, gamestate):
        """
        Called after a player's turn ends

        :param kernel: the game's Kernel object
        :param player: the player whose turn ended
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def handle_score_area(self, kernel, area, default_score, gamestate):
        """
        This handler is called when the score of ANY Area is calculated.  Use it
        to modify what an area's score should be.
        return the score, or None if you don't wish to modify it.

        :param kernel: the game's Kernel object
        :param area: the Area whose score is being calculated
        :param default_score: what this area's score would be without intervention
        :param gamestate: the entire state of the game
        :return: the score, or None if you don't wish to modify it
        """
        pass

    def on_score_area(self, kernel, area, score, gamestate):
        """
        Called after an area is scored
        
        :param kernel: the game's Kernel object
        :param area: the Area whose score was calculated
        :param default_score: the calculated score
        :param gamestate: the entire state of the game
        :return:
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
        :return: the score of the card
        """
        pass

    def on_score_card(self, kernel, card, gamestate):
        """
        Called after a card is scored

        :param kernel: the game's Kernel object
        :param card: the Card whose score was calculated
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def handle_score_player(self, kernel, player, default_score, gamestate):
        """
        This handler is called when the score of ANY Player is calculated.  Use it
        to modify what a player's score should be.
        return the score, or None if you don't wish to modify it.

        :param kernel: the game's Kernel object
        :param area: the Player whose score is being calculated
        :param default_score: what this Player's score would be without intervention
        :param gamestate: the entire state of the game
        :return: a DELTA, to be SUMMED with the score, or None if you don't wish to alter it
        """
        pass

    def on_score_player(self, kernel, player, score, gamestate):
        """
        Called after a player's score is calculated

        :param kernel: the game's Kernel object
        :param player: the Player whose score was calculated
        :param score: the calculated score
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def handle_get_mutable_card(self, kernel, requestor, card, gamestate):
        """
        This handler is called when ANY card requests ANY mutable (editable) version
        of another card.  Use this to prevent cards from being edited, but note that
        this doesn't prevent other cards from masking this card's true point value
        through other handlers like get_score or score_area.
        return True to allow the action, False to deny it, or None if you don't care

        :param kernel: the game's Kernel object
        :param requestor: the card that requested the mutable card
        :param card: the card requested
        :param gamestate: the entire state of the game
        :return: True to allow the action, False to deny it, or None if you don't care
        """
        pass

    def on_get_mutable_card(self, kernel, requestor, card, gamestate):
        """
        Called after a successful get_mutable_card_request

        :param kernel: the game's Kernel object
        :param requestor: the card that requested the mutable card
        :param card: the card requested
        :param gamestate: the entire state of the game
        "return"
        """
        pass

    def handle_create_new_area(self, kernel, requestor, new_area, gamestate):
        """
        This handler is called when any card requests a new Area be created

        :param kernel: the game's Kernel object
        :param requestor: the card that requested the area be added
        :param new_area: the area being added
        :param gamestate: the entire state of the game
        :return: True to allow the action, False to deny it, or None if you don't care
        """
        pass

    def on_create_new_area(self, kernel, new_area, gamestate):
        """
        Called after a successful create_new_area request

        :param kernel: the game's Kernel object
        :param new_area: the area that was added
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def handle_change_turnorder(self, kernel, requestor, new_order, gamestate):
        """
        This handler is called when a card requests a change to the play order

        :param kernel: the game's Kernel object
        :param requestor: the card that requested this action
        :param new_order: the proposed new turn order
        :param gamestate: the entire state of the game
        :return: True to allow the action, False to deny it, or None if you don't care
        """
        pass

    def on_change_turnorder(self, kernel, new_order, gamestate):
        """
        Called after a successful change_turnorder request

        :param kernel: the game's Kernel object
        :param new_order: the new turn order
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def handle_change_temporary_turnorder(self, kernel, requestor, new_order, gamestate):
        """
        This handler is called when a card requests a change to the *temporary* play order

        :param kernel: the game's Kernel object
        :param requestor: the card that requested this action
        :param new_order: the proposed new turn order
        :param gamestate: the entire state of the game
        :return: True to allow the action, False to deny it, or None if you don't care
        """
        pass

    def on_change_temporary_turnorder(self, kernel, gamestate):
        """
        Called after a successful change_temporary_turn_order action
        You can access the new turn queue at `gamestate.turn_q`

        :param kernel: the game's Kernel object
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def handle_add_card(self, kernel, requestor, new_card, area, gamestate):
        """
        This handler is called when a card attempts to add a new card to the game

        :param kernel: this game's Kernel object
        :param requestor: the card that requested this action
        :param new_card: the card being added
        :param area: the area the card will be added to
        :param gamestate: the entire state of the game
        :return: True to allow the action, False to deny it, or None if you don't care
        """
        pass

    def on_add_card(self, kernel, new_card, gamestate):
        """
        Called after a successful add_card request

        :param kernel: this game's Kernel object
        :param new_card: the card that was added
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def handle_change_play_limit(self, kernel, requestor, new_limit, gamestate):
        """
        This handler is called when a card attempts to change the number of a cards
        a player can play on their turn

        :param kernel: the game's Kernel object
        :param requestor: the card that requested this action
        :param new_limit: the proposed new limit
        :param gamestate: the entire current state of the game
        :return: whether this action is allowed, or None if you don't care
        """
        pass

    def on_change_play_limit(self, kernel, new_limit, gamestate):
        """
        Called after the play_limit is changed

        :param kernel: the game's Kernel object
        :param requestor: the card that requested this action
        :param new_limit: the new limit applied
        :param gamestate: the entire current state of the game
        :return:
        """
        pass

    def handle_change_draw_limit(self, kernel, requestor, new_limit, gamestate):
        """
        This handler is called when a card attempts to change the number of a cards
        a player can draw on their turn

        :param kernel: the game's Kernel object
        :param requestor: the card that requested this action
        :param new_limit: the proposed new limit
        :param gamestate: the entire current state of the game
        :return: whether this action is allowed, or None if you don't care
        """
        pass

    def on_change_draw_limit(self, kernel, new_limit, gamestate):
        """
        Called after the draw_limit is changed

        :param kernel: the game's Kernel object
        :param requestor: the card that requested this action
        :param new_limit: the new limit applied
        :param gamestate: the entire current state of the game
        :return:
        """
        pass

    def on_end_game(self, kernel, gamestate):
        """
        Called immediately before the game ends

        :param kernel: the game's Kernel object
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def on_turn_start(self, kernel, player, gamestate):
        """
        Called when a player's turn starts

        :param kernel: the game's Kernel object
        :param player: the player whose turn it is
        :param gamestate: the entire state of the game
        :return:
        """
        pass

    def on_play(self, kernel, gamestate, player):
        """
        Ease-of-use handler, called after ONLY THIS card is successfully played (defined
        as moving from a non play area to a play area)
        If you wish to be able to stop this card from being played, use handle_move instead

        :param kernel: the game's Kernel object
        :param gamestate: the entire state of the game
        :param player: the player that played this card, equivalent to self.player
        :return:
        """
        pass

    def on_discard(self, kernel, gamestate, discarder):
        """
        Ease-of-use handler, called when ONLY THIS card is discarded (defined as moved into
        a discard area) this method is run before the card is moved to the discard pile,
        so you can access the fields as if it were in play
        If you wish to be able to stop this card from being moved, use handle_move instead
        !! IMPORTANT: cards can be discarded from *any* area, don't assume it was last in
        a play area!

        :param kernel: the game's Kernel object
        :param gamestate: the entire state of the game
        :param discarder: the player responsible for discarding this card, NOT self.player
        :return:
        """
        pass

