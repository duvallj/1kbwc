import traceback
from typing import List, Optional
from objects import *
from util import immutablize


class Kernel:
    def __init__(self, game, engine):
        self.__game = game
        self.__engine = engine

    def __update_card_in_game(self, card):
        """
        When a card is played, it gets bumped to the highest callback priority
        * this attempts to move said card in the game's all_cards list
        """
        index = None

        try:
            index = self.__game.all_cards.index(card)
        except ValueError:
            return

        self.__game.all_cards = [card] + self.__game.all_cards[:index] + self.__game.all_cards[index + 1:]

    def __run_card_handler(self, card, handler_str, *args):
        """
        Run a Card's handler function
        -> card specifies the card whose handler is called
        -> handler_str is the name of the function to call
        -> *args is all args to be passed to the handler

        * automatically immutablizes everything in *args before passing it on
        * automatically passes self (this Kernel) as the first argument

        <- returns the return value from the handler call
        """
        if AreaFlag.PLAY_AREA in card._area.flags or CardFlag.ALWAYS_GET_EVENTS in card.flags:
            handler = getattr(card, handler_str, None)
            result = None
            if handler is not None:
                immutable_args = [immutablize(arg) for arg in args]
                try:
                    result = handler(self, *immutable_args)
                except AttributeError as e:
                    # TODO: do something with the error, like alert the
                    # players a card has crashed
                    traceback.print_exc()
            return result
        else:
            return None
    #TODO should we give client's some form of IDing areas without giving them access to contents?
    def look_at(self, player, play_area) -> Optional[List[Card]]:
        """
        Callback for revealing an area to a player
        -> player is the player that the area will be revealed to
        -> play_area is the area to be revealed

        * polls the cards to see if the operation is allowed
        * if no cards return True or False, calls __default_look_handler

        <- if allowed, returns the contents of the area
        """
        can_look = None

        for card in self.__game.all_cards:
            can_look = self.__run_card_handler(card, "handle_look", player, play_area, self.__game)
            if can_look is not None: break

        if can_look is None:
            can_look = self.__default_look_handler(player, play_area)

        if can_look:
            return play_area.cards
        else:
            return None

    def __default_look_handler(self, player, play_area) -> bool:
        """
        Default test if looking at an area is allowed
        """
        if AreaFlag.PLAY_AREA in play_area.flags:
            return True

        if AreaFlag.HAND_AREA in play_area.flags:
            return player in play_area.viewers

        if AreaFlag.DISCARD_AREA in play_area.flags:
            return False

        if AreaFlag.DRAW_AREA in play_area.flags:
            return False

        return True

    # TODO ordering in areas - from top of draw pile or to top of discard pile????
    def move_card(self, player, card, from_area, to_area) -> bool:
        """
        Callback for moving a card between play areas
        -> player is the player responsible for the action
        -> card is the card being moved
        -> from_area is the area the card is being removed from
        -> to_area is the area the card is being added to

        * polls the cards to see if the operation is allowed
        * if no cards return True or False, calls __default_move_handler
        * if allowed, moves the card and

        <- returns whether the action was performed
        """
        if card not in from_area.cards:
            return False

        if from_area is to_area:
            return False

        can_move = None
        for card in self.__game.all_cards:
            can_move = self.__run_card_handler(card, "handle_move", player, card, from_area, to_area, self.__game)
            if can_move is not None: break

        if can_move is None:
            can_move = self.__default_move_handler(player, card, from_area, to_area)

        if AreaFlag.HAND_AREA in from_area.flags and \
                AreaFlag.PLAY_AREA in to_area.flags and \
                player in from_area.owners and \
                player is self.__game.current_player and \
                CardFlag.PLAY_ANY_TIME not in card.flags:
            self.__game.cards_played_this_turn += 1

        if AreaFlag.DRAW_AREA in from_area.flags and \
                AreaFlag.HAND_AREA in to_area.flags and \
                player in to_area.owners and \
                player is self.__game.current_player:
            self.__game.cards_drawn_this_turn += 1

        if can_move:
            index = from_area.cards.index(card)
            from_area.cards = from_area.cards[:index] + from_area.cards[index + 1:]
            to_area.cards = [card] + to_area.cards
            card._owners = to_area.owners

            self.__update_card_in_game(card)

        return can_move

    """
    Requires:
    * card in from_area
    * from_area is not to_area
    * card not in to_area
    Ensures:
    * Returns true ==> card in to_area and card not in from_area
    * Returns false ==> card in from_area and card not in to_area
    """

    def __default_move_handler(self, player, card, from_area, to_area) -> bool:
        """
        Checks if a move is allowed based on the current player's turn
        """
        if AreaFlag.HAND_AREA in from_area.flags and \
                AreaFlag.PLAY_AREA in to_area.flags and \
                player in from_area.owners:
            if CardFlag.PLAY_ANY_TIME in card.flags:
                return True
            elif player is self.__game.current_player and \
                    self.__game.cards_played_this_turn == 0 and \
                    self.__game.cards_drawn_this_turn < 2:
                return True

        if AreaFlag.DRAW_AREA in from_area.flags and \
                AreaFlag.HAND_AREA in to_area.flags and \
                player in to_area.owners:
            if player is self.__game.current_player and \
                    (self.__game.cards_drawn_this_turn == 0 or
                     (self.__game.cards_drawn_this_turn == 1 and
                      self.__game.cards_played_this_turn == 0)):
                return True

        return False

    # TODO Check if the game is over (drawpile is empty) in here?
    def end_turn(self, player) -> bool:
        """
        Advances to the next turn
        -> player - the player whose turn is ending

        * polls the cards to see if the operation is allowed
        * if no cards return True or False, calls __default_end_turn_handler
        * if allowed, calls the game's advance_turn function

        <- returns whether the action was performed
        """
        can_end_turn = None

        for card in self.__game.all_cards:
            can_end_turn = self.__run_card_handler(card, "handle_end_turn", player, self.__game)
            if can_end_turn is not None:
                break

        if can_end_turn is None:
            can_end_turn = self.__default_end_turn_handler(player)

        if can_end_turn:
            self.__engine.advance_turn()

        return can_end_turn

    def __default_end_turn_handler(self, player) -> bool:
        """
        Checks if the current player has either drawn & played, or drawn twice
        """
        if player is self.__game.current_player:
            if self.__game.cards_drawn_this_turn + \
                    self.__game.cards_played_this_turn >= 2:
                return True

        return False

    def score_area(self, score_area):
        """
        Gets the score of an area
        -> score_area - the area to score

        * polls the cards to see if a custom scoring operation is needed
        * if no cards return a score, calls __default_score_area_handler
    
        <- returns the score
        """
        score = None

        for card in self.__game.all_cards:
            score = self.__run_card_handler(card, 'handle_score_area', score_area, self.__game)

            if score is not None:
                break

        if score is None:
            score = self.__default_score_area_handler(score_area)

        return score

    def __default_score_area_handler(self, score_area):
        """
        Loops through the cards in an area and calls the score_card callback on each
        """
        score = 0

        for card in score_area.contents:
            score += self.score_card(card)

        return score

