from snakegame.config import GameConfig


def test_settings_save_and_load(tmp_path):
    settings_file = tmp_path / "settings.json"
    config1 = GameConfig(
        width=30,
        height=20,
        initial_speed=9.0,
        theme_name="Cyberpunk Neon",
        super_food_enabled=False,
        settings_path=settings_file,
    )

    assert config1.save_settings() is True
    assert settings_file.exists()

    config2 = GameConfig(settings_path=settings_file)
    config2.load_saved_settings()

    assert config2.width == 30
    assert config2.height == 20
    assert config2.initial_speed == 9.0
    assert config2.theme_name == "Cyberpunk Neon"
    assert config2.super_food_enabled is False
