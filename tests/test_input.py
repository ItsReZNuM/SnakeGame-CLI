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
