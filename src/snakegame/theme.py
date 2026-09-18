from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Theme:
    name: str
    head_style: str
    body_style: str
    body_alt_style: str
    food_style: str
    super_food_style: str
    border_style: str
    accent_style: str


THEMES: Dict[str, Theme] = {
    "Nokia Classic": Theme(
        name="Nokia Classic",
        head_style="bold bright_yellow",
        body_style="bold bright_green",
        body_alt_style="green",
        food_style="bold bright_red",
        super_food_style="bold bright_yellow",
        border_style="bright_green",
        accent_style="green",
    ),
    "Cyberpunk Neon": Theme(
        name="Cyberpunk Neon",
        head_style="bold bright_yellow",
        body_style="bold bright_cyan",
        body_alt_style="blue",
        food_style="bold bright_magenta",
        super_food_style="bold bright_yellow",
        border_style="bright_magenta",
        accent_style="cyan",
    ),
    "Retro Amber": Theme(
        name="Retro Amber",
        head_style="bold bright_white",
        body_style="bold bright_yellow",
        body_alt_style="yellow",
        food_style="bold bright_red",
        super_food_style="bold bright_cyan",
        border_style="bright_yellow",
        accent_style="yellow",
    ),
    "Synthwave": Theme(
        name="Synthwave",
        head_style="bold bright_cyan",
        body_style="bold magenta",
        body_alt_style="dark_magenta",
        food_style="bold bright_yellow",
        super_food_style="bold bright_green",
        border_style="bright_cyan",
        accent_style="magenta",
    ),
    "Matrix Monochrome": Theme(
        name="Matrix Monochrome",
        head_style="bold bright_white",
        body_style="bold white",
        body_alt_style="dim white",
        food_style="bold bright_white",
        super_food_style="bold bright_yellow",
        border_style="white",
        accent_style="white",
    ),
}

THEME_NAMES: List[str] = list(THEMES.keys())


def get_theme(name: str) -> Theme:
    return THEMES.get(name, THEMES["Nokia Classic"])
