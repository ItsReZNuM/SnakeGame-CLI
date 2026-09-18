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
