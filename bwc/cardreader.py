import inspect
import random

from bwc.objects import Card
# We need this import here to "prime" the import later on into realizing our __all__ in
# cards/__init__.py should actually be used to list the modules
from bwc.cards import *


def read_cards():
    from bwc import cards
    card_modules = inspect.getmembers(cards, inspect.ismodule)
    card_classes = []
    for card_module in card_modules:
        card_classes.extend(inspect.getmembers(card_module[1], inspect.isclass))
    card_classes = [card_class[1] for card_class in card_classes if card_class[1] != Card]
    card_classes = [card_class for card_class in card_classes if Card in card_class.__bases__]
    return card_classes


def make_deck(size=0, shuffle=True):
    classes = read_cards()
    deck = []
    for card_class in classes:
        deck.append(card_class())
    if shuffle:
        random.shuffle(deck)  # nice
    if size == 0:
        return deck
    while len(deck) < size:
        deck.append(random.choice(classes)())
    while len(deck) > size:
        del deck[random.randint(0, len(deck) - 1)]
    return deck


if __name__ == "__main__":
    print(read_cards())
