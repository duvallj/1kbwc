from objects import Card, Area

class UnitTest(Card):
    def init(self):
        self.val = 200
        self.name = 'Unit Test'
        self.image = 'UnitTest.jpg'
        self.flags = set()
        self.r = 0
        self.d = set()

    def on_play(self, kernel, gamestate, player):

        self.r = 3
        self.exp(kernel.end_turn(self.owners[0]), False)
        self.r = 4
        self.exp(kernel.end_turn(self.owners[0]), True)

        self.r = 5
        self.exp(kernel.score_area(self.area), 200)
        self.r = 6
        self.exp(kernel.score_area(self.area), 2)

        self.r = 7
        self.exp(kernel.score_card(self), 200)
        self.r = 8
        self.exp(kernel.score_card(self), 2)

        self.r = 9
        self.exp(kernel.score_player(self.owners[0]), 200)
        self.r = 10
        self.exp(kernel.score_player(self.owners[0]), 2)

        self.r = 11
        self.exp(kernel.get_mutable_card(self, self), None)
        self.r = 12
        self.exp(kernel.get_mutable_card(self, self), self)

        self.r = 13
        area = Area()
        area.id = "UNIT_TEST"
        area.contents = [self]
        self.exp(kernel.create_new_area(self, area), None)
        self.r = 14
        self.exp(kernel.create_new_area(self, area), area)

        self.r = 15
        self.exp(kernel.change_turnorder(self, self.owners), False)
        self.r = 16
        kernel.change_turnorder(self, self.owners)
        self.exp(gamestate.turn_order, self.owners)

        self.r = 17
        self.exp(kernel.change_temporary_turnorder(self, self.owners), False)
        self.r = 18
        self.exp(kernel.change_temporary_turnorder(self, self.owners), True)
        self.exp(gamestate.turn_q, self.owners)

        self.r = 19
        self.exp(kernel.add_card(self, type(self), gamestate.center), None)
        self.r = 20
        self.exp(type(kernel.add_card(self, type(self), gamestate.center)), type(self))

        self.r = 21
        self.exp(kernel.change_play_limit(self, 3), False)
        self.exp(1, self.gamestate.max_cards_played_this_turn)
        self.r = 22
        self.exp(kernel.change_play_limit(self, 3), True)
        self.exp(3, self.gamestate.max_cards_played_this_turn)

        self.r = 23
        self.exp(kernel.change_draw_limit(self, 4), False)
        self.exp(1, self.gamestate.max_cards_drawn_this_turn)
        self.r = 24
        self.exp(kernel.change_draw_limit(self, 4), True)
        self.exp(4, self.gamestate.max_cards_drawn_this_turn)

        self.r = 1
        self.exp(kernel.move_card(self.owners[0], self, self._area, gamestate.center), False)
        self.r = 2
        self.exp(kernel.move_card(self.owners[0], self, self._area, gamestate.center), True)

        self.r = 99
        kernel.move_card(self.owners[0], self, self.area, gamestate.discard)

        self.r = 100
        kernel.end_game()

        self.d.add(0)
        for x in range(16):
            if x not in self.d:
                self.exp(0, 15)
        if len(self.d) != 16:
            self.exp(0, 16)
        pass

    def handle_look(self, *args):
        print('handle look called')

    def on_look(self, *args):
        self.d.add(1)
        print('on look called')

    def handle_move(self, *args):
        if self.r == 1:
            return False
        elif self.r == 2:
            return True
    def on_move(self, *args):
        self.exp(self.r, 2)
        self.d.add(2)
    
    def handle_end_turn(self, *args):
        if self.r == 3:
            return False
        elif self.r == 4:
            return True
    def on_end_turn(self, *args):
        self.exp(self.r, 4)
        self.d.add(3)

    def handle_score_area(self, *args):
        if self.r == 5:
            return None
        if self.r == 6:
            return 2
    def on_score_area(self, kernel, area, score, *args):
        if self.r == 5:
            self.exp(score, 200)
        if self.r == 6:
            self.exp(score, 2)
        self.d.add(4)

    def handle_score_card(self, *args):
        if self.r == 7:
            return None
        if self.r == 8:
            return 2
    def on_score_card(self, *args):
        if self.r != 5 or self.r != 6:
            self.exp(3, 5)
        self.d.add(5)
    
    def handle_score_player(self, *args):
        if self.r == 9:
            return None
        if self.r == 10:
            return -198
    def on_score_player(self, kernel, player, score, *args):
        if self.r == 9:
            self.exp(score, 200)
        if self.r == 10:
            self.exp(score, 2)
        self.d.add(6)

    def handle_get_mutable_card(self, *args):
        if self.r == 11:
            return False
        if self.r == 12:
            return True
    def on_get_mutable_card(self, *args):
        self.exp(self.r, 12)
        self.d.add(7)

    def handle_create_new_area(self, *args):
        if self.r == 13:
            return False
        if self.r == 14:
            return True
    def on_create_new_area(self, *args):
        self.exp(self.r, 14)
        self.d.add(8)

    def handle_change_turnorder(self, *args):
        if self.r == 15:
            return False
        if self.r == 16:
            return True
    def on_change_turnorder(self, *args):
        self.exp(self.r, 16)
        self.d.add(9)

    def handle_change_temporary_turnorder(self, *args):
        if self.r == 17:
            return False
        if self.r == 18:
            return True
    def on_change_temporary_turnorder(self, *args):
        self.exp(self.r, 18)
        self.d.add(10)

    def handle_add_card(self, *args):
        if self.r == 19:
            return False
        if self.r == 20:
            return True
    def on_add_card(self, *args):
        self.exp(self.r, 20)
        self.d.add(11)

    def handle_change_play_limit(self, *args):
        if self.r == 21:
            return False
        if self.r == 22:
            return True
    def on_change_play_limit(self, *args):
        self.exp(self.r, 22)
        self.d.add(12)
    
    def handle_change_draw_limit(self, *args):
        if self.r == 23:
            return False
        if self.r == 24:
            return True
    def on_change_draw_limit(self, *args):
        self.exp(self.r, 24)
        self.d.add(13)

    def on_discard(self, *args):
        self.exp(self.r, 99)
        self.d.add(14)

    def on_end_game(self, *args):
        self.exp(self.r, 100)
        self.d.add(15)

    def exp(self, val1, val2):
        if val1 != val2:
            raise NotImplementedError("u r b a d; test failed at " + str(self.r))

