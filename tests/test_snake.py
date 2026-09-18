from snakegame.board import Point
from snakegame.snake import Direction, Snake


def test_snake_initialization():
    snake = Snake(initial_head=Point(5, 5), initial_length=3, direction=Direction.RIGHT)
    assert snake.head == Point(5, 5)
    assert snake.length == 3
    assert list(snake.body) == [Point(5, 5), Point(4, 5), Point(3, 5)]
    assert snake.direction == Direction.RIGHT


def test_snake_movement():
    snake = Snake(initial_head=Point(5, 5), initial_length=3, direction=Direction.RIGHT)
    new_head = snake.step()
    assert new_head == Point(6, 5)
    assert snake.head == Point(6, 5)
    assert snake.length == 3
    assert list(snake.body) == [Point(6, 5), Point(5, 5), Point(4, 5)]


def test_snake_growth():
    snake = Snake(initial_head=Point(5, 5), initial_length=3, direction=Direction.RIGHT)
    snake.grow(1)
    snake.step()
    assert snake.length == 4
    assert list(snake.body) == [Point(6, 5), Point(5, 5), Point(4, 5), Point(3, 5)]

    # Next step without growth should keep length 4 and drop tail
    snake.step()
    assert snake.length == 4
    assert list(snake.body) == [Point(7, 5), Point(6, 5), Point(5, 5), Point(4, 5)]


def test_direction_changes():
    snake = Snake(initial_head=Point(5, 5), initial_length=3, direction=Direction.RIGHT)

    # Turn UP is valid
    assert snake.change_direction(Direction.UP) is True
    snake.step()
    assert snake.head == Point(5, 4)
    assert snake.direction == Direction.UP

    # Turn LEFT is valid
    assert snake.change_direction(Direction.LEFT) is True
    snake.step()
    assert snake.head == Point(4, 4)
    assert snake.direction == Direction.LEFT


def test_cannot_reverse_direction():
    snake = Snake(initial_head=Point(5, 5), initial_length=3, direction=Direction.RIGHT)

    # Attempting to reverse immediately into itself should be blocked
    assert snake.change_direction(Direction.LEFT) is False
    snake.step()
    # Continues moving RIGHT
    assert snake.head == Point(6, 5)


def test_turn_buffering_prevents_rapid_reversal():
    snake = Snake(initial_head=Point(5, 5), initial_length=3, direction=Direction.RIGHT)

    # Buffer DOWN
    assert snake.change_direction(Direction.DOWN) is True
    # Trying to immediately buffer UP while DOWN is queued should be rejected
    assert snake.change_direction(Direction.UP) is False
    snake.step()
    assert snake.head == Point(5, 6)
    assert snake.direction == Direction.DOWN


def test_self_collision_detection():
    # Construct a snake long enough to loop into itself
    snake = Snake(initial_head=Point(5, 5), initial_length=5, direction=Direction.RIGHT)
    assert snake.collides_with_self() is False

    # Perform a circle: UP -> LEFT -> DOWN
    snake.change_direction(Direction.UP)
    snake.step()  # (5, 4)
    assert snake.collides_with_self() is False

    snake.change_direction(Direction.LEFT)
    snake.step()  # (4, 4)
    assert snake.collides_with_self() is False

    snake.change_direction(Direction.DOWN)
    snake.step()  # (4, 5) which was occupied by segment
    assert snake.collides_with_self() is True
