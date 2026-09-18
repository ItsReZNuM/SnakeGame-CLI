import time
from snakegame.board import Point
from snakegame.config import GameConfig
from snakegame.food import Food
from snakegame.game import Game, GameState
from snakegame.snake import Direction
from snakegame.ui import format_timer


def test_format_timer():
    assert format_timer(0) == "00:00"
    assert format_timer(42) == "00:42"
    assert format_timer(83) == "01:23"
    assert format_timer(3605) == "60:05"


def test_game_initial_state(tmp_path):
    storage_file = tmp_path / "test_score.json"
    config = GameConfig(storage_path=storage_file)
    game = Game(config=config)

    assert game.state == GameState.START_SCREEN
    assert game.score == 0
    assert game.high_score == 0
    assert game.snake.length == 3
    assert game.board.is_in_bounds(game.snake.head)


def test_speed_progression(tmp_path):
    storage_file = tmp_path / "test_score.json"
    config = GameConfig(
        storage_path=storage_file,
        initial_speed=5.0,
        speed_increment=0.5,
        max_speed=8.0,
        points_per_food=10,
    )
    game = Game(config=config)

    # Initial speed
    assert game.current_speed == 5.0

    # 1 food eaten (10 pts)
    game.score = 10
    assert game.current_speed == 5.5

    # 4 foods eaten (40 pts)
    game.score = 40
    assert game.current_speed == 7.0

    # High score reaches max_speed cap
    game.score = 100
    assert game.current_speed == 8.0


def test_wall_wrap_around(tmp_path):
    storage_file = tmp_path / "test_score.json"
    config = GameConfig(width=10, height=10, storage_path=storage_file)
    game = Game(config=config)
    game._reset_game()

    # Move snake straight into right wall
    game.snake.direction = Direction.RIGHT
    game.snake.next_direction = Direction.RIGHT

    # Force snake head near right edge
    game.snake.body[0] = Point(9, 5)
    game.snake.body[1] = Point(8, 5)
    game.snake.body[2] = Point(7, 5)

    # Step should wrap around to (0, 5) instead of dying
    game._last_tick_time = 0
    game._update()

    assert game.state == GameState.PLAYING
    assert game.snake.head == Point(0, 5)


def test_eating_food_increases_score_and_length(tmp_path):
    storage_file = tmp_path / "test_score.json"
    config = GameConfig(width=15, height=15, storage_path=storage_file, points_per_food=10)
    game = Game(config=config)
    game._reset_game()

    # Position food directly in front of the snake
    game.snake.direction = Direction.RIGHT
    game.snake.next_direction = Direction.RIGHT
    target_point = Point(game.snake.head.x + 1, game.snake.head.y)
    game.food = Food(position=target_point, points=10)

    initial_len = game.snake.length
    game._last_tick_time = 0
    game._update()

    assert game.score == 10
    assert game.snake.head == target_point
    assert game.snake.length == initial_len + 1
