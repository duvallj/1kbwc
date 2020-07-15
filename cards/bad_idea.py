from objects import Card, CardFlag


class Bad_Idea(Card):
    def init(self):
        self.val = -800
        self.name = 'Bad Idea'
        self.image = 'Bad_Idea.png'
        self.flags = {CardFlag.ALWAYS_GET_EVENTS}



