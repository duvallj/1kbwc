from bwc.objects import Card


class positive_feedback_loop(Card):
    def init(self):
        self.val = 200
        self.name = 'Positive Feedback Loop'
        self.image = 'PositiveFeedbackLoop.png'
        self.flags = set()
        self.tags = set()

    def on_move(self, kernel, player, card, from_area, to_area, gamestate):
        if to_area == self.area and self.val == 200:  # Potential gain
            if isinstance(card, positive_feedback_loop):  # Gain (possibly to one)
                if len([c for c in self.area.contents if isinstance(c, positive_feedback_loop)]) >= 2:  # Count
                    self.val = 600
        elif from_area == self.area and self.val == 600:  # Potential loss
            if isinstance(card, positive_feedback_loop):  # Loss (possibly to more than one)
                if len([c for c in self.area.contents if isinstance(c, positive_feedback_loop)]) < 2:  # Count
                    self.val = 200
