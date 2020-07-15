from objects import Card


class Blast_Furnace(Card):
    def init(self):
        self.val = 50
        self.name = 'Blast Furnace'
        self.image = 'Blast_Furnace.png'
        self.flags = set()
        self.active = -1
        self.tags = {'Metallurgy'}

    def on_move(self, kernel, player, card, from_area, to_area, gamestate):
        print("BF on_move called....")
        if to_area == self.area and self.active == -1:
            print("card played to this area; doing a move!")
            self.active = 1
            print(f"card bein moved: {gamestate.draw.contents[0]}")
            kernel.move_card(self.owners[0], gamestate.draw.contents[0], gamestate.draw, self.area)
        print("BF resetting")
        self.active = -1

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        print("BF handle_move called")
        if self.active == 1:
            print(" is active...")
            if player == self.owners[0]:
                print("  player is correct")
                print(f'{card, gamestate.draw.contents[0]}')
                if card == gamestate.draw.contents[0]:
                    print("   card is from top of deck, returning true!")
                    self.active += 1
                    return True
