from objects import Card


class expo_marker(Card):
    def init(self):
        self.val = 300
        self.name = 'Expo Marker'
        self.image = 'Expo_Marker.png'
        self.flags = set()
        self.tags = set()
