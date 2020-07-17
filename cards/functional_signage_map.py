from objects import Card


class functional_signage_map(Card):
    def init(self):
        self.val = 400
        self.name = 'Functional Signage Map'
        self.image = 'FunctionalSignageMap.png'
        self.flags = set()
        self.tags = {"Technology"}
