import json
from pathlib import Path
from typing import Optional


class ScoreStorage:
    def __init__(self, storage_path: Optional[Path] = None) -> None:
        if storage_path is not None:
            self.path = Path(storage_path)
        else:
            self.path = Path.home() / ".snakegame" / "scores.json"

    def load_high_score(self) -> int:
        if not self.path.exists():
            return 0

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("high_score", 0))
        except (json.JSONDecodeError, OSError, ValueError, TypeError):
            return 0

    def save_high_score(self, score: int) -> bool:
        current_best = self.load_high_score()
        if score <= current_best:
            return False

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"high_score": score}, f, indent=2)
            return True
        except OSError:
            return False
