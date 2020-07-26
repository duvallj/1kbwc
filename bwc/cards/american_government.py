from bwc.objects import Card, CardFlag


class american_government(Card):
    def init(self):
        self.val = 0
        self.name = 'American Government'
        self.image = 'American_Government.png'
        self.flags = {CardFlag.ONLY_PLAY_TO_CENTER}
        self.tags = {"Government System"}
