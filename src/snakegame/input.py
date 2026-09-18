import sys
from enum import Enum, auto
from typing import Optional

try:
    import msvcrt
    WINDOWS = True
except ImportError:
    WINDOWS = False
    import select
    import termios
    import tty


class Action(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    PAUSE = auto()
    RESTART = auto()
    START = auto()
    QUIT = auto()


class InputHandler:
    def __init__(self) -> None:
        self._orig_termios = None

    def enter(self) -> None:
        if not WINDOWS and sys.stdin.isatty():
            try:
                self._orig_termios = termios.tcgetattr(sys.stdin.fileno())
                tty.setcbreak(sys.stdin.fileno())
            except Exception:
                self._orig_termios = None

    def exit(self) -> None:
        if not WINDOWS and self._orig_termios is not None and sys.stdin.isatty():
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._orig_termios)
            except Exception:
                pass
            self._orig_termios = None

    def get_action(self) -> Optional[Action]:
        if WINDOWS:
            return self._get_action_windows()
        return self._get_action_unix()

    def _get_action_windows(self) -> Optional[Action]:
        if not msvcrt.kbhit():
            return None

        ch = msvcrt.getwch()

        # Handle Ctrl+C
        if ch == "\x03":
            raise KeyboardInterrupt

        # Extended key prefix for arrow keys
        if ch in ("\x00", "\xe0"):
            if not msvcrt.kbhit():
                return None
            code = msvcrt.getwch()
            if code == "H":
                return Action.UP
            elif code == "P":
                return Action.DOWN
            elif code == "K":
                return Action.LEFT
            elif code == "M":
                return Action.RIGHT
            return None

        return self._map_char(ch)

    def _get_action_unix(self) -> Optional[Action]:
        if not sys.stdin.isatty():
            return None

        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if not rlist:
            return None

        ch = sys.stdin.read(1)
        if ch == "\x03":
            raise KeyboardInterrupt

        if ch == "\x1b":
            # Check if this is an ANSI escape sequence
            r2, _, _ = select.select([sys.stdin], [], [], 0.02)
            if r2:
                seq = sys.stdin.read(2)
                if seq == "[A":
                    return Action.UP
                elif seq == "[B":
                    return Action.DOWN
                elif seq == "[D":
                    return Action.LEFT
                elif seq == "[C":
                    return Action.RIGHT
            return Action.QUIT

        return self._map_char(ch)

    @staticmethod
    def _map_char(ch: str) -> Optional[Action]:
        low = ch.lower()
        if low == "w":
            return Action.UP
        elif low == "s":
            return Action.DOWN
        elif low == "a":
            return Action.LEFT
        elif low == "d":
            return Action.RIGHT
        elif low == "p":
            return Action.PAUSE
        elif low == "r":
            return Action.RESTART
        elif low in ("q", "\x1b"):
            return Action.QUIT
        elif low in (" ", "\r", "\n"):
            return Action.START
        return None
