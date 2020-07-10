import traceback
from typing import List, Optional
from objects import *
from util import immutablize


class Kernel:
    def __init__(self, game, engine):
        self.__game = game
        self.__engine = engine

    def __update_card_in_game(self, card):
        index = None

        try:
            index = self.__game.all_cards.index(card)
        except ValueError:
            return

        self.__game.all_cards = [card] + self.__game.all_cards[:index] + self.__game.all_cards[index + 1:]

    def __run_card_handler(self, card, handler_str, *args):
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

    def look_at(self, player, play_area) -> Optional[List[Card]]:
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
        if AreaFlag.PLAY_AREA in play_area.flags:
            return True

        if AreaFlag.HAND_AREA in play_area.flags:
            return player in play_area.viewers

        if AreaFlag.DISCARD_AREA in play_area.flags:
            return False

        if AreaFlag.DRAW_AREA in play_area.flags:
            return False

        return True

    def move_card(self, player, card, from_area, to_area) -> bool:
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
        if player is self.__game.current_player:
            if self.__game.cards_drawn_this_turn + \
                    self.__game.cards_played_this_turn >= 2:
                return True

        return False
