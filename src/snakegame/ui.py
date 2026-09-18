from typing import Optional, List
from rich.align import Align
from rich.box import ROUNDED, DOUBLE, HEAVY, HORIZONTALS
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
        is_paused: bool = False,
        is_dying: bool = False,
        death_flash: bool = False,
    ) -> Panel:
        theme = self.theme
        lines = []
        body_list = list(snake.body)
        head = snake.head
        body_coords = set(body_list[1:])

        food_pos = food.position if food else None
        super_food_pos = super_food.position if super_food else None

        mid_y = board.height // 2

        for y in range(board.height):
            # If paused, render high-visibility pause banner across the center rows
            if is_paused and y == mid_y:
                banner_str = " ⏸   P A U S E D   ⏸ "
                row_width = board.width * 2
                padded_banner = banner_str.center(row_width)
                if self.config.no_color:
                    row_text = Text(padded_banner, style="reverse")
                else:
                    row_text = Text(padded_banner, style="bold bright_black on bright_yellow")
                lines.append(row_text)
                continue
            elif is_paused and y == mid_y + 1:
                prompt_str = " Press SPACE, ESC or P to Resume • M for Menu "
                row_width = board.width * 2
                padded_prompt = prompt_str.center(row_width)
                if self.config.no_color:
                    row_text = Text(padded_prompt, style="bold")
                else:
                    row_text = Text(padded_prompt, style="bold white on grey19")
                lines.append(row_text)
                continue

            row_text = Text()
            for x in range(board.width):
                pt = Point(x, y)
                if pt == head:
                    if is_dying:
                        if death_flash:
                            if self.config.no_color:
                                row_text.append("XX")
                            else:
                                row_text.append("XX", style="bold bright_white on bright_red")
                        else:
                            row_text.append("  ")
                    elif self.config.no_color:
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
        panel_width = max(54, board.width * 2 + 4)

        return Panel(
            Align.center(board_content),
            border_style=border_style,
            box=ROUNDED,
            width=panel_width,
            padding=(0, 1),
            title="[bold green]Snake Game CLI[/bold green]" if not self.config.no_color else "Snake Game CLI",
            title_align="center",
        )

    def render_stats_bar(
        self,
        board: Board,
        score: int,
        high_score: int,
        elapsed_time: float,
        speed: float,
        length: int,
        regular_foods_eaten: int = 0,
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

        # Dedicated SuperFood status line (prevents layout jumping)
        if super_food is not None and not super_food.is_expired(current_time):
            left = super_food.time_left(current_time)
            super_line = f"[bold bright_yellow]★ SUPERFOOD: {left:.1f}s (+50 PTS / +3 LENGTH) ★[/bold bright_yellow]"
        elif self.config.super_food_enabled:
            next_in = self.config.super_food_interval - (regular_foods_eaten % self.config.super_food_interval)
            super_line = f"[dim]★ SuperFood spawns in {next_in} food{'s' if next_in != 1 else ''} ★[/dim]"
        else:
            super_line = "[dim]★ SuperFood: Disabled ★[/dim]"

        footer_text = "[dim]Controls: [↑/W/↓/S/←/A/→/D] Move  [P] Pause  [M] Menu  [Q] Quit[/dim]"

        content = Group(
            table,
            Text(""),
            Align.center(Text.from_markup(super_line) if not self.config.no_color else Text(super_line)),
            Align.center(Text.from_markup(footer_text) if not self.config.no_color else Text(footer_text)),
        )

        panel_width = max(54, board.width * 2 + 4)
        border_style = "dim green" if not self.config.no_color else "white"
        return Panel(content, box=ROUNDED, width=panel_width, border_style=border_style)

    def render_game_view(
        self,
        board: Board,
        snake: Snake,
        food: Optional[Food],
        score: int,
        high_score: int,
        elapsed_time: float,
        speed: float,
        regular_foods_eaten: int = 0,
        super_food: Optional[SuperFood] = None,
        current_time: float = 0.0,
        is_paused: bool = False,
        is_dying: bool = False,
        death_flash: bool = False,
    ) -> Align:
        board_panel = self.render_board(
            board, snake, food, super_food, is_paused=is_paused, is_dying=is_dying, death_flash=death_flash
        )
        stats_panel = self.render_stats_bar(
            board=board,
            score=score,
            high_score=high_score,
            elapsed_time=elapsed_time,
            speed=speed,
            length=snake.length,
            regular_foods_eaten=regular_foods_eaten,
            super_food=super_food,
            current_time=current_time,
            is_paused=is_paused,
        )
        combined = Group(board_panel, stats_panel)
        return Align.center(combined)

    def render_main_menu(
        self,
        selected_index: int,
        high_score: int,
        terminal_name: Optional[str] = None,
    ) -> Align:
        theme = self.theme
        menu_items = [
            "Start Game",
            "Settings",
            "About Creator",
            "Exit",
        ]

        # Inner header panel with double border for clean, distortion-free rendering
        header_panel = Panel(
            Align.center(
                Text(
                    "S N A K E   G A M E\nTerminal CLI Edition",
                    style="bold bright_green" if not self.config.no_color else "bold white",
                )
            ),
            box=DOUBLE,
            border_style="bold bright_green" if not self.config.no_color else "white",
            width=46,
            padding=(0, 1),
        )

        best_score_text = Text.from_markup(
            f"[yellow]★ All-Time High Score:[/] [bold bright_white]{high_score} points[/bold bright_white]"
        )

        BUTTON_WIDTH = 28
        menu_elements = []
        for i, item in enumerate(menu_items):
            if i == selected_index:
                label = f"▶   {item.upper()}   ◀"
                padded = label.center(BUTTON_WIDTH)
                if self.config.no_color:
                    btn = Text(padded, style="reverse")
                else:
                    btn = Text(padded, style=f"bold bright_black on {theme.accent_style}")
            else:
                label = item
                padded = label.center(BUTTON_WIDTH)
                if self.config.no_color:
                    btn = Text(padded, style="white")
                else:
                    btn = Text(padded, style="bold bright_white on grey19")
            menu_elements.append(Align.center(btn))
            menu_elements.append(Text(""))

        divider = Text("─" * 46, style="dim green" if not self.config.no_color else "dim white")
        nav_hints = Text.from_markup(
            "[dim][bold bright_white]↑/W/↓/S[/] Navigate  •  [bold bright_white]ENTER/SPACE[/] Select  •  [bold bright_white]Q[/] Exit[/dim]"
        )

        footer_items = [
            Align.center(divider),
            Text("\n"),
            Align.center(nav_hints),
        ]
        if terminal_name:
            footer_items.extend([
                Text("\n"),
                Align.center(Text.from_markup(f"[dim]Terminal: [bright_black]{terminal_name}[/bright_black][/dim]")),
            ])

        content = Group(
            Align.center(header_panel),
            Text("\n"),
            Align.center(best_score_text),
            Text("\n"),
            *menu_elements,
            *footer_items,
        )

        panel = Panel(
            content,
            box=DOUBLE,
            width=64,
            border_style=theme.border_style if not self.config.no_color else "white",
            padding=(1, 2),
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
        terminal_name: Optional[str] = None,
    ) -> Align:
        theme = self.theme
        settings_items = [
            ("Arena Width", f"< {config.width} cells >"),
            ("Arena Height", f"< {config.height} cells >"),
            ("Color Theme", f"< {config.theme_name} >"),
            ("Initial Speed", f"< {config.initial_speed:.1f} moves/sec >"),
            ("SuperFood (Bonus)", f"< {'ENABLED' if config.super_food_enabled else 'DISABLED'} >"),
            ("Keybindings", "[ CONFIGURE KEYS > ]"),
            ("Action", "[ SAVE & RETURN ]"),
        ]

        title = Text("S E T T I N G S   &   C U S T O M I Z A T I O N\n", style="bold bright_cyan")

        req_width = max(54, config.width * 2 + 4)
        req_height = config.height + 9
        term_label = f"Env: [bold bright_white]{terminal_name}[/] | " if terminal_name else ""
        size_info = Text.from_markup(
            f"[dim]{term_label}Size: [bold bright_white]{term_width} cols × {term_height} lines[/bold bright_white] "
            f"| Arena Needs: [bold bright_white]≥ {req_width} × {req_height}[/bold bright_white][/dim]\n"
        )

        warning_text = Text()
        if term_width < req_width or term_height < req_height:
            warning_text = Text.from_markup(
                "[bold bright_red]⚠️ Warning:[/] Terminal is smaller than arena requirements!\n"
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
            "\n[dim][bold bright_white]↑/↓[/] Navigate  •  [bold bright_white]←/→[/] Change  •  "
            "[bold bright_white]ENTER[/] Select  •  [bold bright_white]ESC[/] Back[/dim]"
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
            width=64,
            border_style=theme.border_style,
            padding=(1, 2),
            title="[bold cyan]GAME CONFIGURATION[/bold cyan]",
            title_align="center",
        )
        return Align.center(panel)

    def render_keybindings_menu(
        self,
        config: GameConfig,
        selected_index: int,
        binding_target: Optional[str] = None,
    ) -> Align:
        theme = self.theme
        title = Text("K E Y B I N D I N G S\n", style="bold bright_cyan")

        bindings = config.keybindings
        items = [
            ("Move Up", bindings.get("up", "w").upper()),
            ("Move Down", bindings.get("down", "s").upper()),
            ("Move Left", bindings.get("left", "a").upper()),
            ("Move Right", bindings.get("right", "d").upper()),
            ("Pause Game", bindings.get("pause", "p").upper()),
            ("Reset Defaults", "[ RESTORE DEFAULT KEYS ]"),
            ("Back to Settings", "[ RETURN TO SETTINGS ]"),
        ]

        action_keys = ["up", "down", "left", "right", "pause"]

        table = Table(box=ROUNDED, border_style=theme.border_style, show_header=False, expand=True)
        table.add_column("Action", style="bold white", ratio=5)
        table.add_column("Assigned Key", justify="center", ratio=5)

        for i, (act, val) in enumerate(items):
            if binding_target is not None and i < len(action_keys) and action_keys[i] == binding_target:
                opt_str = f"[bold yellow]▶ {act}[/]"
                val_str = "[bold bright_white on red] [ PRESS ANY KEY... ] [/]"
            elif i == selected_index:
                opt_str = f"[bold bright_green]▶ {act}[/]"
                val_str = f"[bold bright_black on bright_green]  {val}  [/]"
            else:
                opt_str = f"  {act}"
                val_str = f"[cyan]{val}[/]"
            table.add_row(opt_str, val_str)

        if binding_target is not None:
            prompt = Text.from_markup(
                "\n[bold bright_yellow]Press any key to bind, or [ESC] to cancel[/bold bright_yellow]"
            )
        else:
            prompt = Text.from_markup(
                "\n[dim][bold bright_white]↑/↓[/] Navigate  •  [bold bright_white]ENTER[/] Rebind  •  [bold bright_white]ESC[/] Back[/dim]\n"
                "[dim](Arrow keys, SPACE & ESC are always available)[/dim]"
            )

        content = Group(
            Align.center(title),
            table,
            Align.center(prompt),
        )

        panel = Panel(
            content,
            box=DOUBLE,
            width=64,
            border_style=theme.border_style,
            padding=(1, 2),
            title="[bold cyan]KEYBOARD CONTROLS[/bold cyan]",
            title_align="center",
        )
        return Align.center(panel)

    def render_about_creator(self, terminal_name: Optional[str] = None) -> Align:
        theme = self.theme
        title = Text("A B O U T   T H E   C R E A T O R\n", style="bold bright_green")

        card = Table.grid(padding=(0, 2))
        card.add_column(justify="right", style="bold cyan")
        card.add_column(justify="left", style="white")

        card.add_row("Author:", "Made with ❤️ by [bold bright_yellow]ItsReZNuM[/]")
        card.add_row("GitHub:", "github.com/ItsReZNuM")
        card.add_row("Repository:", "github.com/ItsReZNuM/SnakeGame-CLI")
        card.add_row("Telegram:", "t.me/ItsReZNuM")
        card.add_row("Instagram:", "instagram.com/rez.num")
        if terminal_name:
            card.add_row("Terminal:", f"[dim]{terminal_name}[/dim]")

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
            width=64,
            border_style=theme.border_style,
            padding=(1, 3),
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
        title_style = "bold bright_red" if not self.config.no_color else "bold white"
        border_style = "red" if not self.config.no_color else "white"

        banner = Panel(
            Align.center(Text("G A M E   O V E R", style=title_style)),
            box=DOUBLE,
            border_style="bold red" if not self.config.no_color else "white",
            width=46,
            padding=(0, 1),
        )

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
            width=64,
            border_style=border_style,
            padding=(1, 3),
            title="[bold red]GAME OVER[/bold red]" if not self.config.no_color else "GAME OVER",
            title_align="center",
        )
        return Align.center(panel)
