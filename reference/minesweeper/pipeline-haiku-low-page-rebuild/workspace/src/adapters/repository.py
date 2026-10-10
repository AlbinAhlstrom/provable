"""
Repository Layer: Abstract and In-Memory Fake Repositories for DDD entities.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from src.domain.game import Game
from src.domain.difficulty_setting import DifficultySetting

class AbstractGameRepository(ABC):
    @abstractmethod
    def add(self, item: Game) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: str) -> Optional[Game]:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[Game]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, item_id: str) -> None:
        raise NotImplementedError


class AbstractDifficultySettingRepository(ABC):
    @abstractmethod
    def add(self, item: DifficultySetting) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: str) -> Optional[DifficultySetting]:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[DifficultySetting]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, item_id: str) -> None:
        raise NotImplementedError


class FakeGameRepository(AbstractGameRepository):
    def __init__(self, items: Optional[List[Game]] = None):
        self._items: Dict[str, Game] = {getattr(i, 'id', str(idx)): i for idx, i in enumerate(items or [])}

    def add(self, item: Game) -> None:
        self._items[str(getattr(item, 'id', ''))] = item

    def get(self, item_id: str) -> Optional[Game]:
        return self._items.get(str(item_id))

    def list(self) -> List[Game]:
        return list(self._items.values())

    def delete(self, item_id: str) -> None:
        self._items.pop(str(item_id), None)


class FakeDifficultySettingRepository(AbstractDifficultySettingRepository):
    def __init__(self, items: Optional[List[DifficultySetting]] = None):
        self._items: Dict[str, DifficultySetting] = {getattr(i, 'id', str(idx)): i for idx, i in enumerate(items or [])}

    def add(self, item: DifficultySetting) -> None:
        self._items[str(getattr(item, 'id', ''))] = item

    def get(self, item_id: str) -> Optional[DifficultySetting]:
        return self._items.get(str(item_id))

    def list(self) -> List[DifficultySetting]:
        return list(self._items.values())

    def delete(self, item_id: str) -> None:
        self._items.pop(str(item_id), None)

