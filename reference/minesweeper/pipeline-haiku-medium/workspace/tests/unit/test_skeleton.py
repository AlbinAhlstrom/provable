import pytest
from src.domain.difficulty import Difficulty
from src.adapters.repository import FakeDifficultyRepository
from src.service_layer.unit_of_work import FakeUnitOfWork
from src.app import app

def test_domain_entity_instantiation():
    """Verify domain entity can be instantiated."""
    item = Difficulty(id="test-1", name="test-1", rows=1, columns=1, mine_count=1)
    assert item is not None

def test_fake_repository_crud():
    """Verify repository CRUD operations in memory."""
    repo = FakeDifficultyRepository()
    item = Difficulty(id="test-1", name="test-1", rows=1, columns=1, mine_count=1)
    repo.add(item)
    assert len(repo.list()) == 1

def test_fake_uow_commit():
    """Verify Unit of Work transaction lifecycle."""
    uow = FakeUnitOfWork()
    with uow:
        getattr(uow, "difficulties").add(Difficulty(id="test-1", name="test-1", rows=1, columns=1, mine_count=1))
        uow.commit()
    assert uow.committed
