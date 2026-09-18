import time
from enum import Enum, auto
from typing import Optional

from rich.console import Console
from rich.live import Live

from snakegame.board import Board, Point
from snakegame.config import GameConfig
from snakegame.food import Food, SuperFood
from snakegame.input import Action, InputHandler
from snakegame.snake import Direction, Snake
from snakegame.storage import ScoreStorage
from snakegame.terminal import TerminalDetector, TerminalInfo
from snakegame.theme import THEME_NAMES, get_theme
from snakegame.ui import GameRenderer


class GameState(Enum):
    MAIN_MENU = auto()
    SETTINGS = auto()
    KEYBINDINGS = auto()
    ABOUT = auto()
    PLAYING = auto()
    PAUSED = auto()
    DYING = auto()
    GAME_OVER = auto()
    EXIT = auto()


GameState.START_SCREEN = GameState.MAIN_MENU  # type: ignore


class Game:
    def __init__(self, config: GameConfig, console: Optional[Console] = None) -> None:
        self.config = config
        self.console = console or Console(no_color=config.no_color)
        self.storage = ScoreStorage(config.storage_path)
        self.renderer = GameRenderer(config, self.console)
        self.input_handler = InputHandler(config.keybindings)

        self.board = Board(width=config.width, height=config.height)
        self.high_score = self.storage.load_high_score()

        self.terminal_info: TerminalInfo = TerminalDetector.detect()
        self._needs_render: bool = True
        self._last_term_size = None
        self._last_render_time: float = 0.0

        self.state = GameState.MAIN_MENU
        self.main_menu_index = 0
        self.settings_index = 0
        self.keybindings_index = 0
        self.binding_target: Optional[str] = None
        self.death_flash: bool = False
        self._death_start_time: float = 0.0

        self.score = 0
        self.regular_foods_eaten = 0
        self.super_foods_eaten = 0
        self.snake: Snake = self._create_initial_snake()
        self.food: Optional[Food] = None
        self.super_food: Optional[SuperFood] = None
        self.is_new_high = False

        self.elapsed_time = 0.0
        self._last_resume_time = 0.0
        self._last_tick_time = 0.0
        self._pause_start_time = 0.0

    def _create_initial_snake(self) -> Snake:
        start_x = max(3, self.board.width // 2)
        start_y = self.board.height // 2
        return Snake(initial_head=Point(start_x, start_y), initial_length=3, direction=Direction.RIGHT)

    def _reset_game(self) -> None:
        self.board = Board(width=self.config.width, height=self.config.height)
        self.score = 0
        self.regular_foods_eaten = 0
        self.super_foods_eaten = 0
        self.elapsed_time = 0.0
        self.is_new_high = False
        self.high_score = self.storage.load_high_score()
        self.snake = self._create_initial_snake()
        self.food = Food.spawn(self.board, self.snake.body_set, points=self.config.points_per_food)
        self.super_food = None
        self.state = GameState.PLAYING
        self._needs_render = True
        now = time.perf_counter()
        self._last_resume_time = now
        self._last_tick_time = now

    @property
    def current_speed(self) -> float:
        food_eaten = max(self.regular_foods_eaten, self.score // max(1, self.config.points_per_food))
        speed = self.config.initial_speed + (food_eaten * self.config.speed_increment)
        return min(self.config.max_speed, speed)

    def run(self) -> None:
        self.input_handler.enter()
        try:
            with Live(
                self.renderer.render_main_menu(
                    self.main_menu_index,
                    self.high_score,
                    terminal_name=self.terminal_info.name,
                ),
                console=self.console,
                screen=True,
                auto_refresh=False,
            ) as live:
                self._last_term_size = self.console.size
                self._last_render_time = time.perf_counter()
                self._needs_render = False

                while self.state != GameState.EXIT:
                    self._handle_input()
                    self._update()

                    # Dynamic terminal resize detection
                    current_size = self.console.size
                    if self._last_term_size != current_size:
                        self._last_term_size = current_size
                        self._needs_render = True

                    if self._needs_render:
                        self._render(live)
                        self._needs_render = False
                        self._last_render_time = time.perf_counter()

                    time.sleep(0.015)
        except KeyboardInterrupt:
            pass
        finally:
            self.input_handler.exit()
            self.console.show_cursor(True)

    def _handle_input(self) -> None:
        if self.state == GameState.KEYBINDINGS and self.binding_target is not None:
            raw_key = self.input_handler.get_raw_key()
            if raw_key is not None:
                self._needs_render = True
                if raw_key == "esc":
                    self.binding_target = None
                else:
                    val = " " if raw_key == "space" else raw_key
                    self.config.keybindings[self.binding_target] = val
                    self.input_handler.set_keybindings(self.config.keybindings)
                    self.config.save_settings()
                    self.binding_target = None
            return

        action = self.input_handler.get_action()
        if action is None:
            return

        self._needs_render = True

        if self.state == GameState.MAIN_MENU:
            if action == Action.UP:
                self.main_menu_index = (self.main_menu_index - 1) % 4
            elif action == Action.DOWN:
                self.main_menu_index = (self.main_menu_index + 1) % 4
            elif action == Action.SELECT:
                if self.main_menu_index == 0:
                    self._reset_game()
                elif self.main_menu_index == 1:
                    self.settings_index = 0
                    self.state = GameState.SETTINGS
                elif self.main_menu_index == 2:
                    self.state = GameState.ABOUT
                elif self.main_menu_index == 3:
                    self.state = GameState.EXIT
            elif action == Action.QUIT:
                self.state = GameState.EXIT

        elif self.state == GameState.SETTINGS:
            self._handle_settings_input(action)

        elif self.state == GameState.KEYBINDINGS:
            self._handle_keybindings_input(action)

        elif self.state == GameState.ABOUT:
            if action in (Action.BACK, Action.SELECT, Action.MENU, Action.QUIT):
                self.state = GameState.MAIN_MENU

        elif self.state == GameState.PLAYING:
            if action == Action.UP:
                self.snake.change_direction(Direction.UP)
            elif action == Action.DOWN:
                self.snake.change_direction(Direction.DOWN)
            elif action == Action.LEFT:
                self.snake.change_direction(Direction.LEFT)
            elif action == Action.RIGHT:
                self.snake.change_direction(Direction.RIGHT)
            elif action in (Action.PAUSE, Action.SELECT, Action.BACK):
                self.elapsed_time += time.perf_counter() - self._last_resume_time
                self._pause_start_time = time.perf_counter()
                self.state = GameState.PAUSED
            elif action == Action.QUIT:
                self.state = GameState.MAIN_MENU

        elif self.state == GameState.PAUSED:
            if action in (Action.PAUSE, Action.SELECT, Action.BACK, Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT):
                pause_duration = time.perf_counter() - self._pause_start_time
                if self.super_food is not None:
                    self.super_food.spawn_time += pause_duration
                now = time.perf_counter()
                self._last_resume_time = now
                self._last_tick_time = now
                self.state = GameState.PLAYING
            elif action in (Action.QUIT, Action.MENU):
                self.state = GameState.MAIN_MENU

        elif self.state == GameState.DYING:
            if action in (Action.SELECT, Action.BACK, Action.RESTART, Action.MENU):
                self._trigger_game_over()

        elif self.state == GameState.GAME_OVER:
            if action in (Action.RESTART, Action.SELECT):
                self._reset_game()
            elif action in (Action.MENU, Action.BACK):
                self.state = GameState.MAIN_MENU
            elif action == Action.QUIT:
                self.state = GameState.EXIT

    def _handle_settings_input(self, action: Action) -> None:
        if action == Action.UP:
            self.settings_index = (self.settings_index - 1) % 7
        elif action == Action.DOWN:
            self.settings_index = (self.settings_index + 1) % 7
        elif action == Action.LEFT:
            if self.settings_index == 0:
                self.config.width = max(10, self.config.width - 2)
            elif self.settings_index == 1:
                self.config.height = max(8, self.config.height - 1)
            elif self.settings_index == 2:
                idx = THEME_NAMES.index(self.config.theme_name) if self.config.theme_name in THEME_NAMES else 0
                self.config.theme_name = THEME_NAMES[(idx - 1) % len(THEME_NAMES)]
                self.renderer.theme = get_theme(self.config.theme_name)
            elif self.settings_index == 3:
                self.config.initial_speed = max(1.0, round(self.config.initial_speed - 0.5, 1))
            elif self.settings_index == 4:
                self.config.super_food_enabled = not self.config.super_food_enabled
        elif action == Action.RIGHT:
            if self.settings_index == 0:
                self.config.width = min(60, self.config.width + 2)
            elif self.settings_index == 1:
                self.config.height = min(35, self.config.height + 1)
            elif self.settings_index == 2:
                idx = THEME_NAMES.index(self.config.theme_name) if self.config.theme_name in THEME_NAMES else 0
                self.config.theme_name = THEME_NAMES[(idx + 1) % len(THEME_NAMES)]
                self.renderer.theme = get_theme(self.config.theme_name)
            elif self.settings_index == 3:
                self.config.initial_speed = min(25.0, round(self.config.initial_speed + 0.5, 1))
            elif self.settings_index == 4:
                self.config.super_food_enabled = not self.config.super_food_enabled
            elif self.settings_index == 5:
                self.keybindings_index = 0
                self.binding_target = None
                self.state = GameState.KEYBINDINGS
        elif action == Action.SELECT:
            if self.settings_index == 4:
                self.config.super_food_enabled = not self.config.super_food_enabled
            elif self.settings_index == 5:
                self.keybindings_index = 0
                self.binding_target = None
                self.state = GameState.KEYBINDINGS
            elif self.settings_index == 6:
                self.config.save_settings()
                self.board = Board(self.config.width, self.config.height)
                self.state = GameState.MAIN_MENU
        elif action == Action.BACK:
            self.config.save_settings()
            self.board = Board(self.config.width, self.config.height)
            self.state = GameState.MAIN_MENU

    def _handle_keybindings_input(self, action: Action) -> None:
        action_keys = ["up", "down", "left", "right", "pause"]
        if action == Action.UP:
            self.keybindings_index = (self.keybindings_index - 1) % 7
        elif action == Action.DOWN:
            self.keybindings_index = (self.keybindings_index + 1) % 7
        elif action == Action.SELECT:
            if self.keybindings_index < len(action_keys):
                self.binding_target = action_keys[self.keybindings_index]
            elif self.keybindings_index == 5:
                self.config.keybindings = dict(InputHandler.DEFAULT_KEYBINDINGS)
                self.input_handler.set_keybindings(self.config.keybindings)
                self.config.save_settings()
            elif self.keybindings_index == 6:
                self.state = GameState.SETTINGS
        elif action in (Action.BACK, Action.MENU):
            self.state = GameState.SETTINGS

    def _start_death_animation(self) -> None:
        self.elapsed_time += time.perf_counter() - self._last_resume_time
        self.state = GameState.DYING
        self._death_start_time = time.perf_counter()
        self.death_flash = True
        self._needs_render = True

    def _update(self) -> None:
        now = time.perf_counter()

        if self.state == GameState.DYING:
            elapsed = now - self._death_start_time
            # 3 cycles of 0.15s ON / 0.15s OFF = 0.9s
            blink_phase = int(elapsed / 0.15)
            flash = (blink_phase % 2 == 0)
            if flash != self.death_flash:
                self.death_flash = flash
                self._needs_render = True
            if elapsed >= 0.9:
                self._trigger_game_over()
            return

        if self.state != GameState.PLAYING:
            return

        # Check SuperFood expiration
        if self.super_food is not None and self.super_food.is_expired(now):
            self.super_food = None
            self._needs_render = True

        # Throttle live clock/countdown rendering based on terminal recommended FPS
        min_render_interval = 1.0 / self.terminal_info.recommended_fps
        if now - self._last_render_time >= min_render_interval:
            self._needs_render = True

        tick_interval = 1.0 / self.current_speed
        if now - self._last_tick_time < tick_interval:
            return

        self._last_tick_time = now
        next_head = self.snake.peek_next_head(self.board.width, self.board.height)

        eating_regular = self.food is not None and next_head == self.food.position
        eating_super = self.super_food is not None and next_head == self.super_food.position

        if eating_regular:
            self.score += self.food.points
            self.regular_foods_eaten += 1
            self.snake.grow(1)
            if self.score > self.high_score:
                self.high_score = self.score
                self.is_new_high = True
                self.storage.save_high_score(self.high_score)

        elif eating_super:
            self.score += self.super_food.points
            self.super_foods_eaten += 1
            self.snake.grow(self.super_food.growth)
            self.super_food = None
            if self.score > self.high_score:
                self.high_score = self.score
                self.is_new_high = True
                self.storage.save_high_score(self.high_score)

        new_head = self.snake.step(self.board.width, self.board.height)
        self._needs_render = True

        # Self collision check
        if self.snake.collides_with_self():
            self._start_death_animation()
            return

        # Handle post-step food spawn
        if eating_regular:
            occupied = self.snake.body_set
            if self.super_food is not None:
                occupied = occupied | {self.super_food.position}
            self.food = Food.spawn(self.board, occupied, points=self.config.points_per_food)

            # Spawn SuperFood every 5 foods if enabled and none currently active
            if (
                self.config.super_food_enabled
                and self.regular_foods_eaten > 0
                and self.regular_foods_eaten % self.config.super_food_interval == 0
                and self.super_food is None
            ):
                occupied_all = self.snake.body_set
                if self.food is not None:
                    occupied_all = occupied_all | {self.food.position}
                self.super_food = SuperFood.spawn(
                    board=self.board,
                    occupied=occupied_all,
                    spawn_time=time.perf_counter(),
                    duration=self.config.super_food_duration,
                    points=self.config.super_food_points,
                    growth=self.config.super_food_growth,
                )

            if self.food is None:
                self._start_death_animation()

    def _trigger_game_over(self) -> None:
        if self.state != GameState.DYING:
            self.elapsed_time += time.perf_counter() - self._last_resume_time
        if self.score > 0 and self.storage.save_high_score(self.score):
            self.is_new_high = True
            self.high_score = max(self.high_score, self.score)
        self.state = GameState.GAME_OVER
        self._needs_render = True

    def _current_play_time(self) -> float:
        if self.state == GameState.PLAYING:
            return self.elapsed_time + (time.perf_counter() - self._last_resume_time)
        return self.elapsed_time

    def _render(self, live: Live) -> None:
        if self.state == GameState.MAIN_MENU:
            live.update(
                self.renderer.render_main_menu(
                    self.main_menu_index,
                    self.high_score,
                    terminal_name=self.terminal_info.name,
                ),
                refresh=True,
            )

        elif self.state == GameState.SETTINGS:
            term_size = self.console.size
            live.update(
                self.renderer.render_settings_menu(
                    config=self.config,
                    selected_index=self.settings_index,
                    term_width=term_size.width,
                    term_height=term_size.height,
                    terminal_name=self.terminal_info.name,
                ),
                refresh=True,
            )

        elif self.state == GameState.KEYBINDINGS:
            live.update(
                self.renderer.render_keybindings_menu(
                    config=self.config,
                    selected_index=self.keybindings_index,
                    binding_target=self.binding_target,
                ),
                refresh=True,
            )

        elif self.state == GameState.ABOUT:
            live.update(
                self.renderer.render_about_creator(
                    terminal_name=self.terminal_info.name,
                ),
                refresh=True,
            )

        elif self.state in (GameState.PLAYING, GameState.PAUSED, GameState.DYING):
            play_time = self._current_play_time()
            live.update(
                self.renderer.render_game_view(
                    board=self.board,
                    snake=self.snake,
                    food=self.food,
                    score=self.score,
                    high_score=self.high_score,
                    elapsed_time=play_time,
                    speed=self.current_speed,
                    regular_foods_eaten=self.regular_foods_eaten,
                    super_food=self.super_food,
                    current_time=time.perf_counter(),
                    is_paused=(self.state == GameState.PAUSED),
                    is_dying=(self.state == GameState.DYING),
                    death_flash=self.death_flash,
                ),
                refresh=True,
            )

        elif self.state == GameState.GAME_OVER:
            live.update(
                self.renderer.render_game_over_screen(
                    score=self.score,
                    high_score=self.high_score,
                    elapsed_time=self.elapsed_time,
                    snake_length=self.snake.length,
                    is_new_high=self.is_new_high,
                    super_foods_eaten=self.super_foods_eaten,
                ),
                refresh=True,
            )
