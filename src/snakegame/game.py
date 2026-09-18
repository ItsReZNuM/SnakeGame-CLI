import time
from enum import Enum, auto
from typing import Optional

from rich.console import Console
from rich.live import Live

from snakegame.board import Board, Point
from snakegame.config import GameConfig
from snakegame.food import Food
from snakegame.input import Action, InputHandler
from snakegame.snake import Direction, Snake
from snakegame.storage import ScoreStorage
from snakegame.ui import GameRenderer


class GameState(Enum):
    START_SCREEN = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    EXIT = auto()


class Game:
    def __init__(self, config: GameConfig, console: Optional[Console] = None) -> None:
        self.config = config
        self.console = console or Console(no_color=config.no_color)
        self.storage = ScoreStorage(config.storage_path)
        self.renderer = GameRenderer(config, self.console)
        self.input_handler = InputHandler()

        self.board = Board(width=config.width, height=config.height)
        self.high_score = self.storage.load_high_score()

        self.state = GameState.START_SCREEN
        self.score = 0
        self.snake: Snake = self._create_initial_snake()
        self.food: Optional[Food] = None
        self.is_new_high = False

        self.elapsed_time = 0.0
        self._last_resume_time = 0.0
        self._last_tick_time = 0.0

    def _create_initial_snake(self) -> Snake:
        start_x = max(3, self.board.width // 2)
        start_y = self.board.height // 2
        return Snake(initial_head=Point(start_x, start_y), initial_length=3, direction=Direction.RIGHT)

    def _reset_game(self) -> None:
        self.score = 0
        self.elapsed_time = 0.0
        self.is_new_high = False
        self.high_score = self.storage.load_high_score()
        self.snake = self._create_initial_snake()
        self.food = Food.spawn(self.board, self.snake.body_set, points=self.config.points_per_food)
        self.state = GameState.PLAYING
        now = time.perf_counter()
        self._last_resume_time = now
        self._last_tick_time = now

    @property
    def current_speed(self) -> float:
        food_eaten = self.score // max(1, self.config.points_per_food)
        speed = self.config.initial_speed + (food_eaten * self.config.speed_increment)
        return min(self.config.max_speed, speed)

    def run(self) -> None:
        self.input_handler.enter()
        try:
            with Live(
                self.renderer.render_start_screen(self.high_score),
                console=self.console,
                screen=True,
                auto_refresh=False,
            ) as live:
                while self.state != GameState.EXIT:
                    self._handle_input()
                    self._update()
                    self._render(live)
                    time.sleep(0.015)
        except KeyboardInterrupt:
            pass
        finally:
            self.input_handler.exit()
            self.console.show_cursor(True)

    def _handle_input(self) -> None:
        action = self.input_handler.get_action()
        if action is None:
            return

        if action == Action.QUIT:
            self.state = GameState.EXIT
            return

        if self.state == GameState.START_SCREEN:
            if action in (Action.START, Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT):
                self._reset_game()

        elif self.state == GameState.PLAYING:
            if action == Action.UP:
                self.snake.change_direction(Direction.UP)
            elif action == Action.DOWN:
                self.snake.change_direction(Direction.DOWN)
            elif action == Action.LEFT:
                self.snake.change_direction(Direction.LEFT)
            elif action == Action.RIGHT:
                self.snake.change_direction(Direction.RIGHT)
            elif action in (Action.PAUSE, Action.START):
                # Pause the game and record accumulated time
                self.elapsed_time += time.perf_counter() - self._last_resume_time
                self.state = GameState.PAUSED

        elif self.state == GameState.PAUSED:
            if action in (Action.PAUSE, Action.START, Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT):
                # Resume the game and reset resume baseline
                self._last_resume_time = time.perf_counter()
                self._last_tick_time = time.perf_counter()
                self.state = GameState.PLAYING

        elif self.state == GameState.GAME_OVER:
            if action == Action.RESTART or action == Action.START:
                self._reset_game()

    def _update(self) -> None:
        if self.state != GameState.PLAYING:
            return

        now = time.perf_counter()
        tick_interval = 1.0 / self.current_speed

        if now - self._last_tick_time < tick_interval:
            return

        self._last_tick_time = now
        next_head = self.snake.peek_next_head()
        eating_food = self.food is not None and next_head == self.food.position

        if eating_food:
            self.score += self.food.points
            self.snake.grow(1)
            if self.score > self.high_score:
                self.high_score = self.score
                self.is_new_high = True
                self.storage.save_high_score(self.high_score)

        new_head = self.snake.step()

        # Wall collision check
        if not self.board.is_in_bounds(new_head):
            self._trigger_game_over()
            return

        # Self collision check
        if self.snake.collides_with_self():
            self._trigger_game_over()
            return

        if eating_food:
            self.food = Food.spawn(self.board, self.snake.body_set, points=self.config.points_per_food)
            if self.food is None:
                # Board completely filled - game won!
                self._trigger_game_over()

    def _trigger_game_over(self) -> None:
        self.elapsed_time += time.perf_counter() - self._last_resume_time
        if self.score > 0 and self.storage.save_high_score(self.score):
            self.is_new_high = True
            self.high_score = max(self.high_score, self.score)
        self.state = GameState.GAME_OVER

    def _current_play_time(self) -> float:
        if self.state == GameState.PLAYING:
            return self.elapsed_time + (time.perf_counter() - self._last_resume_time)
        return self.elapsed_time

    def _render(self, live: Live) -> None:
        if self.state == GameState.START_SCREEN:
            live.update(self.renderer.render_start_screen(self.high_score), refresh=True)
        elif self.state in (GameState.PLAYING, GameState.PAUSED):
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
                    is_paused=(self.state == GameState.PAUSED),
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
                ),
                refresh=True,
            )
