import json
import pytest
from snakegame.storage import ScoreStorage


def test_storage_non_existent_file(tmp_path):
    storage_file = tmp_path / "scores.json"
    storage = ScoreStorage(storage_path=storage_file)
    assert storage.load_high_score() == 0


def test_storage_save_and_load(tmp_path):
    storage_file = tmp_path / "sub" / "scores.json"
    storage = ScoreStorage(storage_path=storage_file)

    assert storage.save_high_score(50) is True
    assert storage.load_high_score() == 50

    # Lower score does not overwrite higher score
    assert storage.save_high_score(30) is False
    assert storage.load_high_score() == 50

    # Higher score updates successfully
    assert storage.save_high_score(120) is True
    assert storage.load_high_score() == 120


def test_storage_handles_corrupted_json(tmp_path):
    storage_file = tmp_path / "corrupt.json"
    storage_file.write_text("{invalid_json_syntax", encoding="utf-8")

    storage = ScoreStorage(storage_path=storage_file)
    assert storage.load_high_score() == 0
