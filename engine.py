import cardreader
from objects import *
from kernel import Kernel

class Engine():
    def __init__(self):
        self.game = None
        self.kernel = None

    def reset(self):
        self.game = Game()
        self.kernel = Kernel(self.game)

    def setup_game(self):
        setup_areas()
        self.game.turn_order = self.game.players[:]
        self.game.current_player = self.game.turn_order(self.game.turn_order_index)        

    def setup_areas(self):
        card_deck = cardreader.make_deck(len(self.game.players) * 10) #MAGIC NUMBER, AAAAA

        # discard
        discard = Area()
        discard.flags = {AreaFlag.DISCARD_AREA}
        self.game.discard = discard
        self.game.all_areas.append(discard)
        
        # center
        center = Area()
        center.owners = self.game.players[:]
        center.viewers = self.game.players[:]
        center.flags = {AreaFlag.PLAY_AREA}
        self.game.center = center
        self.game.all_areas.append(center)

        # players' play areas
        for player in self.game.players:
            area = Area()
            area.owners = [player]
            area.viewers = self.game.players[:]
            area.flags = {AreaFlag.PLAY_AREA}
            player.area = area
            self.game.all_areas.append(area)
        
        # players' hands
        for player in self.game.players:
            hand = Area()
            hand.owners = [player]
            hand.viewers = [player]
            player.hand = hand
            hand.flags = {AreaFlag.HAND_AREA}
            hand.contents = deck[:5]
            deck = deck[5:]
            self.game.all_areas.append(hand)
        
        # draw pile
        draw = Area()
        draw.contents = deck
        draw.flags = {AreaFlag.DRAW_AREA}
        self.game.all_areas.append(draw)

    def add_player(self, username):
        if self.game is None:
            return False

        new_player = Player()
        new_player.username = username
        self.game.players.append(new_player)

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

