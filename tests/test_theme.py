from snakegame.theme import THEMES, THEME_NAMES, get_theme


def test_theme_count_and_names():
    assert len(THEMES) == 5
    assert "Nokia Classic" in THEME_NAMES
    assert "Cyberpunk Neon" in THEME_NAMES
    assert "Retro Amber" in THEME_NAMES
    assert "Synthwave" in THEME_NAMES
    assert "Matrix Monochrome" in THEME_NAMES


def test_get_theme_valid():
    theme = get_theme("Cyberpunk Neon")
    assert theme.name == "Cyberpunk Neon"
    assert theme.border_style == "bright_magenta"


def test_get_theme_fallback():
    theme = get_theme("NonExistentTheme")
    assert theme.name == "Nokia Classic"
