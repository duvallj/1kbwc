from bwc.objects import Card


class cat_with_dollar(Card):
    def init(self):
        self.val = 100
        self.name = 'Cat with Dollar'
        self.image = 'CatWithDollar.png'
        self.flags = set()
        self.tags = {"Animal", "Cat"}
