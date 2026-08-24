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
