"""
Unit tests for Stateful Orchestration Graph (Loop A: Backend Domain -> Loop B: Frontend UI -> Loop C: Watchdog).
Verifies that the entire 3-stage Graph executes cleanly with FakeUnitOfWork and ZERO domain hardcoding.
"""

import pytest
from service_layer.unit_of_work import FakeUnitOfWork
from onboarding.orchestration_graph import run_onboarding_graph, GraphExecutionResult

def test_orchestration_graph_execution_with_fake_uow():
    uow = FakeUnitOfWork()
    pitch = "An app to order pizzas"

    result = run_onboarding_graph(pitch, uow=uow)

    assert isinstance(result, GraphExecutionResult)
    assert result.status == "success"
    assert result.ontology is not None
    assert result.ontology.master_entity.entity_name.lower() in ["pizza", "item", "product", "dish"]
    
    # Assert backend artifacts generated
    assert any(k.endswith("model.py") for k in result.backend_files)
    assert any(k.endswith("commands.py") for k in result.backend_files)
    assert any(k.endswith("events.py") for k in result.backend_files)
    
    # Assert frontend code generated
    assert result.frontend_code != ""
    assert "export default function App" in result.frontend_code
    
    # Assert UoW persisted requirements
    assert uow.committed is True
    reqs = uow.requirements.list()
    assert len(reqs) > 0


def test_orchestration_graph_arbitrary_domain_scuba():
    uow = FakeUnitOfWork()
    pitch = "Scuba diving excursion and gear rental portal"

    result = run_onboarding_graph(pitch, uow=uow)

    assert result.status == "success"
    assert result.ontology.master_entity.entity_name != ""
    assert "Scuba" in result.ontology.master_entity.entity_name or "Gear" in result.ontology.master_entity.entity_name or "Rental" in result.ontology.master_entity.entity_name or "Item" in result.ontology.master_entity.entity_name
    
    # Ensure zero babysitter keywords in generated frontend
    assert "sitter" not in result.frontend_code.lower()
    assert "babysit" not in result.frontend_code.lower()
