import random
from dataclasses import dataclass
from typing import Optional, Set

from snakegame.board import Board, Point


@dataclass
class Food:
    position: Point
    points: int = 10

    @classmethod
    def spawn(
        cls,
        board: Board,
        occupied: Set[Point],
        points: int = 10,
        rng: Optional[random.Random] = None,
    ) -> Optional["Food"]:
        empty_cells = board.get_empty_cells(occupied)
        if not empty_cells:
            return None

        picker = rng if rng is not None else random
        chosen = picker.choice(empty_cells)
        return cls(position=chosen, points=points)


@dataclass
class SuperFood:
    position: Point
    spawn_time: float
    duration: float = 5.0
    points: int = 50
    growth: int = 3

    def time_left(self, current_time: float) -> float:
        return max(0.0, self.duration - (current_time - self.spawn_time))

    def is_expired(self, current_time: float) -> bool:
        return (current_time - self.spawn_time) >= self.duration

    @classmethod
    def spawn(
        cls,
        board: Board,
        occupied: Set[Point],
        spawn_time: float,
        duration: float = 5.0,
        points: int = 50,
        growth: int = 3,
        rng: Optional[random.Random] = None,
    ) -> Optional["SuperFood"]:
        empty_cells = board.get_empty_cells(occupied)
        if not empty_cells:
            return None

        picker = rng if rng is not None else random
        chosen = picker.choice(empty_cells)
        return cls(
            position=chosen,
            spawn_time=spawn_time,
            duration=duration,
            points=points,
            growth=growth,
        )
