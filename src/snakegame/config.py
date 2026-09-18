import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional, Dict

from snakegame.theme import THEME_NAMES

DEFAULT_KEYBINDINGS: dict[str, str] = {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
    "pause": "p",
}


class ConfigError(ValueError):
    """Raised when game configuration parameters are outside valid ranges."""
    pass


@dataclass
class GameConfig:
    width: int = 24
    height: int = 16
    initial_speed: float = 6.0
    speed_increment: float = 0.3
    max_speed: float = 20.0
    points_per_food: int = 10
    no_color: bool = False
    theme_name: str = "Nokia Classic"
    super_food_enabled: bool = True
    super_food_interval: int = 5
    super_food_duration: float = 5.0
    super_food_points: int = 50
    super_food_growth: int = 3
    keybindings: Dict[str, str] = field(default_factory=lambda: dict(DEFAULT_KEYBINDINGS))
    storage_path: Optional[Path] = None
    settings_path: Optional[Path] = None

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
        if self.theme_name not in THEME_NAMES:
            self.theme_name = "Nokia Classic"

    def get_settings_file(self) -> Path:
        if self.settings_path is not None:
            return Path(self.settings_path)
        return Path.home() / ".snakegame" / "settings.json"

    def save_settings(self) -> bool:
        try:
            target = self.get_settings_file()
            target.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "width": self.width,
                "height": self.height,
                "initial_speed": self.initial_speed,
                "theme_name": self.theme_name,
                "super_food_enabled": self.super_food_enabled,
                "keybindings": self.keybindings,
            }
            with open(target, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except OSError:
            return False

    def load_saved_settings(self) -> None:
        target = self.get_settings_file()
        if not target.exists():
            return
        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "width" in data and isinstance(data["width"], int) and 10 <= data["width"] <= 60:
                self.width = data["width"]
            if "height" in data and isinstance(data["height"], int) and 8 <= data["height"] <= 35:
                self.height = data["height"]
            if "initial_speed" in data and isinstance(data["initial_speed"], (int, float)) and 1.0 <= data["initial_speed"] <= 25.0:
                self.initial_speed = float(data["initial_speed"])
            if "theme_name" in data and data["theme_name"] in THEME_NAMES:
                self.theme_name = data["theme_name"]
            if "super_food_enabled" in data and isinstance(data["super_food_enabled"], bool):
                self.super_food_enabled = data["super_food_enabled"]
            if "keybindings" in data and isinstance(data["keybindings"], dict):
                for k in ("up", "down", "left", "right", "pause"):
                    val = data["keybindings"].get(k)
                    if isinstance(val, str) and val:
                        self.keybindings[k] = val.lower()
        except (json.JSONDecodeError, OSError, TypeError):
            pass
