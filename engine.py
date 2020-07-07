#!/usr/bin/env python3
import abc

class Card(abc.ABC):
    def on_play():
        pass

    def on_card_play(card, target_area, source_player):
        pass
