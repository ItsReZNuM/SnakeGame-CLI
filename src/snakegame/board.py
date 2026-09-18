from dataclasses import dataclass
from typing import NamedTuple, Set, List


class Point(NamedTuple):
    x: int
    y: int


@dataclass(frozen=True)
class Board:
    width: int
    height: int

    def is_in_bounds(self, point: Point) -> bool:
        return 0 <= point.x < self.width and 0 <= point.y < self.height

    @property
    def total_cells(self) -> int:
        return self.width * self.height

    def get_empty_cells(self, occupied: Set[Point]) -> List[Point]:
        empty = []
        for y in range(self.height):
            for x in range(self.width):
                pt = Point(x, y)
                if pt not in occupied:
                    empty.append(pt)
        return empty
