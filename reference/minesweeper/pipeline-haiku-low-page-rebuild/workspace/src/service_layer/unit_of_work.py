"""
Unit of Work Layer: Manages atomic transactional boundaries and repositories.
"""

from abc import ABC, abstractmethod
from src.adapters import repository

class AbstractUnitOfWork(ABC):
    games: repository.AbstractGameRepository
    difficulty_settings: repository.AbstractDifficultySettingRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.games = repository.FakeGameRepository()
        self.difficulty_settings = repository.FakeDifficultySettingRepository()
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass
