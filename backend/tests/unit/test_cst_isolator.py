import pytest
from onboarding.cst_isolator import extract_class_cst, splice_class_cst

SAMPLE_MODULE_CODE = """# Top-level module comment
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PizzaOrder:
    \"\"\"Aggregate Root for Pizza Orders.\"\"\"
    id: str
    customer_name: str = "Guest"
    status: str = "PENDING"
    total_amount: float = 0.0

    def calculate_total(self) -> float:
        # Initial calculation
        return self.total_amount

@dataclass
class PizzaItem:
    \"\"\"Value Object for Pizza Item.\"\"\"
    name: str
    price: float = 0.0

def helper_function():
    # Helper that must NOT be touched
    return True
"""

def test_extract_class_cst_extracts_target_class_with_comments():
    class_code = extract_class_cst(SAMPLE_MODULE_CODE, "PizzaOrder")
    
    assert "class PizzaOrder:" in class_code
    assert '"""Aggregate Root for Pizza Orders."""' in class_code
    assert "# Initial calculation" in class_code
    assert "class PizzaItem" not in class_code
    assert "helper_function" not in class_code

def test_splice_class_cst_updates_class_while_preserving_surrounding_code():
    new_pizza_order_code = """@dataclass
class PizzaOrder:
    \"\"\"Aggregate Root for Pizza Orders with updated logic.\"\"\"
    id: str
    customer_name: str = "Guest"
    status: str = "PENDING"
    total_amount: float = 0.0
    discount_applied: bool = False

    def calculate_total(self) -> float:
        # Updated calculation with discount
        return self.total_amount * 0.9 if self.discount_applied else self.total_amount
"""
    spliced_code = splice_class_cst(SAMPLE_MODULE_CODE, "PizzaOrder", new_pizza_order_code)
    
    # 1. Verify updated class contents
    assert "discount_applied: bool = False" in spliced_code
    assert "# Updated calculation with discount" in spliced_code
    
    # 2. Verify surrounding code is 100% preserved
    assert "# Top-level module comment" in spliced_code
    assert "from dataclasses import dataclass" in spliced_code
    assert "class PizzaItem:" in spliced_code
    assert '"""Value Object for Pizza Item."""' in spliced_code
    assert "def helper_function():" in spliced_code
    assert "# Helper that must NOT be touched" in spliced_code


def test_splice_class_cst_synchronizes_datetime_and_fallback_imports():
    orig_code = """from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional

try:
    from src.domain.exceptions import DomainError
    from src.domain.events import DomainEvent
except ImportError:
    try:
        from domain.exceptions import DomainError
        from domain.events import DomainEvent
    except ImportError:
        pass

@dataclass
class Equipment:
    id: str
"""

    mutated_class = """@dataclass
class Equipment:
    id: str
    operating_hours: float = 0.0

    def check_status(self):
        tz = timezone.utc
        delta = timedelta(hours=1)
        if self.operating_hours >= 500:
            self.events.append(MaintenanceRequiredEvent(self.id, self.operating_hours))
            raise MaintenanceRequiredError("Lockout")
"""

    spliced = splice_class_cst(orig_code, "Equipment", mutated_class)

    # Verify datetime imports
    assert "timezone" in spliced.split("from datetime import")[1].split("\n")[0]
    assert "timedelta" in spliced.split("from datetime import")[1].split("\n")[0]

    # Verify both primary and fallback exception/event imports
    src_exc_line = [l for l in spliced.splitlines() if "from src.domain.exceptions import" in l][0]
    dom_exc_line = [l for l in spliced.splitlines() if "from domain.exceptions import" in l][0]
    assert "MaintenanceRequiredError" in src_exc_line
    assert "MaintenanceRequiredError" in dom_exc_line

    src_evt_line = [l for l in spliced.splitlines() if "from src.domain.events import" in l][0]
    dom_evt_line = [l for l in spliced.splitlines() if "from domain.events import" in l][0]
    assert "MaintenanceRequiredEvent" in src_evt_line
    assert "MaintenanceRequiredEvent" in dom_evt_line


def test_splice_class_cst_synchronizes_stdlib_and_typing_imports():
    orig_code = """from dataclasses import dataclass
from typing import Optional

@dataclass
class Contract:
    id: str
"""

    mutated_class = """@dataclass
class Contract:
    id: str
    duration: Optional[Union[int, float]] = None

    def calc(self):
        return math.ceil(10.5)
"""

    spliced = splice_class_cst(orig_code, "Contract", mutated_class)

    assert "import math" in spliced
    assert "Union" in spliced.split("from typing import")[1].split("\n")[0]


