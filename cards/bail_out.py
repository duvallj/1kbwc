from objects import Card


class Bail_Out(Card):
    def init(self):
        self.val = -200
        self.name = 'Bail-Out'
        self.image = 'Bail-Out.png'
        self.flags = set()

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        print("BO got handle_move!")
        print(f'{self.owners, player}')
        print(f'{self.owners[0] == player}')
        if player in self.owners:
            print(" move is from this card's owner...")
            if from_area == player.hand:
                print("  and it's from the ower's hand...")
                if to_area == gamestate.draw:
                    print("   and it's going to the draw pile.  Allow action!")
                    return True
