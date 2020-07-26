## THIS API FILE IS FOR REFERENCE ONLY; IT IS NOT AN IMPLEMENTATION

# below are the methods cards can invoke on a game's Kernel

```
class Kernel:
    def look_at(self, player: Player, play_area: Area) -> Tuple[bool, Union[int, List[Card]]]:
        """
        Callback for revealing an area to a player
        Polls the cards to see if the operation is allowed
        If no cards return True or False, calls __default_look_handler

        :param player: the player that the area will be revealed to
        :param play_area: the area to be revealed
        :return: contents of the area if allowed, None otherwise
        """

    def move_card(self, requestor: Union[Player, Card], moving_card: Card, from_area: Area, to_area: Area) -> bool:
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

    # TODO Check if the game is over (drawpile is empty) in here?
    def end_turn(self, player: Player) -> bool:
        """
        Advances to the next turn
        polls the cards to see if the operation is allowed
        if no cards return True or False, calls __default_end_turn_handler
        if allowed, calls the game's advance_turn function
        
        :param player: the player whose turn is ending
        :return: True/False, whether the action was performed
        """

    def score_area(self, score_area: Area):
        """
        Gets the score of an area
        polls the cards to see if a custom scoring operation is needed
        if no cards return a score, calls __default_score_area_handler
        
        :param score_area: the area to score
        :return: the score
        """

    def score_card(self, score_card: Card):
        """
        Gets the score of a card.
        Polls the cards to see if a custom score value should be returned.
        If no cards return a custom score, calls __default_score_card_handler.

        :param score_card: - the card to score
        :return: the score
        """

    def score_player(self, player: Player):
        """
        Gets a player's score
        By defualt sums all the PLAY_AREAs the player owns
        Polls cards for a custom score

        :param player: the player whose score is calculated
        :return: the score
        """

    def get_mutable_card(self, requestor: Card, requested_card: Card):
        """
        Returns a mutable copy of a card
        polls the cards to see if the requestor is allowed to edit the requested card
        if no cards return a True or False, calls __default_score_card_handler

        :param requestor: the card doing the card request
        :param requested_card: the card the requestor wants a mutable version of
        :return: if allowed, a mutable reference the card, otherwise None
        """

    # TODO this should actually end the game
    def end_game(self):
        """
        Calls card's end_game hooks right before the game ends.
        """

    def send_message(self, players: List[Player], message: str) -> bool:
        """
        Send something to a group of selected players!

        :param player: the player who will be saying the message
        :param message: the message to be broadcast to everyone
        :return: whether or not the message was sent
        """

    def get_player_input(self, player: Player, choices: List[str], callback: Callable[[str], None]):
        """
        Prompt a player with the choices,
        Pause execution until the player makes a choice,
        And return which choice they chose
        :param player: the player to send the choice to
        :param choices: the list of choices the player can choose from
        :param callback: a function that will be called when the player makes their choice
        """

    def create_new_area(self, requestor: Card, new_area: Area):
        """
        Add a new area to the game, if poll allows

        :param requestor: the card that initiated this action
        :param new_area: the area to create
        :return: the new area if allowed, or None
        """

    def change_turnorder(self, requestor: Card, new_order: List[Player]):
        """
        Changes the order play rotates
        Polls cards to see if action is allowed first

        :param requestor: the card that requested the change
        :param new_order: the new order to be implemented, any ordered iterable
        :return: if the change was allowed
        """

    def change_temporary_turnorder(self, requestor: Card, new_order: List[Player]):
        """
        Appends something to the temporary turn order queue
        Use for, say, allowing a player to take one extra turn after the current one
        Polls cards to see if action is allowed

        :param requestor: the card that requested the change
        :param new_order: the order to be appended to the temporary turn order queue
        :return: if the change was allowed
        """

    def add_card(self, requestor: Card, card_class: Callable[[], Card], to_area: Area):
        """
        Creates a new instance of card_class and adds it to to_area
        First polls all the cards

        :param requestor: the card that requested this action
        :param card_class: the class to instantiate the new card from
        :param to_area: the location to put the new card in
        :return: the added card if allowed, otherwise None
        """

    def change_play_limit(self, requestor: Card, new_limit: int):
        """
        Change the number of cards that can be played THIS TURN
        Only affects default move card handler, cards can still allow more movements
        First polls call the cards
        
        :param requestor: the card that requested this action
        :param new_limit: the new number of play actions this turn
        :return: whether this operation was allowed
        """

    def change_draw_limit(self, requestor: Card, new_limit: int):
        """
        Change the number of cards that can be drawn THIS TURN
        Only affects default move card handler, cards can still allow more movements
        First polls call the cards
        
        :param requestor: the card that requested this action
        :param new_limit: the new number of draw actions allowed this turn
        :return: whether this operation was allowed
        """

    def on_turn_start(self):
        """
        Call all the on_turn_start handlers
        """
```