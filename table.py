from deck import DeckGenerator
from logic import GameLogic
from logic import TableCard
from deck import Card
import shutil
from os import system
from sys import exit
from itertools import combinations


class Game:
    WIDTH = shutil.get_terminal_size().columns

    def __init__(self, deck, table, game_logic):
        """
        Initialize class.
        :param deck: DeckGenerator object
        :param table: TableCard object
        :param game_logic: GameLogic object
        """
        assert isinstance(deck, DeckGenerator), 'incorrect DeckGenerator object'
        assert isinstance(table, TableCard), 'incorrect TableCard object'
        assert isinstance(game_logic, GameLogic), 'incorrect GameLogic object'
        self._d = deck
        self._t = table
        self._gl = game_logic
        self._pyramid = self._t.pyramid_deck
        # current extra card
        self._add_card = self._gl.card_from_additional_deck
        # current pyramid card indexes
        self._indexes = [self._p_s.index(card) for card in self._p_s]
        self._supported_commands = ['ng', 'n', 'q', 'x', 'c', 'h', 'lvl', 'd',
                                    'r', '?']
        self._debug_bool = False  # for debugging
        self._level = 'easy'  # current game mode

    @property
    def _p_s(self):
        """Return cards which user can use."""
        p_s = []  # possible options
        for row in self._pyramid:
            for card in row:
                if card.status and card.rank is not None:
                    p_s.append(card)
        return p_s

    def _update_pyramid(self):
        """If two cards will be delete, uncover top cards."""
        for row in range(len(self._pyramid) - 1, 0, -1):
            for item in range(1, row + 1):
                if self._pyramid[row][item].rank is None and \
                        self._pyramid[row][item - 1].rank is None and \
                        self._pyramid[row - 1][item - 1].status is False and \
                        self._pyramid[row - 1][item - 1].rank is not None:
                    self._pyramid[row - 1][item - 1].status = True
        # if redo changes
        for row in range(len(self._pyramid) - 1, 0, -1):
            for item in range(1, row + 1):
                if self._pyramid[row][item].status and \
                        self._pyramid[row][item - 1].status and \
                        self._pyramid[row - 1][item - 1].status:
                    self._pyramid[row - 1][item - 1].status = False

    @property
    def _hint(self):
        """Return cards which can be compare.
        :return str index: 'x' if add card, '0...n' if card from pyramid;
                           '1 5' or 'x 4' if coincided two card.
        """
        # additional card are always last in this list
        open_cards = self._p_s
        open_cards.append(self._add_card)
        all_cards = open_cards
        for card in all_cards:
            if card.value == 13:
                return 'x' if all_cards.index(card) == len(all_cards)-1 else \
                    str(all_cards.index(card))
        # all possible card combinations (tuple)
        comb = combinations(all_cards, 2)  # (1, 2), (1, 3), ...
        len_ = len(all_cards)
        for item in comb:
            fst_card = item[0]
            snd_card = item[1]
            if sum([fst_card.value, snd_card.value]) == 13:
                if all_cards.index(fst_card) == len_-1:
                    return '{} {}'.format('x', str(all_cards.index(snd_card)))
                elif all_cards.index(snd_card) == len_-1:
                    return '{} {}'.format('x', str(all_cards.index(fst_card)))
                else:
                    return '{} {}'.format(str(all_cards.index(fst_card)),
                                          str(all_cards.index(snd_card)))

    def instruction(self):
        """Return game instruction."""
        text = '###############################\n' \
               '#      PYRAMID SOLITAIRE      #\n' \
               '#                             #\n' \
               '#     A = 1        J = 11     #\n' \
               '#     Q = 12       K = 13     #\n' \
               '#                             #\n' \
               '#  ng - new game   q - quit   #\n' \
               '#  n - next extra card        #\n' \
               '#  x - select extra card      #\n' \
               '#  c - compare                #\n' \
               '#  h - help window            #\n' \
               '#                             #\n' \
               '###############################\n'.format(self._gl.level)
        return text

    def _menu(self):
        """Return main menu text."""
        print('Mode: {}\n'.format(self._gl.level))
        text = ''
        for r in self._pyramid:
            for c in r:
                if c.status:
                    text += c.rank + ':' + c.suit + ' '
                else:
                    if c.rank is None:
                        text += ' - ' + ' '
                    elif c.rank is not None:
                        text += '#' + '   '
            text += '\n'
        text = text.split('\n')
        for item in text:
            print(item.center(self.WIDTH))
        # Debug info
        if self._debug_bool:
            stack = self._gl.card_stack
            deck = self._t.additional_deck.deck
            pyramid = self._pyramid
            print('Stack: ', end = '')
            for i in stack:
                print('{}:{}:{}'.format(i.rank, i.suit,
                                        'T' if i.status else 'F'), end = ' ')
            print('\nLength stack: ' + str(len(stack)))
            print('\nDeck: ', end = '')
            for i in deck:
                if i.rank is None:
                    print('-', end = ' ')
                else:
                    print('{}:{}:{}'.format(i.rank, i.suit,
                                            'T' if i.status else 'F'),
                          end = ' ')
            print('\nLength deck: ' + str(len(deck)))
            print('\nPyramid: ', end = '')
            for row in pyramid:
                for card in row:
                    if card.rank is None:
                        print('-', end = ' ')
                    else:
                        print('{}:{}:{}'.format(card.rank, card.suit,
                                                'T' if card.status else 'F'),
                              end = ' ')
            print()

        if self._add_card.rank is not None:
            print('\nExtra card: {}:{}\n'.format(self._add_card.rank,
                                                 self._add_card.suit))
        else:
            self._add_card = self._gl.card_from_additional_deck
            system('cls')
            self.start()

        # print indexes
        for c in self._p_s:
            print('{} = {}:{}'.format(self._p_s.index(c), c.rank, c.suit))

    def _start_new_game(self):
        """Start new game, with new objects."""
        D = DeckGenerator()
        D.shuffle()
        T = TableCard(D)
        T.generate_pyramid()
        gL = GameLogic(T)
        gL.level = self._level
        for item in T.pyramid_deck[-1]:
            item.status = True
        return Game(D, T, gL)

    def _compare(self):
        """Cards compare menu."""
        usr_card = input('Enter card (through space): ').strip().split(' ')
        usr_card = list(filter(lambda x: x != '', usr_card))
        if len(usr_card) not in range(1, 3):
            system('cls')
            self.start()
        try:
            if len(usr_card) == 1:
                card = usr_card[0]
                if card.isdigit():
                    if int(card) in self._indexes:
                        self._gl.compare_card(self._p_s[int(card)])
                    else:
                        return None
                elif card == 'x':
                    self._gl.compare_card(self._add_card)
                else:
                    return None
            else:
                card1 = usr_card[0]
                card2 = usr_card[1]
                if card1.isdigit() and card2.isdigit():
                    if int(card1) in self._indexes and int(
                            card2) in self._indexes:
                        self._gl.compare_card(self._p_s[int(card1)],
                                              self._p_s[int(card2)])
                    else:
                        return None
                elif card1 == 'x' and card2.isdigit():
                    if int(card2) in self._indexes:
                        self._gl.compare_card(self._add_card,
                                              self._p_s[int(card2)])
                    else:
                        return None
                elif card2 == 'x' and card1.isdigit():
                    if int(card1) in self._indexes:
                        self._gl.compare_card(self._add_card,
                                              self._p_s[int(card1)])
                    else:
                        return None
                else:
                    return None
            self._update_pyramid()
        except (ValueError, IndexError, AssertionError):
            system('cls')
            self.start()

    def _enter_command(self, command):
        """Depending on the command, we select the desired algorithm."""
        if command not in self._supported_commands:
            return None
        if command == 'ng':
            system('cls')
            self._start_new_game().start()
        elif command == 'q':
            exit()
        elif command == 'c':
            self._compare()
        elif command == 'n':
            self._add_card = self._gl.card_from_additional_deck
            system('cls')
            self.start()
        elif command == 'h':
            system('cls')
            input(self.instruction() + '\nPress any key to continue...')
            system('cls')
            self.start()
        elif command == 'd':
            system('cls')
            if self._debug_bool:
                self._debug_bool = False
            else:
                self._debug_bool = True
        elif command == 'lvl':
            try:
                enter_lvl = input('Enter level [easy, hard]: ').strip()
                self._level = enter_lvl
                system('cls')
                self._start_new_game().start()
            except AssertionError:
                return None

        elif command == 'r':
            system('cls')
            try:
                # dict {card, card_index, card_type} ↓
                redo_card = self._gl.redo_changes()
                card_obj = redo_card['card']
                card_index = redo_card['card_index']
                card_type = redo_card['card_type']

                if card_type == 'pyramid_deck':
                    row_index = card_index[0]
                    card_index_in_row = card_index[1]
                    # remove deleted card from list
                    remove_card = self._pyramid[row_index][card_index_in_row]
                    self._pyramid[row_index].remove(remove_card)
                    # insert backup card
                    self._pyramid[row_index].insert(card_index_in_row, card_obj)
                else:
                    add_deck = self._t.additional_deck.deck
                    for card in add_deck:
                        if card.rank is None:
                            add_deck.remove(card)
                            add_deck.append(card_obj)
                            break

                    stack = self._gl.card_stack
                    for card in stack:
                        if card.rank is None:
                            stack.remove(card)
                            stack.append(card_obj)
                            break
                self._update_pyramid()
                self.start()
            except IndexError:
                return None

        elif command == '?':
            print('Hint: {}'.format(self._hint))
            input('Press any key to continue...')
            system('cls')
            self.start()

    def start(self):
        """Main game class start here."""
        while self._pyramid[0][0].rank is not None:  # if top card is not None
            self._menu()
            command = input('\nCommand: ').strip()
            if self._enter_command(command) is None:
                system('cls')
                continue
        else:
            system('cls')
            input('\nGame Over')
            print(game.instruction())
            input('Press any key to continue...')  # wait user
            system('cls')
            self.start()



d = DeckGenerator()  # create deck
d.shuffle()
t = TableCard(d)  # create pyramid and additional card
t.generate_pyramid()
gl = GameLogic(t)
for i in t.pyramid_deck[-1]:  # open bottom row
    i.status = True


###################### Game ###################

game = Game(d, t, gl)
print(game.instruction())
input('Press any key to continue...')  # wait user
system('cls')
game.start()


def test():
    # ---------------- Test ----------------
    d = DeckGenerator()
    d.shuffle()
    t = TableCard(d)
    t.generate_pyramid()


if __name__ == '__main__':
    test()