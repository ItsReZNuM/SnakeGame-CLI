from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class ConfigError(ValueError):
    """Raised when game configuration parameters are outside valid ranges."""
    pass


@dataclass(frozen=True)
class GameConfig:
    width: int = 24
    height: int = 16
    initial_speed: float = 6.0
    speed_increment: float = 0.3
    max_speed: float = 20.0
    points_per_food: int = 10
    no_color: bool = False
    storage_path: Optional[Path] = None

    def validate(self) -> None:
        if not (10 <= self.width <= 60):
            raise ConfigError(
                f"Board width must be between 10 and 60 cells (received {self.width})."
            )
        if not (8 <= self.height <= 35):
            raise ConfigError(
                f"Board height must be between 8 and 35 cells (received {self.height})."
            )
        if not (1.0 <= self.initial_speed <= 25.0):
            raise ConfigError(
                f"Initial speed must be between 1.0 and 25.0 moves/sec (received {self.initial_speed})."
            )
        if self.speed_increment < 0:
            raise ConfigError("Speed increment cannot be negative.")
        if self.max_speed < self.initial_speed:
            raise ConfigError("Maximum speed cannot be less than initial speed.")
