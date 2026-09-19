from snakegame.input import Action, InputHandler


def test_input_char_mapping():
    assert InputHandler._map_char("w") == Action.UP
    assert InputHandler._map_char("W") == Action.UP
    assert InputHandler._map_char("s") == Action.DOWN
    assert InputHandler._map_char("S") == Action.DOWN
    assert InputHandler._map_char("a") == Action.LEFT
    assert InputHandler._map_char("A") == Action.LEFT
    assert InputHandler._map_char("d") == Action.RIGHT
    assert InputHandler._map_char("D") == Action.RIGHT
    assert InputHandler._map_char(" ") == Action.SELECT
    assert InputHandler._map_char("\r") == Action.SELECT
    assert InputHandler._map_char("\n") == Action.SELECT
    assert InputHandler._map_char("p") == Action.PAUSE
    assert InputHandler._map_char("r") == Action.RESTART
    assert InputHandler._map_char("m") == Action.MENU
    assert InputHandler._map_char("q") == Action.QUIT
    assert InputHandler._map_char("b") == Action.BACK
    assert InputHandler._map_char("\x08") == Action.BACK


def test_custom_keybindings():
    custom_keys = {"up": "i", "down": "k", "left": "j", "right": "l", "pause": "o"}
    handler = InputHandler(keybindings=custom_keys)

    assert handler.map_char("i") == Action.UP
    assert handler.map_char("I") == Action.UP
    assert handler.map_char("k") == Action.DOWN
    assert handler.map_char("j") == Action.LEFT
    assert handler.map_char("l") == Action.RIGHT
    assert handler.map_char("o") == Action.PAUSE

    # Default WASD should not trigger UP when remapped
    assert handler.map_char("w") is None


def test_persian_keyboard_mapping():
    # Persian keys corresponding to physical QWERTY positions
    assert InputHandler._map_char("ص") == Action.UP       # W
    assert InputHandler._map_char("س") == Action.DOWN     # S
    assert InputHandler._map_char("ش") == Action.LEFT     # A
    assert InputHandler._map_char("ی") == Action.RIGHT    # D (Persian Yeh)
    assert InputHandler._map_char("ي") == Action.RIGHT    # D (Arabic Yeh)
    assert InputHandler._map_char("ح") == Action.PAUSE    # P
    assert InputHandler._map_char("ق") == Action.RESTART  # R
    assert InputHandler._map_char("پ") == Action.MENU     # M
    assert InputHandler._map_char("ئ") == Action.MENU     # M (alternate)
    assert InputHandler._map_char("ض") == Action.QUIT     # Q
    assert InputHandler._map_char("ذ") == Action.BACK     # B

