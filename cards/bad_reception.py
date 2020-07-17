from objects import Card


class bad_reception(Card):
    def init(self):
        self.val = -100
        self.name = 'Bad Reception'
        self.image = 'BadReception.png'
        self.flags = set()
        self.tags = {"Technology"}
        self.turnsLeft = {}
        self.active = False

    def on_play(self, kernel, gamestate, player):
        '''
        Ease-of-use handler, called after ONLY THIS card is successfully played (defined
        as moving from a non play area to a play area)
        If you wish to be able to stop this card from being played, use handle_move instead

        :param kernel: the game's Kernel object
        :param gamestate: the entire state of the game
        :param player: the player that played this card, equivalent to self.player
        :return:
        '''
        self.turnsLeft = {};
        for p in self.owners:
            self.turnsLeft[p.username] = 2
        self.active = True

    def on_turn_start(self, kernel, player, gamestate):
        '''
        Called when a player's turn starts

        :param kernel: the game's Kernel object
        :param player: the player whose turn it is
        :param gamestate: the entire state of the game
        :return:
        '''
        if self.active:
            if player.username in self.turnsLeft:
                if self.turnsLeft[player.username] > 0:
                    self.turnsLeft[player.username] -= 1
                    currMax = gamestate.max_cards_drawn_this_turn
                    if currMax > 0 and kernel.change_draw_limit(self, currMax - 1):
                        kernel.send_message([player], f"{self.name} prevented you from drawing a card this turn!")
