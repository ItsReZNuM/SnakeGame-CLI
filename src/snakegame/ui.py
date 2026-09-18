from typing import Optional, Set
from rich.align import Align
from rich.box import ROUNDED, DOUBLE, SIMPLE
from rich.console import Console, RenderableType, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from snakegame.board import Board, Point
from snakegame.config import GameConfig
from snakegame.food import Food
from snakegame.snake import Snake


def format_timer(seconds: float) -> str:
    total_sec = int(seconds)
    minutes = total_sec // 60
    secs = total_sec % 60
    return f"{minutes:02d}:{secs:02d}"


class GameRenderer:
    def __init__(self, config: GameConfig, console: Optional[Console] = None) -> None:
        self.config = config
        self.console = console or Console(no_color=config.no_color)

    def render_board(self, board: Board, snake: Snake, food: Optional[Food]) -> Panel:
        lines = []
        body_list = list(snake.body)
        head = snake.head
        body_coords = set(body_list[1:])

        food_pos = food.position if food else None

        for y in range(board.height):
            row_text = Text()
            for x in range(board.width):
                pt = Point(x, y)
                if pt == head:
                    if self.config.no_color:
                        row_text.append("@@")
                    else:
                        row_text.append("██", style="bold bright_yellow")
                elif pt in body_coords:
                    if self.config.no_color:
                        row_text.append("##")
                    else:
                        # Alternate segment brightness for a classic segmented look
                        try:
                            idx = body_list.index(pt)
                            if idx % 2 == 0:
                                row_text.append("██", style="bold bright_green")
                            else:
                                row_text.append("██", style="green")
                        except ValueError:
                            row_text.append("██", style="bold green")
                elif food_pos is not None and pt == food_pos:
                    if self.config.no_color:
                        row_text.append("<>")
                    else:
                        row_text.append("◆ ", style="bold bright_red")
                else:
                    row_text.append("  ")
            lines.append(row_text)

        board_content = Text("\n").join(lines)
        border_style = "white" if self.config.no_color else "bright_green"
        return Panel(
            board_content,
            border_style=border_style,
            box=ROUNDED,
            padding=(0, 1),
            title="[bold green]NOKIA 3310[/bold green]" if not self.config.no_color else "SNAKE",
            title_align="center",
        )

    def render_stats_bar(
        self,
        score: int,
        high_score: int,
        elapsed_time: float,
        speed: float,
        length: int,
        is_paused: bool = False,
    ) -> Panel:
        table = Table.grid(expand=True)
        table.add_column(justify="center", ratio=1)
        table.add_column(justify="center", ratio=1)
        table.add_column(justify="center", ratio=1)
        table.add_column(justify="center", ratio=1)
        table.add_column(justify="center", ratio=1)

        timer_str = format_timer(elapsed_time)

        if self.config.no_color:
            s_score = f"SCORE: {score}"
            s_best = f"BEST: {high_score}"
            s_time = f"TIME: {timer_str}"
            s_speed = f"SPEED: {speed:.1f}/s"
            s_len = f"LENGTH: {length}"
        else:
            s_score = f"[cyan]SCORE:[/] [bold bright_white]{score}[/]"
            s_best = f"[yellow]BEST:[/] [bold bright_white]{high_score}[/]"
            s_time = f"[magenta]TIME:[/] [bold bright_white]{timer_str}[/]"
            s_speed = f"[blue]SPEED:[/] [bold bright_white]{speed:.1f}/s[/]"
            s_len = f"[green]LENGTH:[/] [bold bright_white]{length}[/]"

        table.add_row(s_score, s_best, s_time, s_speed, s_len)

        status = ""
        if is_paused:
            status = " [bold bright_yellow][ PAUSED - Press P or Space to Resume ][/]"

        footer_text = (
            "[dim]Controls: [↑/W/↓/S/←/A/→/D] Move  [P/Space] Pause  [Q] Quit[/dim]" + status
            if not self.config.no_color
            else "Controls: [WASD/Arrows] Move  [P/Space] Pause  [Q] Quit"
            + (" [PAUSED]" if is_paused else "")
        )

        content = Group(table, Align.center(Text.from_markup(footer_text)))
        return Panel(content, box=ROUNDED, border_style="dim green" if not self.config.no_color else "white")

    def render_game_view(
        self,
        board: Board,
        snake: Snake,
        food: Optional[Food],
        score: int,
        high_score: int,
        elapsed_time: float,
        speed: float,
        is_paused: bool = False,
    ) -> Align:
        board_panel = self.render_board(board, snake, food)
        stats_panel = self.render_stats_bar(
            score=score,
            high_score=high_score,
            elapsed_time=elapsed_time,
            speed=speed,
            length=snake.length,
            is_paused=is_paused,
        )
        combined = Group(board_panel, stats_panel)
        return Align.center(combined)

    def render_start_screen(self, high_score: int) -> Align:
        title_style = "bold bright_green" if not self.config.no_color else "bold"
        border_style = "green" if not self.config.no_color else "white"

        header_text = Text()
        header_text.append("  ╔════════════════════════════════════════╗\n", style=title_style)
        header_text.append("  ║        S N A K E   C L A S S I C       ║\n", style=title_style)
        header_text.append("  ║       Retro Nokia 3310 Edition         ║\n", style=title_style)
        header_text.append("  ╚════════════════════════════════════════╝\n", style=title_style)

        info_table = Table.grid(padding=(0, 2))
        info_table.add_column(justify="right", style="bold cyan" if not self.config.no_color else "bold")
        info_table.add_column(justify="left")

        info_table.add_row("Movement:", "Arrow Keys (↑ ↓ ← →) or W / A / S / D")
        info_table.add_row("Pause:", "P or Spacebar")
        info_table.add_row("Quit:", "Q or Escape")
        info_table.add_row("All-Time Best:", f"{high_score} points")

        prompt_markup = (
            "\n[bold bright_green]▶ Press [SPACE] or [ENTER] to Begin ◀[/]\n"
            "[dim]Press [Q] to Quit[/dim]"
            if not self.config.no_color
            else "\n▶ Press [SPACE] or [ENTER] to Begin ◀\nPress [Q] to Quit"
        )
        prompt_text = Align.center(Text.from_markup(prompt_markup))

        content = Group(
            Align.center(header_text),
            Align.center(info_table),
            prompt_text,
        )

        panel = Panel(
            content,
            box=DOUBLE,
            border_style=border_style,
            padding=(1, 2),
            title="[bold green]NOKIA ARCADE[/bold green]" if not self.config.no_color else "SNAKE",
            title_align="center",
        )
        return Align.center(panel)

    def render_game_over_screen(
        self,
        score: int,
        high_score: int,
        elapsed_time: float,
        snake_length: int,
        is_new_high: bool,
    ) -> Align:
        title_style = "bold bright_red" if not self.config.no_color else "bold"
        border_style = "red" if not self.config.no_color else "white"

        banner = Text()
        banner.append("  ╔════════════════════════════════════════╗\n", style=title_style)
        banner.append("  ║           G A M E   O V E R            ║\n", style=title_style)
        banner.append("  ╚════════════════════════════════════════╝\n", style=title_style)

        high_note = ""
        if is_new_high and score > 0:
            high_note = (
                "[bold bright_yellow]★ NEW HIGH SCORE! CONGRATULATIONS! ★[/]\n\n"
                if not self.config.no_color
                else "★ NEW HIGH SCORE! CONGRATULATIONS! ★\n\n"
            )

        table = Table.grid(padding=(0, 2))
        table.add_column(justify="right", style="bold yellow" if not self.config.no_color else "bold")
        table.add_column(justify="left", style="bold bright_white" if not self.config.no_color else "")

        table.add_row("Final Score:", str(score))
        table.add_row("High Score:", str(high_score))
        table.add_row("Survival Time:", format_timer(elapsed_time))
        table.add_row("Snake Length:", str(snake_length))
        table.add_row("Food Eaten:", str(max(0, snake_length - 3)))

        prompt_markup = (
            "\n[bold bright_green]Press [R] to Play Again[/bold bright_green]  •  [dim]Press [Q] to Quit[/dim]"
            if not self.config.no_color
            else "\nPress [R] to Play Again  •  Press [Q] to Quit"
        )

        content = Group(
            Align.center(banner),
            Align.center(Text.from_markup(high_note)) if high_note else Text(),
            Align.center(table),
            Align.center(Text.from_markup(prompt_markup)),
        )

        panel = Panel(
            content,
            box=ROUNDED,
            border_style=border_style,
            padding=(1, 3),
            title="[bold red]GAME OVER[/bold red]" if not self.config.no_color else "GAME OVER",
            title_align="center",
        )
        return Align.center(panel)
