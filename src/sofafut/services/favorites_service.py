import json
from pathlib import Path

from sofafut.infrastructure.settings import PROJECT_ROOT


class FavoritesService:
    def __init__(self, favorites_path: Path | None = None) -> None:
        self.favorites_path = favorites_path or PROJECT_ROOT / "data" / "favorites.json"

    def get_favorites(self, username: str) -> set[str]:
        return self.get_favorites_by_type(username, "clube")

    def get_favorites_by_type(self, username: str, entity_type: str) -> set[str]:
        data = self._read()
        user_data = data.get(username, [])
        if isinstance(user_data, list):
            return set(user_data) if entity_type == "clube" else set()
        return set(user_data.get(entity_type, []))

    def save_favorites(self, username: str, teams: set[str]) -> None:
        self.save_favorites_by_type(username, "clube", teams)

    def save_favorites_by_type(self, username: str, entity_type: str, entities: set[str]) -> None:
        data = self._read()
        user_data = data.get(username, {})
        if isinstance(user_data, list):
            user_data = {"clube": user_data}
        user_data[entity_type] = sorted(entities)
        data[username] = user_data
        self.favorites_path.parent.mkdir(parents=True, exist_ok=True)
        self.favorites_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_favorite(self, username: str, entity_type: str, entity_id: str) -> set[str]:
        favorites = self.get_favorites_by_type(username, entity_type)
        favorites.add(entity_id)
        self.save_favorites_by_type(username, entity_type, favorites)
        return favorites

    def remove_favorite(self, username: str, entity_type: str, entity_id: str) -> set[str]:
        favorites = self.get_favorites_by_type(username, entity_type)
        favorites.discard(entity_id)
        self.save_favorites_by_type(username, entity_type, favorites)
        return favorites

    def rename_user(self, old_username: str, new_username: str) -> None:
        if old_username == new_username:
            return
        data = self._read()
        if old_username not in data:
            return
        user_data = data.pop(old_username)
        if new_username in data:
            target_data = data[new_username]
            if isinstance(target_data, list):
                target_data = {"clube": target_data}
            if isinstance(user_data, list):
                user_data = {"clube": user_data}
            for entity_type, values in user_data.items():
                existing = set(target_data.get(entity_type, []))
                existing.update(values)
                target_data[entity_type] = sorted(existing)
            data[new_username] = target_data
        else:
            data[new_username] = user_data
        self.favorites_path.parent.mkdir(parents=True, exist_ok=True)
        self.favorites_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _read(self) -> dict[str, object]:
        if not self.favorites_path.exists():
            return {}
        return json.loads(self.favorites_path.read_text(encoding="utf-8"))
