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
    SELECT = auto()
    START = SELECT
    BACK = auto()
    PAUSE = auto()
    RESTART = auto()
    MENU = auto()
    QUIT = auto()


class InputHandler:
    DEFAULT_KEYBINDINGS: dict[str, str] = {
        "up": "w",
        "down": "s",
        "left": "a",
        "right": "d",
        "pause": "p",
    }

    PERSIAN_TO_ENGLISH: dict[str, str] = {
        "ض": "q",
        "ص": "w",
        "ث": "e",
        "ق": "r",
        "ف": "t",
        "غ": "y",
        "ع": "u",
        "ه": "i",
        "خ": "o",
        "ح": "p",
        "ج": "[",
        "چ": "]",
        "ش": "a",
        "س": "s",
        "ی": "d",
        "ي": "d",
        "ب": "f",
        "ل": "g",
        "ا": "h",
        "آ": "h",
        "ت": "j",
        "ن": "k",
        "م": "l",
        "ک": ";",
        "ك": ";",
        "گ": "'",
        "ظ": "z",
        "ط": "x",
        "ز": "c",
        "ر": "v",
        "ذ": "b",
        "پ": "m",
        "ئ": "m",
        "د": "n",
        "و": ",",
    }

    def __init__(self, keybindings: Optional[dict[str, str]] = None) -> None:
        self._orig_termios = None
        self.keybindings: dict[str, str] = dict(self.DEFAULT_KEYBINDINGS)
        if keybindings:
            self.keybindings.update(keybindings)

    def set_keybindings(self, keybindings: dict[str, str]) -> None:
        self.keybindings.update(keybindings)

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

    def get_raw_key(self) -> Optional[str]:
        """Read a single raw key without action mapping (for key binding)."""
        if WINDOWS:
            if not msvcrt.kbhit():
                return None
            ch = msvcrt.getwch()
            if ch == "\x03":
                raise KeyboardInterrupt
            if ch in ("\x00", "\xe0"):
                msvcrt.getwch()
                return None
            if ch == "\x1b":
                return "esc"
            if ch in ("\r", "\n"):
                return "enter"
            if ch == " ":
                return "space"
            raw = ch.lower()
            return self.PERSIAN_TO_ENGLISH.get(raw, raw)
        else:
            if not sys.stdin.isatty():
                return None
            rlist, _, _ = select.select([sys.stdin], [], [], 0)
            if not rlist:
                return None
            ch = sys.stdin.read(1)
            if ch == "\x03":
                raise KeyboardInterrupt
            if ch == "\x1b":
                return "esc"
            if ch in ("\r", "\n"):
                return "enter"
            if ch == " ":
                return "space"
            raw = ch.lower()
            return self.PERSIAN_TO_ENGLISH.get(raw, raw)

    def _get_action_windows(self) -> Optional[Action]:
        if not msvcrt.kbhit():
            return None

        ch = msvcrt.getwch()

        # Handle Ctrl+C
        if ch == "\x03":
            raise KeyboardInterrupt

        # Extended key prefix for arrow keys (Standard CMD / PowerShell scan codes)
        if ch in ("\x00", "\xe0"):
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

        # Virtual Terminal / ANSI Escape Sequences (Windows Terminal)
        if ch == "\x1b":
            if msvcrt.kbhit():
                next_ch = msvcrt.getwch()
                if next_ch == "[":
                    if msvcrt.kbhit():
                        arrow = msvcrt.getwch()
                        if arrow == "A":
                            return Action.UP
                        elif arrow == "B":
                            return Action.DOWN
                        elif arrow == "D":
                            return Action.LEFT
                        elif arrow == "C":
                            return Action.RIGHT
            return Action.BACK

        return self._map_char_with_bindings(ch)

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
            return Action.BACK

        return self._map_char_with_bindings(ch)

    def map_char(self, ch: str) -> Optional[Action]:
        return self._map_char_with_bindings(ch)

    def _map_char_with_bindings(self, ch: str) -> Optional[Action]:
        return self._map_char_static(ch, self.keybindings)

    @classmethod
    def _map_char_static(cls, ch: str, keybindings: Optional[dict[str, str]] = None) -> Optional[Action]:
        bindings = keybindings or cls.DEFAULT_KEYBINDINGS
        low = ch.lower()
        norm = cls.PERSIAN_TO_ENGLISH.get(low, low)

        up_key = bindings.get("up", "w")
        down_key = bindings.get("down", "s")
        left_key = bindings.get("left", "a")
        right_key = bindings.get("right", "d")
        pause_key = bindings.get("pause", "p")

        if low == up_key or norm == up_key:
            return Action.UP
        elif low == down_key or norm == down_key:
            return Action.DOWN
        elif low == left_key or norm == left_key:
            return Action.LEFT
        elif low == right_key or norm == right_key:
            return Action.RIGHT
        elif low == pause_key or norm == pause_key:
            return Action.PAUSE
        elif low in (" ", "\r", "\n"):
            return Action.SELECT
        elif low in ("\x08", "b") or norm == "b":
            return Action.BACK
        elif low == "r" or norm == "r":
            return Action.RESTART
        elif low == "m" or norm == "m":
            return Action.MENU
        elif low == "q" or norm == "q":
            return Action.QUIT
        return None

    @classmethod
    def _map_char(cls, ch: str) -> Optional[Action]:
        return cls._map_char_static(ch)
