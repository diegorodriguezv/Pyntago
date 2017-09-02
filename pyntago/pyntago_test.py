#! /usr/bin/env python
import unittest

import pyntago

players = [pyntago.Player('White', pyntago.COLOR_WHITE), pyntago.Player('Black', pyntago.COLOR_BLACK)]


class BoardWith4Corners(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.players = [pyntago.Player('White', pyntago.COLOR_WHITE), pyntago.Player('Black', pyntago.COLOR_BLACK)]
        cls.corners = [(0, 0), (5, 5), (0, 5), (5, 0)]
        current_player_index = 0
        cls.board = {}
        for x, y in cls.corners:
            cls.board[pyntago.Position(x, y)] = players[current_player_index]
            current_player_index = (current_player_index + 1) % 2
        print('Board with 4 corners:', flush=True)
        pyntago.print_board(cls.board)

    def setUp(self):
        self.current_player_index = 0

    def test_has_proper_length(self):
        self.assertEqual(len(self.board), 4)

    def test_has_no_winners(self):
        self.assertIsNone(pyntago.winner(self.board, self.players))

    def test_rotates_one_notch_and_back_in_every_block(self):
        new_board = self.board
        for block in range(4):
            new_board = pyntago.rotate(new_board, block, pyntago.DIRECTION_RIGHT)
        for c in self.corners:
            self.assertTrue(c in self.board)
            self.assertFalse(c in new_board)
        print('Board with 4 corners rotated right:', flush=True)
        pyntago.print_board(new_board)
        for block in range(4):
            new_board = pyntago.rotate(new_board, block, pyntago.DIRECTION_LEFT)
        for c in self.corners:
            self.assertTrue(c in self.board)
            self.assertTrue(c in new_board)

    def test_rotates_two_notches_each_direction_for_every_block(self):
        r_board = self.board
        for block in range(4):
            r_board = pyntago.rotate(r_board, block, pyntago.DIRECTION_RIGHT)
            r_board = pyntago.rotate(r_board, block, pyntago.DIRECTION_RIGHT)
        for c in self.corners:
            self.assertTrue(c in self.board)
            self.assertFalse(c in r_board)
        print('Board with 4 corners rotated right twice:', flush=True)
        pyntago.print_board(r_board)
        l_board = self.board
        for block in range(4):
            l_board = pyntago.rotate(l_board, block, pyntago.DIRECTION_LEFT)
            l_board = pyntago.rotate(l_board, block, pyntago.DIRECTION_LEFT)
        for c in self.corners:
            self.assertTrue(c in self.board)
            self.assertFalse(c in l_board)
        print('Board with 4 corners rotated left twice:', flush=True)
        pyntago.print_board(l_board)
        self.assertEqual(r_board, l_board)
        self.assertNotEqual(r_board, self.board)
        self.assertNotEqual(l_board, self.board)

    def has_4_corners(self):
        for c in self.corners:
            self.assertTrue(c in self.board)


class TwoVerticalStripeBoards(unittest.TestCase):
    def setUp(self):
        self.board = {}
        self.players = [pyntago.Player('White', pyntago.COLOR_WHITE), pyntago.Player('Black', pyntago.COLOR_BLACK)]
        self.current_player_index = 0
        for x in range(2):
            for y in range(6):
                self.board[pyntago.Position(x, y)] = self.players[self.current_player_index]
            self.current_player_index = (self.current_player_index + 1) % 2
        print('two vertical stripes board:', flush=True)
        pyntago.print_board(self.board)

    def test_has_proper_length(self):
        self.assertEqual(len(self.board), 12)

    def test_is_a_tie(self):
        self.assertEqual(pyntago.winner(self.board, self.players), pyntago.Player(None, None))

    def test_is_not_a_tie_when_properly_rotated(self):
        new_board = pyntago.rotate(self.board, 2, pyntago.DIRECTION_RIGHT)
        print('two vertical stripes board rotated:', flush=True)
        pyntago.print_board(new_board)
        self.assertIsNone(pyntago.winner(new_board, self.players))


class TwoHorizontalStripeBoards(unittest.TestCase):
    def setUp(self):
        self.board = {}
        self.players = [pyntago.Player('White', pyntago.COLOR_WHITE), pyntago.Player('Black', pyntago.COLOR_BLACK)]
        self.current_player_index = 0
        for y in range(2):
            for x in range(6):
                self.board[pyntago.Position(x, y)] = self.players[self.current_player_index]
            self.current_player_index = (self.current_player_index + 1) % 2
        print('two horizontal stripes board:', flush=True)
        pyntago.print_board(self.board)

    def test_has_proper_length(self):
        self.assertEqual(len(self.board), 12)

    def test_is_a_tie(self):
        self.assertEqual(pyntago.winner(self.board, self.players), pyntago.Player(None, None))

    def test_is_not_a_tie_when_properly_rotated(self):
        new_board = pyntago.rotate(self.board, 1, pyntago.DIRECTION_RIGHT)
        print('two horizontal stripes board rotated:', flush=True)
        pyntago.print_board(new_board)
        self.assertIsNone(pyntago.winner(new_board, self.players))


class TwoDiagonalStripeBoards(unittest.TestCase):
    def setUp(self):
        self.board = {}
        self.players = [pyntago.Player('White', pyntago.COLOR_WHITE), pyntago.Player('Black', pyntago.COLOR_BLACK)]
        self.current_player_index = 0
        for x in range(6):
            self.board[pyntago.Position(x, x)] = self.players[self.current_player_index]
        self.current_player_index = (self.current_player_index + 1) % 2
        for x in range(5):
            self.board[pyntago.Position(x + 1, x)] = self.players[self.current_player_index]
        print('two horizontal stripes board:', flush=True)
        pyntago.print_board(self.board)

    def test_has_proper_length(self):
        self.assertEqual(len(self.board), 11)

    def test_is_a_tie(self):
        self.assertEqual(pyntago.winner(self.board, self.players), pyntago.Player(None, None))

    def test_is_not_a_tie_when_properly_rotated(self):
        new_board = pyntago.rotate(self.board, 1, pyntago.DIRECTION_RIGHT)
        print('two horizontal stripes board rotated:', flush=True)
        pyntago.print_board(new_board)
        self.assertEqual(pyntago.winner(new_board, self.players), players[0])


def main():
    unittest.main()


if __name__ == '__main__':
    main()
