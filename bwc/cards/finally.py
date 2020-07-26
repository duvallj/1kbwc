from bwc.objects import Card, CardFlag


class _finally_(Card):
    def init(self):
        self.val = 400
        self.name = '} finally {'
        self.image = 'Finally.png'
        self.flags = {CardFlag.ALWAYS_GET_EVENTS}
        self.tags = {"Technology"}
        self.old_owners = None
        self.active = False

    def on_discard(self, kernel, gamestate, discarder):
        kernel.send_message(self.owners, "} finally { you may discard a card! }")
        self.old_owners = list(self.owners)
        self.active = True

    def handle_move(self, kernel, player, card, from_area, to_area, gamestate):
        if self.active:
            if player in self.old_owners:
                if to_area == gamestate.discard:
                    self.old_owners.remove(player)
                    if len(self.old_owners) == 0:
                        self.active = False
                    return True
