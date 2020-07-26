from bwc.objects import Card, CardFlag


class NoahsBalance(Card):
    def init(self):
        self.val = 0
        self.name = 'Noah\'s Balance'
        self.image = 'NoahsBalance.jpg'
        self.flags = {CardFlag.ALWAYS_GET_EVENTS}
        self.tags = {"Lined"}

    def on_move(self, kernel, player, moving_card, from_area, to_area, gamestate):
        player_counts = dict((name, 0) for name in gamestate.players)
        for card in gamestate.all_cards:
            if "Lined" in card.tags:
                for owner in card.owners:
                    player_counts[owner.username] += 1

        winning_players = []
        for player_name, count in player_counts.items():
            if gamestate.players[player_name] in self.owners and \
                    count >= 7:
                # Emulate "infinite" points
                self.val = 1_000_000_000
                winning_players.append(player_name)

        if winning_players:
            for player_name in winning_players:
                kernel.send_message(gamestate.players.values(), f"{format_player(player_name)} as EXNOAHDIAED")
            kernel.end_game()
