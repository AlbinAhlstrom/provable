import pytest
import os
from onboarding.router_engine import (
    DomainStructureSchema, EntitySpec, AttributeSpec
)
from onboarding.skeleton_builder import (
    generate_fullstack_skeleton_files,
    build_and_write_skeleton
)

@pytest.fixture
def sample_pizza_structure():
    return DomainStructureSchema(
        domain_name="PizzeriaDomain",
        entities=[
            EntitySpec(
                name="PizzaOrder",
                is_aggregate_root=True,
                attributes=[
                    AttributeSpec(name="id", type="str", required=True),
                    AttributeSpec(name="customer_name", type="str", required=True, default_value="Guest"),
                    AttributeSpec(name="status", type="str", required=True, default_value="PENDING"),
                    AttributeSpec(name="total_amount", type="float", required=True, default_value=0.0)
                ],
                relationships=[{"target": "PizzaItem", "relation_type": "one_to_many"}]
            )
        ],
        value_objects=[
            EntitySpec(
                name="PizzaItem",
                is_aggregate_root=False,
                attributes=[
                    AttributeSpec(name="name", type="str", required=True),
                    AttributeSpec(name="price", type="float", required=True, default_value=0.0)
                ]
            )
        ]
    )

def test_generate_fullstack_skeleton_files_creates_all_layers(sample_pizza_structure):
    files = generate_fullstack_skeleton_files(sample_pizza_structure)
    
    # 1. Domain Aggregate isolation (SRP)
    assert any("domain/pizza_order.py" in path.replace("\\", "/") for path in files)
    domain_code = next(code for path, code in files.items() if "domain/pizza_order.py" in path.replace("\\", "/"))
    assert "class PizzaOrder:" in domain_code or "@dataclass" in domain_code
    assert "customer_name: str" in domain_code
    assert "total_amount: float" in domain_code
    
    # 2. Repository and UnitOfWork
    assert any("adapters/repository.py" in path.replace("\\", "/") for path in files)
    repo_code = next(code for path, code in files.items() if "adapters/repository.py" in path.replace("\\", "/"))
    assert "class AbstractPizzaOrderRepository" in repo_code
    assert "class FakePizzaOrderRepository" in repo_code
    
    assert any("service_layer/unit_of_work.py" in path.replace("\\", "/") for path in files)
    uow_code = next(code for path, code in files.items() if "service_layer/unit_of_work.py" in path.replace("\\", "/"))
    assert "class AbstractUnitOfWork" in uow_code
    assert "class FakeUnitOfWork" in uow_code
    
    # 3. Pydantic DTOs & FastAPI Routers (for immediate OpenAPI generation)
    assert any("entrypoints/schemas.py" in path.replace("\\", "/") for path in files)
    schemas_code = next(code for path, code in files.items() if "entrypoints/schemas.py" in path.replace("\\", "/"))
    assert "class PizzaOrderCreateSchema" in schemas_code or "class PizzaOrderSchema" in schemas_code
    
    assert any("entrypoints/routers/pizza_order.py" in path.replace("\\", "/") for path in files)
    router_code = next(code for path, code in files.items() if "entrypoints/routers/pizza_order.py" in path.replace("\\", "/"))
    assert "router = APIRouter" in router_code
    
    # 4. FastAPI app entrypoint
    assert any("app.py" in path.replace("\\", "/") for path in files)
    app_code = next(code for path, code in files.items() if "app.py" in path.replace("\\", "/"))
    assert "app = FastAPI" in app_code

def test_build_and_write_skeleton_in_memory_or_temp(tmp_path, sample_pizza_structure):
    target_dir = str(tmp_path)
    created_paths = build_and_write_skeleton(sample_pizza_structure, target_dir=target_dir)
    
    assert len(created_paths) >= 5
    for p in created_paths:
        assert os.path.exists(p)


def test_generate_domain_module_orders_non_default_before_default_fields():
    """Verify that fields without defaults are always rendered before fields with defaults in @dataclass."""
    from onboarding.skeleton_builder import generate_domain_module
    
    # Intermixed required and defaulted attributes matching the warehouse Pallet issue
    mixed_entity = EntitySpec(
        name="Pallet",
        is_aggregate_root=True,
        attributes=[
            AttributeSpec(name="pallet_id", type="str", required=True),
            AttributeSpec(name="tracking_code", type="str", required=False), # default None
            AttributeSpec(name="current_zone_id", type="str", required=False), # default None
            AttributeSpec(name="weight_kg", type="float", required=True), # non-default
            AttributeSpec(name="status", type="str", required=True, default_value="UNASSIGNED"), # default "UNASSIGNED"
            AttributeSpec(name="last_moved_datetime", type="str", required=False), # default None
            AttributeSpec(name="created_datetime", type="str", required=True) # non-default
        ]
    )

    code = generate_domain_module(mixed_entity)

    # Compile and execute the generated code in a local namespace to ensure Python @dataclass succeeds without TypeError
    namespace = {}
    exec(code, namespace)
    pallet_cls = namespace.get("Pallet")
    assert pallet_cls is not None

    # Instantiate the dataclass with positional or keyword arguments
    instance = pallet_cls(pallet_id="PAL-1", weight_kg=12.5, created_datetime="2026-08-26")
    assert instance.pallet_id == "PAL-1"
    assert instance.weight_kg == 12.5
    assert instance.created_datetime == "2026-08-26"
    assert instance.tracking_code is None
    assert instance.status == "UNASSIGNED"

