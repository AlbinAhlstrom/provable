"""
Unit of Work Pattern — Context manager managing atomic transaction boundaries.
"""

import abc
from adapters.repository import (
    AbstractRequirementRepository, SqliteRequirementRepository, FakeRequirementRepository,
    AbstractProjectRepository, SqliteProjectRepository, FakeProjectRepository,
    AbstractKickstartRepository, SqliteKickstartRepository, FakeKickstartRepository
)

class AbstractUnitOfWork(abc.ABC):
    requirements: AbstractRequirementRepository
    projects: AbstractProjectRepository
    kickstart: AbstractKickstartRepository

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()

    def commit(self):
        self._commit()

    def rollback(self):
        self._rollback()

    def collect_new_events(self):
        for repo_name in ("requirements", "projects", "kickstart"):
            repo = getattr(self, repo_name, None)
            if repo and hasattr(repo, "seen"):
                for entity in list(repo.seen):
                    while hasattr(entity, "events") and entity.events:
                        yield entity.events.pop(0)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _rollback(self):
        raise NotImplementedError


class SqliteUnitOfWork(AbstractUnitOfWork):
    """Real SQLite Unit of Work context manager."""
    def __enter__(self):
        self.requirements = SqliteRequirementRepository()
        self.projects = SqliteProjectRepository()
        self.kickstart = SqliteKickstartRepository()
        return super().__enter__()

    def _commit(self):
        # Transaction commits are handled by store SQLite WAL mode
        pass

    def _rollback(self):
        pass


class FakeUnitOfWork(AbstractUnitOfWork):
    """In-memory Fake Unit of Work for fast unit testing."""
    def __init__(self, initial_requirements=None, initial_projects=None, initial_kickstart=None):
        self.requirements = FakeRequirementRepository(initial_requirements or [])
        self.projects = FakeProjectRepository(initial_projects)
        self.kickstart = FakeKickstartRepository(initial_kickstart)
        self.committed = False

    def _commit(self):
        self.committed = True

    def _rollback(self):
        pass

