from deck import DeckGenerator  # only for test
from deck import Card
from functools import reduce
import copy

class TableCard:
    """Contain pyramid deck and additional deck."""

    def __init__(self, deck):
        """
        Initializing class.
        :param deck: DeckGenerator object
        """
        assert isinstance(deck, DeckGenerator), 'deck object incorrect'

        self._current_deck = deck
        self._pyramid = []
        self._pyramid_rows = 7

    def generate_pyramid(self):
        """Generate pyramid."""
        self._pyramid = [[self._current_deck.deck.pop() for j in range(i)]
                         for i in range(1, self._pyramid_rows+1)]

    @property
    def additional_deck(self):
        """Return additional deck object."""
        return self._current_deck

    @property
    def pyramid_deck(self):
        """Return pyramid list."""
        return self._pyramid

    def isPyramidCard(self, card_obj):
        """Check if is a Card object.
        :return: bool """
        assert isinstance(card_obj, Card), 'incorrect Card object'

        if card_obj in self._current_deck.deck:
            return False
        for row in self._pyramid:
            if card_obj in row:
                return True

    def __getitem__(self, item):
        """Return item from deck.
        :param item: Card object"""
        assert isinstance(item, Card), 'incorrect Card object'
        if item in self._current_deck.deck:
            return item
        for row in self._pyramid:
            if item in row:
                return item
        return None

    def __str__(self):
        """Return pyramid in readable style."""
        res = ''
        for row in self._pyramid:
            for card in row:
                res += '|{}-{}-{}|'.format(card.rank, card.suit,
                                           'Open' if card.status else 'Close') \
                       + ' '
            res += '\n'
        return res


class GameLogic:
    """Main game logic class."""

    def __init__(self, table_obj):
        """
        Initializing class.
        :param table_obj: TableCard object
        """
        assert isinstance(table_obj, TableCard), 'incorrect table object'

        self._table_obj = table_obj
        self._level = 'easy'
        self._card_stack = []  # additional card stack
        self._changes = {'pyramid_deck': [], 'add_deck': [],  # changes journal
                         'stack': []}
        self._history = []  # history of changes

    def cardIndex(self, card_obj):
        """Return Card object index from different lists."""
        assert isinstance(card_obj, Card), 'incorrect Card object'

        # if card in add deck
        if card_obj in self._table_obj.additional_deck.deck:
            return self._table_obj.additional_deck.deck.index(card_obj)
        # if card in stack
        elif card_obj in self._card_stack:
            return self._card_stack.index(card_obj)
        # if card in pyramid deck
        for row in self._table_obj.pyramid_deck:
            if card_obj in row:
                return self._table_obj.pyramid_deck.index(row), \
                       row.index(card_obj)

    def _del_card(self, card_obj):
        """Mark card as None."""
        assert isinstance(card_obj, Card), 'incorrect Card object'

        # add copy Card object
        if self._table_obj.isPyramidCard(card_obj):
            self._changes['pyramid_deck'].append(copy.deepcopy(card_obj))
            self._history.append({'pyramid_deck': self.cardIndex(card_obj)})
        else:
            if card_obj in self._card_stack:
                self._changes['stack'].append(copy.deepcopy(card_obj))
                self._history.append({'stack': self.cardIndex(card_obj)})
            else:
                self._changes['add_deck'].append(copy.deepcopy(card_obj))
                self._history.append({'add_deck': self.cardIndex(card_obj)})

        card_obj.rank = None
        card_obj.suit = None
        card_obj.status = False

    def redo_changes(self):
        """Return redo information.
        :returns: card, card_index, card_type """
        last_del_elem = self._history.pop()  # dict
        card_type = list(last_del_elem.keys())[0]  # add_deck or pyramid_deck
                                                   # or stack (str)
        card = self._changes[card_type].pop()  # card obj
        card_index = last_del_elem[card_type]  # index of returned card
        return {'card': card, 'card_index': card_index, 'card_type': card_type}

    def compare_card(self, *args):
        """Compare and delete cards from deck."""
        assert all(list(map(lambda obj: isinstance(obj, Card), list(args)))), \
            'this is not Card object'

        if any(list(map(lambda obj: obj in self._card_stack, list(args)))):
            map(lambda obj: self._del_card(obj), list(args))
        if all(list(map(lambda obj: obj.status, list(args)))):
            if sum(list(map(lambda obj: obj.value, list(args)))) == 13:
                # compare to suits (hard mode)
                if self._level == 'hard':
                    if len(args) != 1:
                        assert reduce(
                            lambda a, b: a.suit == b.suit if a else None,
                            list(args)), 'different suits'

                for item in args:
                    self._del_card(item)
            else:
                raise ValueError('sum of values is not 13')
        else:
            raise ValueError('one of the cards is closed')

    @property
    def table(self):
        """Return TableCard object."""
        return self._table_obj

    @property
    def card_from_additional_deck(self):
        """Return card from additional deck."""
        deck_ = self._table_obj.additional_deck.deck
        if deck_:
            current_card = deck_.pop()
            if current_card.rank is not None:
                current_card.status = True
            self._card_stack.append(current_card)
            if not deck_:
                deck_.extend(self._card_stack)
                self._card_stack.clear()
            return current_card
        for card in self._card_stack:
            card.status = False

    @property
    def card_stack(self):
        """Return cards stack."""
        return self._card_stack

    @property
    def level(self):
        """Return game level."""
        return self._level

    @level.setter
    def level(self, level):
        """Set game level value."""
        levels = ['easy', 'hard']
        assert level in levels, 'incorrect level'
        self._level = level

def test():
    # ---------------- Test ----------------
    d = DeckGenerator()
    d.shuffle()
    t = TableCard(d)
    t.generate_pyramid()
    for i in t.pyramid_deck:
        for j in i:
            j.status = True
    print(t)
    for i in t.additional_deck.deck:
        i.status = True
        print(t.additional_deck.deck.index(i), i)
    gl = GameLogic(t)



if __name__ == '__main__':
    test()
