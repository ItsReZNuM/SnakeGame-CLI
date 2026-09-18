import time
from snakegame.board import Board, Point
from snakegame.config import GameConfig
from snakegame.food import SuperFood
from snakegame.game import Game
from snakegame.snake import Direction


def test_super_food_spawn():
    board = Board(width=10, height=10)
    occupied = {Point(0, 0), Point(1, 0)}
    sf = SuperFood.spawn(board, occupied, spawn_time=100.0, duration=5.0, points=50, growth=3)

    assert sf is not None
    assert sf.position not in occupied
    assert sf.points == 50
    assert sf.growth == 3
    assert sf.duration == 5.0
    assert sf.time_left(102.0) == 3.0
    assert sf.is_expired(105.1) is True
    assert sf.is_expired(104.9) is False


def test_game_eating_super_food(tmp_path):
    storage_file = tmp_path / "test_score.json"
    config = GameConfig(width=15, height=15, storage_path=storage_file)
    game = Game(config=config)
    game._reset_game()

    # Place superfood directly in front of snake
    game.snake.direction = Direction.RIGHT
    game.snake.next_direction = Direction.RIGHT
    target = Point(game.snake.head.x + 1, game.snake.head.y)
    game.super_food = SuperFood(position=target, spawn_time=time.perf_counter(), duration=5.0, points=50, growth=3)

    initial_len = game.snake.length
    initial_score = game.score

    game._last_tick_time = 0
    game._update()

    assert game.score == initial_score + 50
    assert game.super_foods_eaten == 1
    assert game.super_food is None
    # On first step, snake grows by 1 and has 2 pending growth
    assert game.snake.length == initial_len + 1
    assert game.snake.grow_pending == 2

    # Step 2 more times
    game.snake.step()
    game.snake.step()
    assert game.snake.length == initial_len + 3
    assert game.snake.grow_pending == 0
