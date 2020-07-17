from objects import Card, CardFlag
from server_rendering import format_player
import random

class Ene(Card):
    def init(self):
        self.val = 0
        self.name = 'Ene'
        self.image = 'Ene.jpg'
        self.flags = set()
        self.active_player = None
        self.target_player = None

    def on_turn_start(self, kernel, current_player, game):
        self.active_player = None
        self.target_player = None

        def on_choice(choice):
            self.target_player = game.players[choice]
            kernel.send_message(list(game.players.values()), f"[Ene] {format_player(current_player.username)} is playing a card from {format_player(choice)}'s hand!")

        # See if they want to play from someone else's hand
        if current_player in self.owners:
            self.active_player = current_player
            kernel.send_message([current_player], "[Ene] Which hand would you like to play a card from?")
            kernel.get_player_input(current_player, list(game.players.keys()), on_choice) 


    def handle_move(self, kernel, player, moving_card, from_area, to_area, game):
        if self.active_player == player and \
           self.target_player is not None and \
           from_area == self.target_player.hand:
            # Decrement the play limit by one to count this as a play
            kernel.change_play_limit(self, game.max_cards_played_this_turn - 1)
            return True

    def handle_look(self, kernel, player, area, game):
        if self.active_player == player and \
           self.target_player is not None and \
           area == self.target_player.hand:
            return True
