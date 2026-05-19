from collections.abc import Callable, Iterable
from typing import TypeVar

from sofafut.models.base import Entity

T = TypeVar("T", bound=Entity)


class MemoryRepository:
    def __init__(self) -> None:
        self._items: dict[str, Entity] = {}

    def add(self, item: T) -> T:
        self._items[item.id] = item
        return item

    def get(self, item_id: str) -> Entity:
        try:
            return self._items[item_id]
        except KeyError as exc:
            raise ValueError(f"Item nao encontrado: {item_id}") from exc

    def list(self) -> list[Entity]:
        return list(self._items.values())

    def find_one(self, predicate: Callable[[Entity], bool]) -> Entity | None:
        return next((item for item in self._items.values() if predicate(item)), None)

    def find_all(self, predicate: Callable[[Entity], bool]) -> Iterable[Entity]:
        return (item for item in self._items.values() if predicate(item))
