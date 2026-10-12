"""
Repository Layer: Abstract and In-Memory Fake Repositories for DDD entities.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from src.domain.difficulty import Difficulty
from src.domain.game_session import GameSession

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


class AbstractGameSessionRepository(ABC):
    @abstractmethod
    def add(self, item: GameSession) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: str) -> Optional[GameSession]:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[GameSession]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, item_id: str) -> None:
        raise NotImplementedError


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


class FakeGameSessionRepository(AbstractGameSessionRepository):
    def __init__(self, items: Optional[List[GameSession]] = None):
        self._items: Dict[str, GameSession] = {getattr(i, 'id', str(idx)): i for idx, i in enumerate(items or [])}

    def add(self, item: GameSession) -> None:
        self._items[str(getattr(item, 'id', ''))] = item

    def get(self, item_id: str) -> Optional[GameSession]:
        return self._items.get(str(item_id))

    def list(self) -> List[GameSession]:
        return list(self._items.values())

    def delete(self, item_id: str) -> None:
        self._items.pop(str(item_id), None)

