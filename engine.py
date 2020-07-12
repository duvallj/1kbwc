import cardreader
from objects import *
from kernel import Kernel


class Engine:
    def __init__(self):
        self.game = None
        self.kernel = None

    def reset(self):
        self.game = Game()
        self.kernel = Kernel(self.game, self)

    def setup_game(self):
        self.setup_areas()
        self.game.turn_order = self.game.players[:]
        self.game.current_player = self.game.turn_order[self.game.turn_order_index]

    def setup_areas(self):
        card_deck = cardreader.make_deck(len(self.game.players) * 10)  # MAGIC NUMBER, AAAAA

        # discard
        discard = Area()
        discard.id = "discard"
        discard.flags = {AreaFlag.DISCARD_AREA}
        self.game.discard = discard
        self.game.all_areas[discard.id] = discard

        # center
        center = Area()
        center.owners = self.game.players[:]
        center.viewers = self.game.players[:]
        center.id = "center"
        center.flags = {AreaFlag.PLAY_AREA}
        self.game.center = center
        self.game.all_areas[center.id] = center

        # players' play areas
        for player in self.game.players:
            area = Area()
            area.owners = [player]
            area.viewers = self.game.players[:]
            area.id = f'{player.username}_play'
            area.flags = {AreaFlag.PLAY_AREA}
            player.area = area
            self.game.all_areas[area.id] = area

        # players' hands
        for player in self.game.players:
            hand = Area()
            hand.owners = [player]
            hand.viewers = [player]
            player.hand = hand
            hand.flags = {AreaFlag.HAND_AREA}
            hand.id = f'{player.username}_hand'
            hand.contents = card_deck[:5]
            deck = card_deck[5:]
            self.game.all_areas[hand.id] = hand

        # draw pile
        draw = Area()
        draw.contents = card_deck
        draw.id = "drawpile"
        draw.flags = {AreaFlag.DRAW_AREA}
        self.game.draw = draw
        self.game.all_areas[draw.id] = draw

    def add_player(self, username):
        if self.game is None:
            return False

        new_player = Player()
        new_player.username = username
        self.game.players[username] = new_player

    def advance_turn(self):
        self.game.turn_num += 1
        self.game.cards_played_this_turn = 0
        self.game.cards_drawn_this_turn = 0
        if len(self.game.turn_q) > 0:
            self.game.current_player = self.game.turn_q[0]
            self.game.turn_q = self.game.turn_q[1:]
        else:
            self.game.turn_order_index = (self.game.turn_order_index + 1) % len(self.game.turn_order)
            self.game.current_player = self.game.turn_order[self.game.turn_order_index]

    def is_game_over(self):
        return len(self.game.draw.contents) == 0

    def get_player(self, player_name):
        if player_name in self.game.players:
            return self.game.players[player_name]
        return None

    def get_area(self, area_name):
        if area_name in self.all_areas:
            return self.game.areas[area_name]
        return None
