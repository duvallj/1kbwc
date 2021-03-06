import asyncio
import traceback
from typing import Callable, Tuple, Union

from bwc.objects import *
from bwc.util import immutablize


class Kernel:
    def __init__(self, game: Game, send_message_callback=None, get_player_input_callback=None):
        # Not sure how to annotate types correctly, but
        # await send_message_callback(List[Player], str)
        # await get_player_input_callback(Player, List[str], Callable[[str], None])
        self.__game = game
        self.__send_message_async = send_message_callback
        self.__get_player_input_async = get_player_input_callback

    def __update_card_in_game(self, card: Card):
        """
        When a card is played, it gets bumped to the highest callback priority,
        this attempts to move said card in the game's all_cards list.  Cards
        near the front of the list have their handlers called first

        :param card: the card to be update
        """
        try:
            index = self.__game.all_cards.index(card)
        except ValueError:
            return

        self.__game.all_cards = [card] + self.__game.all_cards[:index] + self.__game.all_cards[index + 1:]

    def __run_card_handler(self, card: Card, handler_str: str, *args):
        """
        Run a Card's handler function.  This will automatically immutablize everything
        in *args to make sure that the card can't modify anything it shouldn't.
        It also passes in Kernel as the default argument.

        :param card: specifies the card whose handler is called
        :param handler_str: the name of the function to call
        :param *args: all remaining args will be passed to the handler
        :return: the return value from the handler call
        """
        immutable_args = [immutablize(arg) for arg in args]
        if AreaFlag.PLAY_AREA in card._area.flags or CardFlag.ALWAYS_GET_EVENTS in card.flags:
            handler = getattr(card, handler_str, None)
            result = None
            try:
                result = handler(self, *immutable_args)
            except AttributeError as e:
                # TODO: do something with the error, like alert the
                # players a card has crashed
                traceback.print_exc()
            return result
        else:
            return None

    def __run_all_hooks(self, hook_str: str, *args):
        """
        Run the function on every card
        For hooks that run after a successful action
        Immutablizes all *args, and passes kernel as first argument

        :param hook_str: the name of the function to run
        :param *args: the args to be passed to the function
        :return:
        """
        immutable_args = [immutablize(arg) for arg in args]
        for card in self.__game.all_cards:
            if AreaFlag.PLAY_AREA in card._area.flags or CardFlag.ALWAYS_GET_EVENTS in card.flags:
                handler = getattr(card, hook_str, None)
                try:
                    handler(self, *immutable_args)
                except Exception:
                    traceback.print_exc()
                    pass

    def __mutablize_obj(self, obj):
        return getattr(obj, "_backing_obj", obj)

    def look_at(self, player: Player, play_area: Area) -> Tuple[bool, Union[int, List[Card]]]:
        """
        Callback for revealing an area to a player
        Polls the cards to see if the operation is allowed
        If no cards return True or False, calls __default_look_handler

        :param player: the player that the area will be revealed to
        :param play_area: the area to be revealed
        :return: contents of the area if allowed, None otherwise
        """
        player = self.__mutablize_obj(player)
        play_area = self.__mutablize_obj(play_area)

        can_look = None

        for card in self.__game.all_cards:
            can_look = self.__run_card_handler(card, "handle_look", player, play_area, self.__game)
            if can_look is not None:
                break

        if can_look is None:
            can_look = self.__default_look_handler(player, play_area)

        if can_look:
            self.__run_all_hooks("on_look", player, play_area, self.__game)
            return True, play_area.contents
        else:
            return False, len(play_area.contents)

    def __default_look_handler(self, player: Player, play_area: Area) -> bool:
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

    def move_card_by_index(self, requestor: Union[Player, Card], index: int, from_area: Area, to_area: Area) -> bool:
        """
        Convenience wrapper for move card; converts the index into a card and calls `move_card`
        Use this method if you want to index cards manually
        It also checks if the card is moving from the draw pile and the draw pile is empty.
        If so, the game is over

        :param requestor: the player or card responsible for the action
        :param index: the index in from_area of the card being moved
        :param from_area: the area the card is being removed from
        :param to_area: the area the card is being added to
        :return: whether the action was performed
        """

        if index >= len(from_area):
            if len(self.__game.draw) == 0 and from_area == self.__game.draw:
                end_game(None)
            return False

        moving_card = from_area[index]
        return move_card(requestor, moving_card, from_area, to_area)

    def move_card(self, requestor: Union[Player, Card], moving_card: Card, from_area: Area, to_area: Area) -> bool:
        """
        Callback for moving a card between play areas
        polls the cards to see if the operation is allowed
        if no cards return True or False, calls __default_move_handler
        if allowed, moves the card

        :param requestor: the player or card responsible for the action
        :param moving_card: the card being moved
        :param from_area: the area the card is being removed from
        :param to_area: the area the card is being added to
        :return: whether the action was performed
        """

        requestor = self.__mutablize_obj(requestor)
        if isinstance(requestor, Player):
            player = requestor
            card_initiated = False
        elif isinstance(requestor, Card):
            player = self.__mutablize_obj(requestor._player)
            card_initiated = True
        else:
            print(f"Unknown move_card requestor {requestor}! Failing \"gracefully\"")
            return False

        moving_card = self.__mutablize_obj(moving_card)
        from_area = self.__mutablize_obj(from_area)
        to_area = self.__mutablize_obj(to_area)

        default_handled = False

        if moving_card not in from_area.contents:
            return False

        if from_area == to_area:
            return False

        can_move = None
        for card in self.__game.all_cards:
            can_move = self.__run_card_handler(card, "handle_move", player, moving_card, from_area, to_area, self.__game)
            if can_move is not None:
                break

        if can_move is None:
            can_move = self.__default_move_handler(requestor, moving_card, from_area, to_area)
            default_handled = True

        if can_move:

            # DISCARD action
            # we call this before the card is moved to the discard pile
            # because once it's discarded it's technically out of play
            if AreaFlag.DISCARD_AREA in to_area.flags and \
                    AreaFlag.DISCARD_AREA not in from_area.flags:
                self.__run_card_handler(moving_card, 'on_discard', self.__game, player)

            # execute action
            index = from_area.contents.index(moving_card)
            from_area.contents = from_area.contents[:index] + from_area.contents[index + 1:]
            to_area.contents = [moving_card] + to_area.contents
            moving_card._owners = to_area.owners
            moving_card._area = to_area

            self.__update_card_in_game(moving_card)
            self.__run_all_hooks('on_move', player, moving_card, from_area, to_area, self.__game)

            # update data

            # Current player is playing
            if AreaFlag.HAND_AREA in from_area.flags and \
                    AreaFlag.PLAY_AREA in to_area.flags and \
                    player in from_area.owners and \
                    player == self.__game.current_player and \
                    CardFlag.PLAY_ANY_TIME not in moving_card.flags and \
                    default_handled and not card_initiated:
                self.__game.cards_played_this_turn += 1

            # PLAY action
            if AreaFlag.PLAY_AREA not in from_area.flags and \
                    AreaFlag.PLAY_AREA in to_area.flags:
                self.__run_card_handler(moving_card, 'on_play', self.__game, player)
                moving_card._player = player
                self.__run_all_hooks('on_play_move', player, moving_card, from_area, to_area, self.__game)

            # DRAW action
            if AreaFlag.DRAW_AREA in from_area.flags and \
                    AreaFlag.HAND_AREA in to_area.flags and \
                    player in to_area.owners and \
                    player == self.__game.current_player and \
                    default_handled and not card_initiated:
                self.__game.cards_drawn_this_turn += 1

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

    def __default_move_handler(self, requestor: Union[Player, Card], card: Card, from_area: Area, to_area: Area) -> bool:
        """
        Checks if a move is allowed based on the current player's turn
        """
        # card's moves are allowed by default
        if isinstance(requestor, Card):
            if CardFlag.NO_PLAY_TO_CENTER in card.flags and \
                    to_area == self.__game.center:
                return False
            if CardFlag.ONLY_PLAY_TO_CENTER in card.flags and \
                    AreaFlag.PLAY_AREA in to_area.flags and \
                    to_area != self.__game.center:
                return False
            return True

        player = requestor

        # player's moves are thoroughly examined
        if AreaFlag.HAND_AREA in from_area.flags and \
                AreaFlag.PLAY_AREA in to_area.flags and \
                player in from_area.owners:
            if CardFlag.ONLY_PLAY_TO_SELF in card.flags and \
                    to_area != player.area:
                return False
            if CardFlag.NO_PLAY_TO_SELF in card.flags and \
                    to_area == player.area:
                return False
            if CardFlag.ONLY_PLAY_TO_CENTER in card.flags and \
                    to_area != self.__game.center:
                return False
            if CardFlag.NO_PLAY_TO_CENTER in card.flags and \
                    to_area == self.__game.center:
                return False
            if CardFlag.PLAY_ANY_TIME in card.flags:
                return True
            elif player == self.__game.current_player and \
                    self.__game.cards_played_this_turn < \
                    self.__game.max_cards_played_this_turn and \
                    self.__game.cards_played_this_turn + \
                    self.__game.cards_drawn_this_turn < \
                    self.__game.max_cards_drawn_this_turn + \
                    self.__game.max_cards_played_this_turn:
                return True

        if AreaFlag.DRAW_AREA in from_area.flags and \
                AreaFlag.HAND_AREA in to_area.flags and \
                player in to_area.owners:
            if player == self.__game.current_player and \
                    (self.__game.cards_drawn_this_turn <
                     self.__game.max_cards_drawn_this_turn or
                     (self.__game.cards_drawn_this_turn <
                      self.__game.max_cards_drawn_this_turn + 1 and
                      self.__game.cards_played_this_turn <
                      self.__game.max_cards_played_this_turn)):
                return True

        return False

    def end_turn(self, player: Player) -> bool:
        """
        Advances to the next turn
        polls the cards to see if the operation is allowed
        if no cards return True or False, calls __default_end_turn_handler
        if allowed, calls the game's advance_turn function

        :param player: the player whose turn is ending
        :return: True/False, whether the action was performed
        """
        player = self.__mutablize_obj(player)

        can_end_turn = None

        for card in self.__game.all_cards:
            can_end_turn = self.__run_card_handler(card, "handle_end_turn", player, self.__game)
            if can_end_turn is not None:
                break

        if can_end_turn is None:
            can_end_turn = self.__default_end_turn_handler(player)

        if can_end_turn:
            self.__run_all_hooks('on_end_turn', player, self.__game)

        return can_end_turn

    def __default_end_turn_handler(self, player: Player) -> bool:
        """
        Checks if the current player has either drawn & played, or drawn twice
        """
        if player == self.__game.current_player:
            if self.__game.cards_drawn_this_turn + \
                    self.__game.cards_played_this_turn >= \
                    self.__game.max_cards_played_this_turn + \
                    self.__game.max_cards_drawn_this_turn:
                return True
            if self.__game.cards_drawn_this_turn >= \
                    self.__game.max_cards_drawn_this_turn + 1 and \
                    len(player.hand.contents) == 0:
                return True
        else:
            print("is not current player")

        return False

    def score_area(self, score_area: Area):
        """
        Gets the score of an area
        polls the cards to see if a custom scoring operation is needed
        if no cards return a score, calls __default_score_area_handler

        :param score_area: the area to score
        :return: the score
        """

        score_area = self.__mutablize_obj(score_area)

        score = None
        default_score = sum(self.score_card(card) for card in score_area.contents)

        for card in self.__game.all_cards:
            score = self.__run_card_handler(card, 'handle_score_area', score_area, default_score, self.__game)

            if score is not None:
                break

        if score is None:
            score = default_score

        self.__run_all_hooks('on_score_area', score_area, score, self.__game)
        return score

    def score_card(self, score_card: Card):
        """
        Gets the score of a card.
        Polls the cards to see if a custom score value should be returned.
        If no cards return a custom score, calls __default_score_card_handler.

        :param score_card: - the card to score
        :return: the score
        """

        score_card = self.__mutablize_obj(score_card)

        score = None

        for card in self.__game.all_cards:
            score = self.__run_card_handler(card, 'handle_score_card', score_card, self.__game)
            if score is not None:
                break

        if score is None:
            # Default is just the defined value
            score = score_card.val

        self.__run_all_hooks('on_score_card', score_card, self.__game)

        return score

    def score_player(self, player: Player):
        """
        Gets a player's score
        By defualt sums all the PLAY_AREAs the player owns
        Polls cards for a custom score

        :param player: the player whose score is calculated
        :return: the score
        """
        player = self.__mutablize_obj(player)

        score = 0
        for area in self.__game.all_areas.values():
            if AreaFlag.PLAY_AREA in area.flags and player in area.owners:
                score += self.score_area(area)

        for card in self.__game.all_cards:
            score_delta = self.__run_card_handler(card, 'handle_score_player', player, score, self.__game)
            if score_delta is not None:
                score += score_delta

        self.__run_all_hooks('on_score_player', player, score, self.__game)

        return score

    def get_mutable_card(self, requestor: Card, requested_card: Card):
        """
        Returns a mutable copy of a card
        polls the cards to see if the requestor is allowed to edit the requested card
        if no cards return a True or False, calls __default_score_card_handler

        :param requestor: the card doing the card request
        :param requested_card: the card the requestor wants a mutable version of
        :return: if allowed, a mutable reference the card, otherwise None
        """

        requestor = self.__mutablize_obj(requestor)
        requested_card = self.__mutablize_obj(requested_card)

        is_allowed = None

        for card in self.__game.all_cards:
            is_allowed = self.__run_card_handler(card, 'handle_get_mutable_card',
                                                 requestor, requested_card, self.__game)
            if is_allowed is not None:
                break

        if is_allowed is None:
            # Default is to allow.
            is_allowed = True

        if is_allowed:  # requested_card has been unimmutablized
            self.__run_all_hooks('on_get_mutable_card', requestor, requested_card, self.__game)
            return requested_card

        return None

    def end_game(self, requestor: Union[Card, None]):
        """
        Ends the game.

        First polls cards to see if the action is allowed, if no card denies it, the game ends

        :param requestor: the card that requested this action (or None if the kernel is
        responsible)
        :return: True if the game ended, False otherwise
        """
    
        if requestor is not None:
            requestor = self.__mutablize_obj(requestor)

        is_allowed = None
        for card in self.__game.all_cards:
            is_allowed = self.__run_card_handler(card, 'handle_end_game', requestor,
                                                 self.__game)
            if is_allowed is not None:
                break

        if is_allowed is None:
            # default is to allow
            is_allowed = True

        if is_allowed:
            self.__game.is_over = True
            self.run_all_hooks('on_end_game', self.__game)

        return is_allowed

    def send_message(self, players: List[Player], message: str) -> bool:
        """
        Send something to a group of selected players!

        :param player: the player who will be saying the message
        :param message: the message to be broadcast to everyone
        :return: whether or not the message was sent
        """
        if self.__send_message_async is not None:
            asyncio.create_task(self.__send_message_async(players, message))
        else:
            print("Warning: kernel can't send_message!")

    def get_player_input(self, player: Player, choices: List[str], callback: Callable[[str], None]):
        """
        Prompt a player with the choices,
        Pause execution until the player makes a choice,
        And return which choice they chose
        :param player: the player to send the choice to
        :param choices: the list of choices the player can choose from
        :param callback: a function that will be called when the player makes their choice
        """
        if self.__get_player_input_async is not None:
            asyncio.create_task(self.__get_player_input_async(player, choices, callback))
        else:
            print("Warning: kernel can't get_player_input!")

    def create_new_area(self, requestor: Card, new_area: Area):
        """
        Add a new area to the game, if poll allows

        :param requestor: the card that initiated this action
        :param new_area: the area to create
        :return: the new area if allowed, or None
        """
        requestor = self.__mutablize_obj(requestor)
        area = Area()  # disallow list for ids: [p.username for p in self.__game.players] + [a.id for a in self.__game.all_areas]
        for owner in new_area.owners:
            area.owners.append(self.__game.players[owner.username])
        for viewer in new_area.viewers:
            area.viewers.append(self.__game.players[viewer.username])
        for content in new_area.contents:
            area.contents.append(self.__mutablize_obj(content))
        if area.id in [p.username for p in self.__game.players.values()] or \
                area.id in [a.id for a in self.__game.all_areas.values()]:  # Add a digit to duplicate ids
            n = 1
            disallowed = [p.username for p in self.__game.players.values()] + [a.id for a in self.__game.all_areas.values()]
            while f"{area.id}{n}" in disallowed:  # No I didn't test this lol it compiles
                n += 1
            area.id = f"{area.id}{n}"
        area.id = self.__mutablize_obj(new_area.id)
        area.flags = self.__mutablize_obj(new_area.flags)

        is_allowed = None

        for card in self.__game.all_cards:
            is_allowed = self.__run_card_handler(card, 'handle_create_new_area',
                                                 requestor, area, self.__game)
            if is_allowed is not None:
                break

        if is_allowed is None:
            # Default is to allow.
            is_allowed = True

        if is_allowed:
            self.__game.all_areas[area.id] = area
            self.__run_all_hooks('on_create_new_area', area, self.__game)
            return area
        return None

    def change_turnorder(self, requestor: Card, new_order: List[Player]):
        """
        Changes the order play rotates
        Polls cards to see if action is allowed first

        :param requestor: the card that requested the change
        :param new_order: the new order to be implemented, any ordered iterable
        :return: if the change was allowed
        """

        requestor = self.__mutablize_obj(requestor)
        order = []
        for p in new_order:
            p = self.__mutablize_obj(p)
            if p not in self.__game.players.values() and p not in order:
                order.append(p)

        is_allowed = None

        for card in self.__game.all_cards:
            is_allowed = self.__run_card_handler(card, 'handle_change_turnorder',
                                                 requestor, order, self.__game)
            if is_allowed is not None:
                break

        if is_allowed is None:
            # Default is to allow.
            is_allowed = True

        if is_allowed:
            if len(order) != len(self.__game.turn_order):
                is_allowed = False
            else:
                self.__game.turn_order = order
                self.__run_all_hooks('on_change_turnorder', order, self.__game)

        return is_allowed

    def change_temporary_turnorder(self, requestor: Card, new_order: List[Player]):
        """
        Appends something to the temporary turn order queue
        Use for, say, allowing a player to take one extra turn after the current one
        Polls cards to see if action is allowed

        :param requestor: the card that requested the change
        :param new_order: the order to be appended to the temporary turn order queue
        :return: if the change was allowed
        """
        requestor = self.__mutablize_obj(requestor)

        is_allowed = None
        order = []
        for p in new_order:
            player = self.__mutablize_obj(p)
            order.append(player)

        for card in self.__game.all_cards:
            is_allowed = self.__run_card_handler(card, 'handle_change_temporary_turnorder',
                                                 requestor, order, self.__game)
            if is_allowed is not None:
                break

        if is_allowed is None:
            # Default is to allow.
            is_allowed = True

        if is_allowed:
            for p in order:
                self.__game.turn_q.append(p)
            self.__run_all_hooks('on_change_temporary_turnorder', self.__game)

        return is_allowed

    def add_card(self, requestor: Card, card_class: Callable[[], Card], to_area: Area):
        """
        Creates a new instance of card_class and adds it to to_area
        First polls all the cards

        :param requestor: the card that requested this action
        :param card_class: the class to instantiate the new card from
        :param to_area: the location to put the new card in
        :return: the added card if allowed, otherwise None
        """
        requestor = self.__mutablize_obj(requestor)
        to_area = self.__mutablize_obj(to_area)
        card_class = self.__mutablize_obj(card_class)

        is_allowed = None

        new_card = card_class()
        new_card._owners = to_area.owners[:]
        new_card._area = to_area

        for card in self.__game.all_cards:
            is_allowed = self.__run_card_handler(card, 'handle_add_card',
                                                 requestor, new_card, to_area, self.__game)
            if is_allowed is not None:
                break

        if is_allowed is None:
            # Default is to allow.
            is_allowed = True

        if is_allowed:
            to_area.contents.append(new_card)
            self.__game.all_cards.append(new_card)
            self.__run_all_hooks('on_add_card', new_card, self.__game)
            return new_card
        return None

    def change_play_limit(self, requestor: Card, new_limit: int):
        """
        Change the number of cards that can be played THIS TURN
        Only affects default move card handler, cards can still allow more movements
        First polls call the cards

        :param requestor: the card that requested this action
        :param new_limit: the new number of play actions this turn
        :return: whether this operation was allowed
        """
        requestor = self.__mutablize_obj(requestor)

        is_allowed = None

        for card in self.__game.all_cards:
            is_allowed = self.__run_card_handler(card, 'handle_change_play_limit', requestor, new_limit, self.__game)
            if is_allowed is not None:
                break

        if is_allowed is None:
            is_allowed = True

        if is_allowed:
            self.__game.max_cards_played_this_turn = new_limit
            self.__run_all_hooks('on_change_play_limit', new_limit, self.__game)
        return is_allowed

    def change_draw_limit(self, requestor: Card, new_limit: int):
        """
        Change the number of cards that can be drawn THIS TURN
        Only affects default move card handler, cards can still allow more movements
        First polls call the cards

        :param requestor: the card that requested this action
        :param new_limit: the new number of draw actions allowed this turn
        :return: whether this operation was allowed
        """
        requestor = self.__mutablize_obj(requestor)

        is_allowed = None

        for card in self.__game.all_cards:
            is_allowed = self.__run_card_handler(card, 'handle_change_draw_limit', requestor, new_limit, self.__game)
            if is_allowed is not None:
                break

        if is_allowed is None:
            is_allowed = True

        if is_allowed:
            self.__game.max_cards_drawn_this_turn = new_limit
            self.__run_all_hooks('on_change_draw_limit', new_limit, self.__game)
        return is_allowed

    def on_turn_start(self):
        """
        Call all the on_turn_start handlers
        """
        self.__run_all_hooks('on_turn_start', self.__game.current_player, self.__game)


    def find_winners(self):
        """
        Find who won the game, and who didn't
        (Spoilers, it's you.  You lost the game...)

        Poll cards for a vote on whether given players won, if nobody interferes find the
        highest-scoring player

        :return: [(Player, winner: bool, score: int)] the players, in order of winningness,
        with the winners tagged and the player's scores included.
        """
        players = []
        for player_name in self.__game.players:
            player = self.__game[player_name]
            score = self.score_player(player)
            winningness = 0
            for card in self.__game.all_cards:
                val = self.__run_card_handler(card, 'handle_winner', player, score,
                                            self.__game)
                if val == True:
                    winningness += 1
                elif val == False:
                    winningness -= 1
            players.append([player, winningness, score])

        use_default = True
        for data in players:
            if data[1] > 0:
                use_default = False

        players = sorted(players, key=lambda data: data[2])
        if use_default:
            players[0][1] += 1

        players = sorted(players, key=lambda data: data[1])

        return [(p[0], p[1] > 0, p[2]) for p in players]
