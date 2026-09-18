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
    header.append("  ╔═════════════════════════════════════════════════════════════╗\n", style="bold bright_green")
    header.append("  ║                     S N A K E   G A M E                     ║\n", style="bold bright_green")
    header.append("  ║                 Classic Nokia Terminal Edition              ║\n", style="bold bright_green")
    header.append("  ╚═════════════════════════════════════════════════════════════╝", style="bold bright_green")

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
    options_table.add_row("--no-color", "False", "Disable terminal colors (monochrome mode)")
    options_table.add_row("-v, --version", "-", "Display version information and exit")
    options_table.add_row("-h, --help", "-", "Show this polished help guide and exit")

    controls_table = Table(box=ROUNDED, border_style="dim green", show_header=True, expand=True)
    controls_table.add_column("Action", style="bold cyan", ratio=3)
    controls_table.add_column("Keys", style="bold bright_white", ratio=5)

    controls_table.add_row("Move Snake", "Arrow Keys (↑ ↓ ← →) or W / A / S / D")
    controls_table.add_row("Pause / Resume", "P  or  Spacebar")
    controls_table.add_row("Restart Game", "R  (on Game Over)")
    controls_table.add_row("Quit", "Q  or  ESC")

    examples_text = Text.from_markup(
        "[bold]Standard Game:[/]            [green]snakegame[/green]\n"
        "[bold]Larger Custom Arena:[/]      [green]snakegame --width 32 --height 20[/green]\n"
        "[bold]Fast Challenge Mode:[/]      [green]snakegame --speed 10.0[/green]\n"
        "[bold]Monochrome Mode:[/]          [green]snakegame --no-color[/green]"
    )

    console.print(banner_panel)
    console.print(Panel(usage_text, title="[bold]Execution Syntax[/bold]", box=ROUNDED, border_style="cyan"))
    console.print(Panel(options_table, title="[bold]Available CLI Options[/bold]", box=ROUNDED, border_style="green"))
    console.print(Panel(controls_table, title="[bold]In-Game Controls[/bold]", box=ROUNDED, border_style="yellow"))
    console.print(Panel(examples_text, title="[bold]Examples[/bold]", box=ROUNDED, border_style="magenta"))


def display_version(console: Console) -> None:
    text = Text.from_markup(
        f"[bold bright_green]SnakeGame CLI[/bold bright_green] "
        f"[bold cyan]v{__version__}[/bold cyan] "
        f"[dim]• Retro Nokia 3310 Terminal Edition[/dim]"
    )
    console.print(Panel(Align.center(text), box=ROUNDED, border_style="bright_green"))


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = RichArgumentParser(description="Classic Retro Nokia Snake for the Terminal.")
    parser.add_argument("-w", "--width", type=int, default=24, help="Grid width in cells")
    parser.add_argument("-H", "--height", type=int, default=16, help="Grid height in cells")
    parser.add_argument("-s", "--speed", type=float, default=6.0, help="Initial speed in moves/second")
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

        config = GameConfig(
            width=args.width,
            height=args.height,
            initial_speed=args.speed,
            no_color=args.no_color,
        )
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
