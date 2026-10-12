"""
Repository Layer: Abstract and In-Memory Fake Repositories for DDD entities.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from src.domain.game import Game
from src.domain.difficulty import Difficulty
from src.domain.best_time import BestTime

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


class AbstractDifficultyRepository(ABC):
    @abstractmethod
    def add(self, item: Difficulty) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: str) -> Optional[Difficulty]:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[Difficulty]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, item_id: str) -> None:
        raise NotImplementedError


class AbstractBestTimeRepository(ABC):
    @abstractmethod
    def add(self, item: BestTime) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: str) -> Optional[BestTime]:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[BestTime]:
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


class FakeDifficultyRepository(AbstractDifficultyRepository):
    def __init__(self, items: Optional[List[Difficulty]] = None):
        self._items: Dict[str, Difficulty] = {getattr(i, 'id', str(idx)): i for idx, i in enumerate(items or [])}

    def add(self, item: Difficulty) -> None:
        self._items[str(getattr(item, 'id', ''))] = item

    def get(self, item_id: str) -> Optional[Difficulty]:
        return self._items.get(str(item_id))

    def list(self) -> List[Difficulty]:
        return list(self._items.values())

    def delete(self, item_id: str) -> None:
        self._items.pop(str(item_id), None)


class FakeBestTimeRepository(AbstractBestTimeRepository):
    def __init__(self, items: Optional[List[BestTime]] = None):
        self._items: Dict[str, BestTime] = {getattr(i, 'id', str(idx)): i for idx, i in enumerate(items or [])}

    def add(self, item: BestTime) -> None:
        self._items[str(getattr(item, 'id', ''))] = item

    def get(self, item_id: str) -> Optional[BestTime]:
        return self._items.get(str(item_id))

    def list(self) -> List[BestTime]:
        return list(self._items.values())

    def delete(self, item_id: str) -> None:
        self._items.pop(str(item_id), None)