################ TODO / WARNING: SHOULD THE SCORE_CARD HOOK EXIST OR CAN IT BE DEPRECATED IN FAVOR OF ALWAYS USING Card.val AND WOULD-BE-HANDLERS USING `get_mutable_card` AND CHANGING THE Card.val FIELD????????????????

    def score_card(self, score_card):
        """
        Gets the score of a card
        -> score_card - the area to score

        * polls the cards to see if a custom score value should be returned
        * if no cards return a custom score, calls __default_score_card_handler
    
        <- returns the score
        """
        score = None

        for card in self.__game.all_cards:
            score = self.__run_card_handler(card, 'handle_score_card', score_card, self.__game)
            if score is not None:
                break

        if score is None:
            score = self.__default_score_card_handler(score_card)

        return score

    def __default_score_card_handler(self, score_card):
        """
        Bruh, we don't need a docstring here.  The docstring is longer than the method
        """
        return score_card.val

    # TODO What should this return if request is denied?
    def get_mutable_card(self, player, requested_card):
        """
        Returns a mutable copy of a card
        -> player, the player behind the card request
        -> requested_card, the card the requestor wants a mutable version of
        
        * polls the cards to see if the requestor is allowed to edit the requested card
        * if no cards return a True or False, calls __default_score_card_handler

        <- if allowed, returns a mutable reference the card, otherwise None
        """
        pass

    # TODO What actually is the default response to a mutable card request?  Allow it?
    def __default_get_mutable_card_handler(self, player, requested_card):
        """
        """
        pass

    def end_game(self):
        """
        Calls card's end_game hooks right before the game ends.
        """
        for card in self.__game.all_cards:
            self.__run_card_handler(self, 'handle_end_game', self.__game)
