from snakegame.board import Board, Point


def test_board_bounds():
    board = Board(width=20, height=15)

    assert board.is_in_bounds(Point(0, 0)) is True
    assert board.is_in_bounds(Point(19, 14)) is True
    assert board.is_in_bounds(Point(10, 7)) is True

    # Out of bounds checks
    assert board.is_in_bounds(Point(-1, 5)) is False
    assert board.is_in_bounds(Point(5, -1)) is False
    assert board.is_in_bounds(Point(20, 5)) is False
    assert board.is_in_bounds(Point(5, 15)) is False
    assert board.is_in_bounds(Point(20, 15)) is False


def test_board_empty_cells():
    board = Board(width=3, height=3)
    assert board.total_cells == 9

    occupied = {Point(0, 0), Point(1, 1), Point(2, 2)}
    empty = board.get_empty_cells(occupied)

    assert len(empty) == 6
    assert Point(0, 0) not in empty
    assert Point(1, 1) not in empty
    assert Point(2, 2) not in empty
    assert Point(0, 1) in empty
