import pytest
from snakegame.config import ConfigError, GameConfig


def test_default_config():
    config = GameConfig()
    config.validate()
    assert config.width == 24
    assert config.height == 16
    assert config.initial_speed == 6.0
    assert config.points_per_food == 10
    assert config.no_color is False


def test_valid_custom_config():
    config = GameConfig(
        width=30,
        height=20,
        initial_speed=10.0,
        speed_increment=0.5,
        max_speed=25.0,
        no_color=True,
    )
    config.validate()
    assert config.width == 30
    assert config.height == 20
    assert config.initial_speed == 10.0
    assert config.no_color is True


def test_invalid_width():
    with pytest.raises(ConfigError, match="Board width"):
        GameConfig(width=5).validate()

    with pytest.raises(ConfigError, match="Board width"):
        GameConfig(width=100).validate()


def test_invalid_height():
    with pytest.raises(ConfigError, match="Board height"):
        GameConfig(height=4).validate()

    with pytest.raises(ConfigError, match="Board height"):
        GameConfig(height=50).validate()


def test_invalid_speed():
    with pytest.raises(ConfigError, match="Initial speed"):
        GameConfig(initial_speed=0.5).validate()

    with pytest.raises(ConfigError, match="Initial speed"):
        GameConfig(initial_speed=30.0).validate()


def test_invalid_speed_increment():
    with pytest.raises(ConfigError, match="Speed increment"):
        GameConfig(speed_increment=-0.1).validate()


def test_max_speed_less_than_initial():
    with pytest.raises(ConfigError, match="Maximum speed"):
        GameConfig(initial_speed=12.0, max_speed=10.0).validate()
