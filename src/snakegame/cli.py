import argparse
import sys
from typing import List, Optional

from rich.align import Align
from rich.box import DOUBLE, ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from snakegame import __version__
from snakegame.config import ConfigError, GameConfig
from snakegame.game import Game
from snakegame.theme import THEME_NAMES


class RichArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser that routes help and errors through Rich."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, add_help=False, **kwargs)

    def error(self, message: str) -> None:
        console = Console(stderr=True)
        console.print(f"[bold red]Error:[/] {message}")
        console.print("[dim]Run [bold cyan]snakegame --help[/bold cyan] for usage and options.[/dim]")
        sys.exit(2)


def display_help(console: Console) -> None:
    header = Text()
    header.append("  ╔════════════════════════════════════════════════════════════╗\n", style="bold bright_green")
    header.append("  ║                     S N A K E   G A M E                    ║\n", style="bold bright_green")
    header.append("  ║                    Terminal CLI Edition                    ║\n", style="bold bright_green")
    header.append("  ╚════════════════════════════════════════════════════════════╝", style="bold bright_green")

    banner_panel = Panel(
        Align.center(header),
        box=ROUNDED,
        border_style="bright_green",
        subtitle=f"[dim]Version {__version__}[/dim]",
        subtitle_align="right",
    )

    usage_text = Text.from_markup(
        "[bold cyan]Usage:[/bold cyan]  [bold green]snakegame[/bold green] [options]\n"
        "[bold cyan]Module:[/bold cyan] [bold green]python -m snakegame[/bold green] [options]"
    )

    options_table = Table(box=ROUNDED, border_style="dim green", show_header=True, expand=True)
    options_table.add_column("Option", style="bold yellow", ratio=3)
    options_table.add_column("Default", style="cyan", ratio=2)
    options_table.add_column("Description", style="white", ratio=6)

    options_table.add_row("-w, --width <int>", "24", "Grid width in cells (range: 10 - 60)")
    options_table.add_row("-H, --height <int>", "16", "Grid height in cells (range: 8 - 35)")
    options_table.add_row("-s, --speed <float>", "6.0", "Initial movement speed in moves/sec (1.0 - 25.0)")
    options_table.add_row("-t, --theme <str>", "Nokia Classic", f"Color theme: {', '.join(THEME_NAMES)}")
    options_table.add_row("--no-color", "False", "Disable terminal colors (monochrome mode)")
    options_table.add_row("-v, --version", "-", "Display version information and exit")
    options_table.add_row("-h, --help", "-", "Show this polished help guide and exit")

    features_table = Table(box=ROUNDED, border_style="dim cyan", show_header=True, expand=True)
    features_table.add_column("Feature", style="bold cyan", ratio=3)
    features_table.add_column("Details", style="white", ratio=7)

    features_table.add_row("Interactive Menu", "Start Game, Settings, About Creator, Exit")
    features_table.add_row("Custom Settings", "Real-time terminal dimension preview, theme picker, size adjust")
    features_table.add_row("Custom Keybindings", "Remap movement & pause keys in Settings with persistence")
    features_table.add_row("5 Color Themes", "Nokia Classic, Cyberpunk Neon, Retro Amber, Synthwave, Matrix")
    features_table.add_row("SuperFood (Bonus)", "Spawns every 5 foods with a 5-second countdown timer (+50 pts, +3 size)")
    features_table.add_row("Wrap-Around Walls", "Snake teleports through boundaries to opposite side")
    features_table.add_row("Death Indicator", "Head flashes red cross upon collision to show defeat location")

    controls_table = Table(box=ROUNDED, border_style="dim green", show_header=True, expand=True)
    controls_table.add_column("Action", style="bold cyan", ratio=3)
    controls_table.add_column("Keys", style="bold bright_white", ratio=5)

    controls_table.add_row("Move Snake / Navigate", "Arrow Keys (↑ ↓ ← →) or Custom Keys (WASD default)")
    controls_table.add_row("Select / Confirm", "Enter  or  Spacebar")
    controls_table.add_row("Back / Cancel", "ESC  or  B")
    controls_table.add_row("Pause / Resume", "Spacebar,  ESC,  or  P")
    controls_table.add_row("Restart Game", "R  (on Game Over)")
    controls_table.add_row("Main Menu", "M  (on Game Over or Pause)")
    controls_table.add_row("Quit", "Q  or  ESC (on Main Menu / Game Over)")

    examples_text = Text.from_markup(
        "[bold]Standard Game:[/]            [green]snakegame[/green]\n"
        "[bold]Custom Dimensions:[/]        [green]snakegame --width 32 --height 20[/green]\n"
        "[bold]Cyberpunk Theme:[/]          [green]snakegame --theme \"Cyberpunk Neon\"[/green]\n"
        "[bold]Fast Challenge Mode:[/]      [green]snakegame --speed 10.0[/green]\n"
        "[bold]Monochrome Mode:[/]          [green]snakegame --no-color[/green]"
    )

    console.print(banner_panel)
    console.print(Panel(usage_text, title="[bold]Execution Syntax[/bold]", box=ROUNDED, border_style="cyan"))
    console.print(Panel(options_table, title="[bold]Available CLI Options[/bold]", box=ROUNDED, border_style="green"))
    console.print(Panel(features_table, title="[bold]Game Features[/bold]", box=ROUNDED, border_style="cyan"))
    console.print(Panel(controls_table, title="[bold]In-Game Controls[/bold]", box=ROUNDED, border_style="yellow"))
    console.print(Panel(examples_text, title="[bold]Examples[/bold]", box=ROUNDED, border_style="magenta"))


