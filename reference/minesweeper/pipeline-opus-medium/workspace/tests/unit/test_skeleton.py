import pytest
from src.domain.game import Game
from src.adapters.repository import FakeGameRepository
from src.service_layer.unit_of_work import FakeUnitOfWork
from src.app import app

def test_domain_entity_instantiation():
    """Verify domain entity can be instantiated."""
    item = Game(id="test-1", difficulty_id="test-1", width=1, height=1, mine_count=1, remaining_mines=1, created_at="test-1")
    assert item is not None

def test_fake_repository_crud():
    """Verify repository CRUD operations in memory."""
    repo = FakeGameRepository()
    item = Game(id="test-1", difficulty_id="test-1", width=1, height=1, mine_count=1, remaining_mines=1, created_at="test-1")
    repo.add(item)
    assert len(repo.list()) == 1

def test_fake_uow_commit():
    """Verify Unit of Work transaction lifecycle."""
    uow = FakeUnitOfWork()
    with uow:
        getattr(uow, "games").add(Game(id="test-1", difficulty_id="test-1", width=1, height=1, mine_count=1, remaining_mines=1, created_at="test-1"))
        uow.commit()
    assert uow.committed
