from objects import Card, CardFlag, AreaFlag


class aegis_of_animated_armor(Card):
    def init(self):
        self.val = 350
        self.name = 'Aegis of Animated Armor'
        self.image = 'AegisOfAnimatedArmor.png'
        self.flags = set()
        self.tags = set()

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        if to_area == self.area and AreaFlag.HAND_AREA in from_area.flags and player not in self.owners:
            if abs(card.val) <= abs(self.val):
                kernel.send_message([player], f"[{self.name}] {card.name} is not a worthy challenger!")
                return False
