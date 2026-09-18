from typing import Optional, List
from rich.align import Align
from rich.box import ROUNDED, DOUBLE, HEAVY
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from snakegame.board import Board, Point
from snakegame.config import GameConfig
from snakegame.food import Food, SuperFood
from snakegame.snake import Snake
from snakegame.theme import get_theme, THEME_NAMES


def format_timer(seconds: float) -> str:
    total_sec = int(seconds)
    minutes = total_sec // 60
    secs = total_sec % 60
    return f"{minutes:02d}:{secs:02d}"


class GameRenderer:
    def __init__(self, config: GameConfig, console: Optional[Console] = None) -> None:
        self.config = config
        self.console = console or Console(no_color=config.no_color)

    @property
    def theme(self):
        return get_theme(self.config.theme_name)

    def render_board(
        self,
        board: Board,
        snake: Snake,
        food: Optional[Food],
        super_food: Optional[SuperFood] = None,
    ) -> Panel:
        theme = self.theme
        lines = []
        body_list = list(snake.body)
        head = snake.head
        body_coords = set(body_list[1:])

        food_pos = food.position if food else None
        super_food_pos = super_food.position if super_food else None

        for y in range(board.height):
            row_text = Text()
            for x in range(board.width):
                pt = Point(x, y)
                if pt == head:
                    if self.config.no_color:
                        row_text.append("@@")
                    else:
                        row_text.append("██", style=theme.head_style)
                elif pt in body_coords:
                    if self.config.no_color:
                        row_text.append("##")
                    else:
                        try:
                            idx = body_list.index(pt)
                            style = theme.body_style if idx % 2 == 0 else theme.body_alt_style
                            row_text.append("██", style=style)
                        except ValueError:
                            row_text.append("██", style=theme.body_style)
                elif super_food_pos is not None and pt == super_food_pos:
                    if self.config.no_color:
                        row_text.append("**")
                    else:
                        row_text.append("★ ", style=theme.super_food_style)
                elif food_pos is not None and pt == food_pos:
                    if self.config.no_color:
                        row_text.append("<>")
                    else:
                        row_text.append("◆ ", style=theme.food_style)
                else:
                    row_text.append("  ")
            lines.append(row_text)

        board_content = Text("\n").join(lines)
        border_style = "white" if self.config.no_color else theme.border_style
        return Panel(
            board_content,
            border_style=border_style,
            box=ROUNDED,
            padding=(0, 1),
            title="[bold green]Snake Game CLI[/bold green]" if not self.config.no_color else "Snake Game CLI",
            title_align="center",
        )

    def render_stats_bar(
        self,
        score: int,
        high_score: int,
        elapsed_time: float,
        speed: float,
        length: int,
        super_food: Optional[SuperFood] = None,
        current_time: float = 0.0,
        is_paused: bool = False,
    ) -> Panel:
        theme = self.theme
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
            s_score = f"[{theme.accent_style}]SCORE:[/] [bold bright_white]{score}[/]"
            s_best = f"[yellow]BEST:[/] [bold bright_white]{high_score}[/]"
            s_time = f"[magenta]TIME:[/] [bold bright_white]{timer_str}[/]"
            s_speed = f"[blue]SPEED:[/] [bold bright_white]{speed:.1f}/s[/]"
            s_len = f"[{theme.accent_style}]LENGTH:[/] [bold bright_white]{length}[/]"

        table.add_row(s_score, s_best, s_time, s_speed, s_len)

        status_elements = []
        if is_paused:
            status_elements.append("[bold bright_yellow][ PAUSED - Press P or Space to Resume ][/]")

        if super_food is not None and not super_food.is_expired(current_time):
            left = super_food.time_left(current_time)
            badge = f"[bold bright_yellow]★ SUPERFOOD: {left:.1f}s (+50 PTS) ★[/bold bright_yellow]"
            status_elements.append(badge)

        footer_elements = ["[dim]Controls: [↑/W/↓/S/←/A/→/D] Move  [P/Space] Pause  [Q] Quit[/dim]"]
        if status_elements:
            footer_elements.extend(status_elements)

        footer_text = "  ".join(footer_elements) if not self.config.no_color else Text.from_markup(footer_text).plain

        content = Group(table, Align.center(Text.from_markup(footer_text)))
        border_style = "dim green" if not self.config.no_color else "white"
        return Panel(content, box=ROUNDED, border_style=border_style)

    def render_game_view(
        self,
        board: Board,
        snake: Snake,
        food: Optional[Food],
        score: int,
        high_score: int,
        elapsed_time: float,
        speed: float,
        super_food: Optional[SuperFood] = None,
        current_time: float = 0.0,
        is_paused: bool = False,
    ) -> Align:
        board_panel = self.render_board(board, snake, food, super_food)
        stats_panel = self.render_stats_bar(
            score=score,
            high_score=high_score,
            elapsed_time=elapsed_time,
            speed=speed,
            length=snake.length,
            super_food=super_food,
            current_time=current_time,
            is_paused=is_paused,
        )
        combined = Group(board_panel, stats_panel)
        return Align.center(combined)

    def render_main_menu(self, selected_index: int, high_score: int) -> Align:
        theme = self.theme
        menu_items = [
            "Start Game",
            "Settings",
            "About Creator",
            "Exit",
        ]

        header_text = Text()
        header_text.append("  ╔═══════════════════════════════════════════════════╗\n", style="bold bright_green")
        header_text.append("  ║                S N A K E   G A M E                ║\n", style="bold bright_green")
        header_text.append("  ║                  Terminal CLI Edition             ║\n", style="bold bright_green")
        header_text.append("  ╚═══════════════════════════════════════════════════╝\n", style="bold bright_green")

        menu_table = Table.grid(padding=(1, 2))
        menu_table.add_column(justify="center", min_width=30)

        for i, item in enumerate(menu_items):
            if i == selected_index:
                styled_item = f"[bold bright_black on bright_green]  ▶  {item.upper()}  ◀  [/]"
            else:
                styled_item = f"[dim white]     {item}     [/dim white]"
            menu_table.add_row(styled_item)

        best_score_text = Text.from_markup(f"\n[yellow]★ All-Time High Score:[/] [bold bright_white]{high_score}[/]\n")
        nav_hints = Text.from_markup("[dim]Use [↑/W] & [↓/S] to Navigate  •  Press [ENTER/SPACE] to Select  •  [Q] Exit[/dim]")

        content = Group(
            Align.center(header_text),
            Align.center(best_score_text),
            Align.center(menu_table),
            Align.center(Text("")),
            Align.center(nav_hints),
        )

        panel = Panel(
            content,
            box=DOUBLE,
            border_style=theme.border_style if not self.config.no_color else "white",
            padding=(1, 3),
            title="[bold green]Snake Game CLI[/bold green]" if not self.config.no_color else "Snake Game CLI",
            title_align="center",
        )
        return Align.center(panel)

    def render_settings_menu(
        self,
        config: GameConfig,
        selected_index: int,
        term_width: int,
        term_height: int,
    ) -> Align:
        theme = self.theme
        settings_items = [
            ("Arena Width", f"< {config.width} cells >"),
            ("Arena Height", f"< {config.height} cells >"),
            ("Color Theme", f"< {config.theme_name} >"),
            ("Initial Speed", f"< {config.initial_speed:.1f} moves/sec >"),
            ("SuperFood (Bonus)", f"< {'ENABLED' if config.super_food_enabled else 'DISABLED'} >"),
            ("Action", "[ SAVE & RETURN TO MAIN MENU ]"),
        ]

        title = Text("S E T T I N G S   &   C U S T O M I Z A T I O N\n", style="bold bright_cyan")

        # Live terminal dimension info
        req_width = config.width * 2 + 6
        req_height = config.height + 9
        size_info = Text.from_markup(
            f"[dim]Live Terminal Size: [bold bright_white]{term_width} cols × {term_height} lines[/bold bright_white] "
            f"| Arena Requires: [bold bright_white]≥ {req_width} × {req_height}[/bold bright_white][/dim]\n"
        )

        warning_text = Text()
        if term_width < req_width or term_height < req_height:
            warning_text = Text.from_markup(
                "[bold bright_red]⚠️ Warning:[/] Your terminal window is smaller than current arena dimensions!\n"
                "[dim]Please expand the terminal window or decrease arena dimensions.[/dim]\n"
            )

        table = Table(box=ROUNDED, border_style=theme.border_style, show_header=False, expand=True)
        table.add_column("Option", style="bold white", ratio=4)
        table.add_column("Value", justify="center", ratio=6)

        for i, (opt, val) in enumerate(settings_items):
            if i == selected_index:
                opt_str = f"[bold bright_green]▶ {opt}[/]"
                val_str = f"[bold bright_black on bright_green]  {val}  [/]"
            else:
                opt_str = f"  {opt}"
                val_str = f"[cyan]{val}[/]"
            table.add_row(opt_str, val_str)

        instructions = Text.from_markup(
            "\n[dim][↑/W/↓/S] Navigate  •  [←/A/→/D] Change Value  •  [ENTER/SPACE] Select  •  [ESC/B] Back to Menu[/dim]"
        )

        content = Group(
            Align.center(title),
            Align.center(size_info),
            Align.center(warning_text) if warning_text.plain else Text(),
            table,
            Align.center(instructions),
        )

        panel = Panel(
            content,
            box=DOUBLE,
            border_style=theme.border_style,
            padding=(1, 3),
            title="[bold cyan]GAME CONFIGURATION[/bold cyan]",
            title_align="center",
        )
        return Align.center(panel)

    def render_about_creator(self) -> Align:
        theme = self.theme
        title = Text("A B O U T   T H E   C R E A T O R\n", style="bold bright_green")

        card = Table.grid(padding=(0, 2))
        card.add_column(justify="right", style="bold cyan")
        card.add_column(justify="left", style="white")

        card.add_row("Author:", "Made with ❤️ by [bold bright_yellow]ItsReZNuM[/]")
        card.add_row("GitHub Profile:", "https://github.com/ItsReZNuM")
        card.add_row("Repository:", "https://github.com/ItsReZNuM/SnakeGame-CLI")
        card.add_row("Telegram:", "t.me/ItsReZNuM")
        card.add_row("Instagram:", "instagram.com/rez.num")

        star_msg = (
            "\n[bold bright_yellow]⭐ Enjoying the game?[/bold bright_yellow]\n"
            "[white]Please consider starring the repository on GitHub! It means a lot and supports development.[/white]\n"
            "[bold cyan]https://github.com/ItsReZNuM/SnakeGame-CLI[/bold cyan]\n"
        )

        prompt = Text.from_markup("[dim]Press [ESC], [B], [M] or [ENTER] to return to Main Menu[/dim]")

        content = Group(
            Align.center(title),
            Align.center(card),
            Align.center(Text.from_markup(star_msg)),
            Align.center(prompt),
        )

        panel = Panel(
            content,
            box=DOUBLE,
            border_style=theme.border_style,
            padding=(1, 4),
            title="[bold green]ABOUT CREATOR[/bold green]",
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
        super_foods_eaten: int = 0,
    ) -> Align:
        title_style = "bold bright_red" if not self.config.no_color else "bold"
        border_style = "red" if not self.config.no_color else "white"

        banner = Text()
        banner.append("  ╔═══════════════════════════════════════════════════╗\n", style=title_style)
        banner.append("  ║               G A M E   O V E R                   ║\n", style=title_style)
        banner.append("  ╚═══════════════════════════════════════════════════╝\n", style=title_style)

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
        table.add_row("Food Eaten:", str(max(0, snake_length - 3 - (super_foods_eaten * 2))))
        table.add_row("SuperFoods Eaten:", str(super_foods_eaten))

        star_reminder = (
            "\n[dim]Enjoyed the game? Star the project on GitHub: [bold cyan]github.com/ItsReZNuM/SnakeGame-CLI[/bold cyan][/dim]\n"
            "[dim]Made with ❤️ by [bold yellow]ItsReZNuM[/bold yellow][/dim]\n"
        )

        prompt_markup = (
            "[bold bright_green]Press [R] to Play Again[/bold bright_green]  •  "
            "[bold cyan][M] Main Menu[/bold cyan]  •  [dim][Q] Quit[/dim]"
        )

        content = Group(
            Align.center(banner),
            Align.center(Text.from_markup(high_note)) if high_note else Text(),
            Align.center(table),
            Align.center(Text.from_markup(star_reminder)),
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
