import json
from pathlib import Path

from sofafut.infrastructure.settings import PROJECT_ROOT


class FavoritesService:
    def __init__(self, favorites_path: Path | None = None) -> None:
        self.favorites_path = favorites_path or PROJECT_ROOT / "data" / "favorites.json"

    def get_favorites(self, username: str) -> set[str]:
        data = self._read()
        return set(data.get(username, []))

    def save_favorites(self, username: str, teams: set[str]) -> None:
        data = self._read()
        data[username] = sorted(teams)
        self.favorites_path.parent.mkdir(parents=True, exist_ok=True)
        self.favorites_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _read(self) -> dict[str, list[str]]:
        if not self.favorites_path.exists():
            return {}
        return json.loads(self.favorites_path.read_text(encoding="utf-8"))
