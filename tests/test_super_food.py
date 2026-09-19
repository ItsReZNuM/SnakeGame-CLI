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


def test_super_food_dynamic_duration_at_higher_speed(tmp_path):
    storage_file = tmp_path / "test_score.json"
    config = GameConfig(
        width=15,
        height=15,
        initial_speed=6.0,
        speed_increment=1.0,
        super_food_duration=5.0,
        storage_path=storage_file,
    )
    game = Game(config=config)
    game._reset_game()

    # Trigger superfood spawn at initial speed (6.0)
    game.regular_foods_eaten = 4
    game.food = Point(game.snake.head.x + 1, game.snake.head.y)  # place food in front
    from snakegame.food import Food
    game.food = Food(position=Point(game.snake.head.x + 1, game.snake.head.y), points=10)
    game._last_tick_time = 0
    game._update()

    assert game.regular_foods_eaten == 5
    assert game.super_food is not None
    duration_at_speed_1 = game.super_food.duration
    # Should be less than or equal to base duration (5.0s)
    assert duration_at_speed_1 <= 5.0

    # Increase eaten foods so speed is even higher, then test next spawn
    game.super_food = None
    game.regular_foods_eaten = 9
    game.score = 90  # higher score -> higher speed
    speed_1 = game.current_speed

    game.food = Food(position=Point(game.snake.head.x + 1, game.snake.head.y), points=10)
    game._last_tick_time = 0
    game._update()

    assert game.regular_foods_eaten == 10
    assert game.super_food is not None
    assert game.current_speed > speed_1
    duration_at_speed_2 = game.super_food.duration
    # Duration at higher speed must be strictly shorter than at lower speed
    assert duration_at_speed_2 < duration_at_speed_1

