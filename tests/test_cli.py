from rich.console import Console
from snakegame.cli import display_help, display_version, parse_args


def test_parse_args_defaults():
    args = parse_args([])
    assert args.width == 24
    assert args.height == 16
    assert args.speed == 6.0
    assert args.no_color is False
    assert args.help is False
    assert args.version is False


def test_parse_args_custom():
    args = parse_args(["--width", "30", "--height", "20", "--speed", "8.5", "--no-color"])
    assert args.width == 30
    assert args.height == 20
    assert args.speed == 8.5
    assert args.no_color is True


def test_display_help_renders_without_exception():
    console = Console(record=True)
    display_help(console)
    output = console.export_text()
    assert "S N A K E   G A M E" in output
    assert "--width" in output
    assert "In-Game Controls" in output


def test_display_version_renders_without_exception():
    console = Console(record=True)
    display_version(console)
    output = console.export_text()
    assert "SnakeGame CLI" in output
    assert "0.1.0" in output
