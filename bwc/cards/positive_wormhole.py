import random

from bwc.objects import Card


class positive_wormhole(Card):
    def init(self):
        self.val = 300
        self.name = 'Positive Wormhole'
        self.image = 'positive_wormhole.png'
        self.flags = set()
        self.tags = set()

    def on_turn_start(self, kernel, player, gamestate):
        '''
        Called when a player's turn starts

        :param kernel: the game's Kernel object
        :param player: the player whose turn it is
        :param gamestate: the entire state of the game
        :return:
        '''
        for player in self.owners:
            def closure(own):
                to_move = random.choice(gamestate.all_cards)

                def callback(choice):
                    if choice == 'In your hand':
                        kernel.move_card(self, to_move, to_move.area, own.hand)
                    else:
                        kernel.move_card(self, to_move, to_move.area, own.area)

                kernel.send_message([own], f'Where do you want to put {to_move.name}?')
                kernel.get_player_input(own, ['In your play area', 'In your hand'], callback)

            closure(player)
