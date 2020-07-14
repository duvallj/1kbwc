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
        area.id = "UNIT TEST"
        self.exp(kernel.create_new_area(self, area), None)
        self.r = 14
        self.exp(kernel.create_new_area(self, area), area)

        self.r = 1
        self.exp(kernel.move_card(self.owners[0], self, self._area, gamestate.center), False)
        self.r = 2
        self.exp(kernel.move_card(self.owners[0], self, self._area, gamestate.center), True)
        pass

    def handle_look(self, *args):
        print('handle look called')

    def on_look(self, *args):
        print('on look called')

    def handle_move(self, *args):
        if self.r == 1:
            return False
        elif self.r == 2:
            return True
    def on_move(self, *args):
        self.exp(self.r, 2)
    
    def handle_end_turn(self, *args):
        if self.r == 3:
            return False
        elif self.r == 4:
            return True
    def on_end_turn(self, *args):
        self.exp(self.r, 4)

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

    def handle_score_card(self, *args):
        if self.r == 7:
            return None
        if self.r == 8:
            return 2
    def on_score_card(self, *args):
        if self.r != 5 or self.r != 6:
            self.exp(3, 5)
    
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

    def handle_get_mutable_card(self, *args):
        if self.r == 11:
            return False
        if self.r == 12:
            return True
    def on_get_mutable_card(self, *args):
        self.exp(self.r, 12)

    def handle_create_new_area(self, *args):
        if self.r == 13:
            return False
        if self.r == 14:
            return True
    def on_create_new_area(self, *args):
        self.exp(self.r, 14)

    def exp(self, val1, val2):
        if val1 != val2:
            raise NotImplementedError("u r b a d; test failed at " + str(self.r))

