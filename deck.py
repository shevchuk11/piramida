from random import shuffle


class Card:
    """Card object class."""

    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    # A - Ace; J - Jack; Q - Queen; K - King
    SUITS = ['S', 'D', 'C', 'H']
    # S - Shades; D - Diamonds; C - Clubs; H - Hearts

    def __init__(self, rank, suit, status=False):
        """
        Initializing class.
        :param rank: rank of card
        :param suit: suit of card
        :param status: False - the face of card close, True - open
        """
        assert isinstance(rank, str) and isinstance(suit, str) and isinstance(
            status, bool), 'enter correct value'
        assert rank in self.RANKS and suit in self.SUITS, 'entered incorrect' \
                                                          ' rank or suit'
        self._rank = rank
        self._suit = suit
        self._status = status
        self._value = self.RANKS.index(rank) + 1  # set card value (1-13)

    @property
    def rank(self):
        """Return card rank."""
        return self._rank

    @rank.setter
    def rank(self, value):
        """Set new card rank. Only None."""
        assert value is None, 'you can set only None value'
        self._rank = value

    @property
    def suit(self):
        """Return card suit."""
        return self._suit

    @suit.setter
    def suit(self, value):
        """Set new card suit. Only None."""
        assert value is None, 'you can set only None value'
        self._suit = value

    @property
    def status(self):
        """Return card status."""
        return self._status

    @status.setter
    def status(self, value):
        """Set new status value. Only bool."""
        assert isinstance(value, bool), 'incorrect value'
        self._status = value

    @property
    def value(self):
        """Return card value."""
        return self._value

    def __str__(self):
        return 'Card: Rank-{}; Suit-{}; Status-{}'\
            .format(self._rank, self._suit, 'Open' if self._status else 'Close')


class DeckGenerator:
    """Generate cards deck."""

    def __init__(self, deck_count=1):
        """
        :param deck_count: count of decks
        _deck - all cards on deck
        _iter - iterator start position
        """
        assert isinstance(deck_count, int), 'must be integer'
        assert deck_count > 0, 'count must be bigger than 0'

        self._deck = []
        self._iter = 0
        self._deck_count = deck_count

        # fill the deck
        for decks in range(self._deck_count):
            for suit in Card.SUITS:
                for rank in Card.RANKS:
                    self._deck.append(Card(rank, suit))

    def __len__(self):
        """Deck length."""
        return len(self._deck)

    def __iter__(self):
        return self

    def __next__(self):
        if self._iter < len(self._deck) - 1:
            self._iter += 1
            return self._deck[self._iter]
        raise StopIteration

    @property
    def deck(self):
        """Return deck list."""
        return self._deck

    def shuffle(self):
        """Shuffle deck list."""
        return shuffle(self._deck)


def test():
    # ---------------- Test ----------------
    d = DeckGenerator()
    d.deck[0].status = True
    print(d.deck[0])
    d.shuffle()
    print(len(d))
    d.deck[0].rank = False
    c = Card('10', 'H')
    c.status = True


if __name__ == '__main__':
    test()