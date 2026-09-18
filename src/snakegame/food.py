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
