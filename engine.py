import cardreader
from objects import *
from kernel import Kernel
from os import listdir


class Engine:
    def __init__(self):
        self.game = None
        self.kernel = None

    def reset(self, send_message, get_player_input):
        self.game = Game()
        self.kernel = Kernel(self.game, send_message, get_player_input)

    def setup_game(self):
        self.setup_areas()
        self.game.turn_order = list(self.game.players.values())
        self.game.current_player = self.game.turn_order[self.game.turn_order_index]

    def setup_areas(self):
        card_deck = cardreader.make_deck(len(self.game.players) * 20)  # MAGIC NUMBER, AAAAA
        self.game.all_cards = card_deck[:]

        # discard
        discard = Area()
        discard.id = "discard"
        discard.flags = {AreaFlag.DISCARD_AREA}
        self.game.discard = discard
        self.game.all_areas[discard.id] = discard

        # center
        center = Area()
        center.owners = list(self.game.players.values())
        center.viewers = list(self.game.players.values())
        center.id = "center"
        center.flags = {AreaFlag.PLAY_AREA}
        self.game.center = center
        self.game.all_areas[center.id] = center

        # players' play areas
        for player in self.game.players.values():
            area = Area()
            area.owners = [player]
            area.viewers = list(self.game.players.values())
            area.id = f'{player.username}.play'
            area.flags = {AreaFlag.PLAY_AREA}
            player.area = area
            self.game.all_areas[area.id] = area

        # players' hands
        for player in self.game.players.values():
            hand = Area()
            hand.owners = [player]
            hand.viewers = [player]
            player.hand = hand
            hand.flags = {AreaFlag.HAND_AREA}
            hand.id = f'{player.username}.hand'
            hand.contents = card_deck[:5]
            for card in hand.contents:
                card._area = hand
                card._owner = player
            card_deck = card_deck[5:]
            self.game.all_areas[hand.id] = hand

        # draw pile
        draw = Area()
        draw.contents = card_deck
        for card in draw.contents:
            card._area = draw
        draw.id = "drawpile"
        draw.flags = {AreaFlag.DRAW_AREA}
        self.game.draw = draw
        self.game.all_areas[draw.id] = draw

        # D E B U G M O D E
        if 'DEBUG' in listdir('.'):
            extra_cards = cardreader.make_deck()
            self.game.all_cards += extra_cards
            player = list(self.game.players.values())[0]
            player.hand.contents += extra_cards
            for card in player.hand.contents:
                card._area = player.hand
                card._owner = player

    def add_player(self, username):
        if self.game is None:
            return False

        new_player = Player()
        new_player.username = username
        self.game.players[username] = new_player

    def remove_player(self, username):
        # TODO: actually remove the player from the game
        pass

    def advance_turn(self):
        self.game.turn_num += 1

        self.game.max_cards_played_this_turn = 1
        self.game.max_cards_drawn_this_turn = 1
        self.game.cards_played_this_turn = 0
        self.game.cards_drawn_this_turn = 0

        if len(self.game.turn_q) > 0:
            self.game.current_player = self.game.turn_q[0]
            self.game.turn_q = self.game.turn_q[1:]
        else:
            self.game.turn_order_index = (self.game.turn_order_index + 1) % len(self.game.turn_order)
            self.game.current_player = self.game.turn_order[self.game.turn_order_index]

        self.kernel.on_turn_start()

    def is_game_over(self):
        return len(self.game.draw.contents) == 0

    def get_player(self, player_name):
        if player_name in self.game.players:
            return self.game.players[player_name]
        return None

    def get_area(self, area_name):
        if area_name in self.game.all_areas:
            return self.game.all_areas[area_name]
        return None