def display_version(console: Console) -> None:
    text = Text.from_markup(
        f"[bold bright_green]SnakeGame CLI[/bold bright_green] "
        f"[bold cyan]v{__version__}[/bold cyan] "
        f"[dim]• Terminal Edition[/dim]"
    )
    console.print(Panel(Align.center(text), box=ROUNDED, border_style="bright_green"))


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = RichArgumentParser(description="SnakeGame CLI - Classic Terminal Edition.")
    parser.add_argument("-w", "--width", type=int, default=24, help="Grid width in cells")
    parser.add_argument("-H", "--height", type=int, default=16, help="Grid height in cells")
    parser.add_argument("-s", "--speed", type=float, default=6.0, help="Initial speed in moves/second")
    parser.add_argument("-t", "--theme", type=str, default=None, choices=THEME_NAMES, help="Color theme")
    parser.add_argument("--no-color", action="store_true", default=False, help="Disable ANSI color codes")
    parser.add_argument("-v", "--version", action="store_true", help="Show version and exit")
    parser.add_argument("-h", "--help", action="store_true", help="Show help and exit")

    return parser.parse_args(argv)


def configure_terminal() -> None:
    if sys.platform == "win32":
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main(argv: Optional[List[str]] = None) -> int:
    configure_terminal()
    console = Console()
    try:
        args = parse_args(argv)

        if args.help:
            display_help(console)
            return 0

        if args.version:
            display_version(console)
            return 0

        config = GameConfig(no_color=args.no_color)
        config.load_saved_settings()

        # Command line arguments override saved settings if specified
        if args.width != 24 or "--width" in sys.argv or "-w" in sys.argv:
            config.width = args.width
        if args.height != 16 or "--height" in sys.argv or "-H" in sys.argv:
            config.height = args.height
        if args.speed != 6.0 or "--speed" in sys.argv or "-s" in sys.argv:
            config.initial_speed = args.speed
        if args.theme:
            config.theme_name = args.theme
        if args.no_color:
            config.no_color = True

        config.validate()

    except ConfigError as exc:
        console.print(f"[bold red]Configuration Error:[/] {exc}")
        console.print("[dim]Run [bold cyan]snakegame --help[/bold cyan] for valid configuration boundaries.[/dim]")
        return 1
    except KeyboardInterrupt:
        return 0

    game = Game(config=config, console=Console(no_color=config.no_color))
    game.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
