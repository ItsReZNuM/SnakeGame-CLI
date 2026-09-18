from collections import deque
from enum import Enum
from typing import Deque, List, Set

from snakegame.board import Point


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    def is_opposite(self, other: "Direction") -> bool:
        return self.dx + other.dx == 0 and self.dy + other.dy == 0


class Snake:
    def __init__(self, initial_head: Point, initial_length: int = 3, direction: Direction = Direction.RIGHT) -> None:
        self.direction = direction
        self.next_direction = direction
        self.grow_pending = 0

        # Build initial body segments extending backwards from the heading direction
        self.body: Deque[Point] = deque()
        rev_dx = -direction.dx
        rev_dy = -direction.dy
        for i in range(initial_length):
            segment = Point(initial_head.x + i * rev_dx, initial_head.y + i * rev_dy)
            self.body.append(segment)

    @property
    def head(self) -> Point:
        return self.body[0]

    def peek_next_head(self) -> Point:
        return Point(self.head.x + self.next_direction.dx, self.head.y + self.next_direction.dy)

    @property
    def length(self) -> int:
        return len(self.body)

    @property
    def body_set(self) -> Set[Point]:
        return set(self.body)

    def change_direction(self, new_direction: Direction) -> bool:
        if new_direction.is_opposite(self.direction) or new_direction.is_opposite(self.next_direction):
            return False
        self.next_direction = new_direction
        return True

    def step(self) -> Point:
        self.direction = self.next_direction
        new_head = Point(self.head.x + self.direction.dx, self.head.y + self.direction.dy)
        self.body.appendleft(new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
        return new_head

    def grow(self, amount: int = 1) -> None:
        self.grow_pending += amount

    def collides_with_self(self) -> bool:
        # Check if head collides with any subsequent segment
        for i in range(1, len(self.body)):
            if self.body[i] == self.head:
                return True
        return False
