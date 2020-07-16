import traceback
from typing import List, Optional, Tuple, Union
from objects import *
from util import immutablize


class Kernel:
    def __init__(self, game):
        self.__game = game

    def __update_card_in_game(self, card):
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

    def __run_card_handler(self, card, handler_str, *args):
        """
        Run a Card's handler function.  This will automatically immutablize everything
        in *args to make sure that the card can't modify anything it shouldn't.
        It also passes in Kernel as the default argument.

        :param card: specifies the card whose handler is called
        :param handler_str: the name of the function to call
        :param *args: all remaining args will be passed to the handler
        :return: the return value from the handler call
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

    def __run_all_hooks(self, hook_str, *args):
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
                if handler is not None:
                    try:
                        handler(self, *immutable_args)
                    except:
                        traceback.print_exc()
                        pass


    def __mutablize_obj(self, obj):
        return getattr(obj, "_backing_obj", obj)

    def look_at(self, player, play_area) -> Tuple[bool, Union[int, List[Card]]]:
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
            if can_look is not None: break

        if can_look is None:
            can_look = self.__default_look_handler(player, play_area)

        if can_look:
            self.__run_all_hooks("on_look", player, play_area, self.__game)
            return True, play_area.contents
        else:
            return False, len(play_area.contents)

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
    def move_card(self, player, moving_card, from_area, to_area) -> bool:
        """
        Callback for moving a card between play areas
        polls the cards to see if the operation is allowed
        if no cards return True or False, calls __default_move_handler
        if allowed, moves the card

        :param player: the player responsible for the action
        :param moving_card: the card being moved
        :param from_area: the area the card is being removed from
        :param to_area: the area the card is being added to
        :return: whether the action was performed
        """

        player = self.__mutablize_obj(player)
        moving_card = self.__mutablize_obj(moving_card)
        from_area = self.__mutablize_obj(from_area)
        to_area = self.__mutablize_obj(to_area)

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
            can_move = self.__default_move_handler(player, moving_card, from_area, to_area)


        if can_move:

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
                    CardFlag.PLAY_ANY_TIME not in moving_card.flags:
                self.__game.cards_played_this_turn += 1
            
            # PLAY action
            if AreaFlag.PLAY_AREA not in from_area.flags and \
                    AreaFlag.PLAY_AREA in to_area.flags:
                self.__run_card_handler(moving_card, 'on_play', self.__game, player)
                moving_card._player = player

            # DRAW action
            if AreaFlag.DRAW_AREA in from_area.flags and \
                    AreaFlag.HAND_AREA in to_area.flags and \
                    player in to_area.owners and \
                    player == self.__game.current_player:
                self.__game.cards_drawn_this_turn += 1

            # DISCARD action
            if AreaFlag.DISCARD_AREA in to_area.flags and \
                    AreaFlag.DISCARD_AREA not in from_area.flags:
                self.__run_card_handler(moving_card, 'on_discard', self.__game, player)
            

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
                    (self.__game.cards_drawn_this_turn < \
                    self.__game.max_cards_drawn_this_turn or \
                    (self.__game.cards_drawn_this_turn < \
                    self.__game.max_cards_drawn_this_turn + 1 and \
                    self.__game.cards_played_this_turn < \
                    self.__game.max_cards_played_this_turn )):
                return True

        return False

    # TODO Check if the game is over (drawpile is empty) in here?
    def end_turn(self, player) -> bool:
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

    def __default_end_turn_handler(self, player) -> bool:
        """
        Checks if the current player has either drawn & played, or drawn twice
        """
        if player == self.__game.current_player:
            print(f"{player.username} Drawn: {self.__game.cards_drawn_this_turn} Played: {self.__game.cards_played_this_turn}")
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

    def score_area(self, score_area):
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


    def get_mutable_card(self, requestor, requested_card):
        """
        Returns a mutable copy of a card
        polls the cards to see if the requestor is allowed to edit the requested card
        if no cards return a True or False, calls __default_score_card_handler

        :paramplayer: the player behind the card request
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

    # TODO this should actually end the game
    def end_game(self):
        """
        Calls card's end_game hooks right before the game ends.
        """
        for card in self.__game.all_cards:
            self.__run_card_handler(card, 'on_end_game', self.__game)

    def send_message(self, players, message):
        """
        Send `message` to each player in `players`
        """
        raise NotImplementedError("PLZ IMPLEMENT")

    def get_player_input(self, player, choices):
        """
        Prompt a player with the choices,
        Pause execution until the player makes a choice,
        And return which choice they chose
        """
        raise NotImplementedError("PLZ IMPLEMENT")

    def create_new_area(self, requestor, new_area):
        """
        Add a new area to the game, if poll allows

        :param requestor: the card that initiated this action
        :param new_area: the area to create
        :return: the new area if allowed, or None
        """
        requestor = self.__mutablize_obj(requestor)
        area = Area()  #disallow list for ids: [p.username for p in self.__game.players] + [a.id for a in self.__game.all_areas]
        for owner in new_area.owners:
            area.owners.append(self.__game.players[owner.username])
        for viewer in new_area.viewers:
            area.viewers.append(self.__game.players[viewer.username])
        for content in new_area.contents:
            area.contents.append(self.__mutablize_obj(content))
        if area.id in [p.username for p in self.__game.players.values()] or \
                area.id in [a.id for a in self.__game.all_areas.values()]:  # Add a digit to duplicate ids
            n = 1
            disallowed = [p.username for p in self.__game.players.values()] + [a.id for a in self.__game.all_areas.values()];
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
    
    def change_turnorder(self, requestor, new_order):
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


    def change_temporary_turnorder(self, requestor, new_order):
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


    def add_card(self, requestor, card_class, to_area):
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


    def change_play_limit(self, requestor, new_limit):
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
    
    def change_draw_limit(self, requestor, new_limit):
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
        for card in self.__game.all_cards:
            self.__run_all_hooks('on_turn_start', self.__game.current_player, self.__game)

