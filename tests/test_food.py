import random
from snakegame.board import Board, Point
from snakegame.food import Food


def test_food_spawns_on_empty_cell():
    board = Board(width=4, height=4)
    occupied = {Point(0, 0), Point(1, 0), Point(2, 0)}

    food = Food.spawn(board, occupied, points=15)
    assert food is not None
    assert food.position not in occupied
    assert board.is_in_bounds(food.position)
    assert food.points == 15


def test_food_spawns_deterministic_with_seed():
    board = Board(width=5, height=5)
    occupied = set()

    rng1 = random.Random(42)
    food1 = Food.spawn(board, occupied, rng=rng1)

    rng2 = random.Random(42)
    food2 = Food.spawn(board, occupied, rng=rng2)

    assert food1 is not None and food2 is not None
    assert food1.position == food2.position


def test_food_spawning_when_board_is_full():
    board = Board(width=2, height=2)
    all_cells = {Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)}

    food = Food.spawn(board, all_cells)
    assert food is None
