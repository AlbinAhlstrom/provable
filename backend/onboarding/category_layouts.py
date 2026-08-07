"""
Category Page Layout Templates for Provable Synthesis Engine.

Provides standardized macro structural page layout templates for standard application categories
(E-Commerce, Service Booking, Operations Dashboard, SaaS Analytics) and custom novel applications.
"""

from typing import Dict, Any, List

CATEGORY_PAGE_LAYOUTS: Dict[str, Dict[str, Any]] = {
    "service_booking": {
        "id": "service_booking",
        "name": "Service & Appointment Booking Layout",
        "description": "Sticky top bar, hero with primary booking CTA, split-view provider cards with weekly calendar grid, and slide-over booking reservation drawer.",
        "category": "Services & Healthcare",
        "slots": [
            {"name": "header", "purpose": "Navigation, branding, user auth status"},
            {"name": "hero", "purpose": "Value proposition, primary search & quick CTA"},
            {"name": "main_content", "purpose": "Provider cards, availability slots, and weekly calendar view"},
            {"name": "modal_drawer", "purpose": "Reservation confirmation drawer or appointment booking form"},
            {"name": "footer", "purpose": "Trust badges, operating hours, support info"}
        ]
    },
    "e_commerce": {
        "id": "e_commerce",
        "name": "Product Catalog & Storefront Layout",
        "description": "Sticky search header with cart counter, hero promotional banner, category pill filters, responsive product grid, and slide-out cart drawer.",
        "category": "E-Commerce & Retail",
        "slots": [
            {"name": "header", "purpose": "Storefront brand, search bar, cart toggle badge"},
            {"name": "hero", "purpose": "Featured deal or seasonal banner"},
            {"name": "filter_bar", "purpose": "Category filters, price slider, search text"},
            {"name": "main_content", "purpose": "Interactive product cards grid with quick add-to-cart"},
            {"name": "modal_drawer", "purpose": "Slide-out cart drawer with order summary and checkout button"},
            {"name": "footer", "purpose": "Payment badges, shipping terms, contact details"}
        ]
    },
    "operations_dashboard": {
        "id": "operations_dashboard",
        "name": "Merchant Operations & KDS Dashboard Layout",
        "description": "Sidebar navigation, top KPI stat bar, multi-column work queue / status pipeline board, and operational control panel.",
        "category": "Operations & Logistics",
        "slots": [
            {"name": "sidebar", "purpose": "Navigation items, active workspace switcher"},
            {"name": "kpi_bar", "purpose": "Key performance metrics (Pending, In Progress, Complete, Revenue)"},
            {"name": "main_content", "purpose": "Kanban pipeline or live queue status grid"},
            {"name": "control_panel", "purpose": "Quick status update actions and inventory controls"}
        ]
    },
    "saas_analytics": {
        "id": "saas_analytics",
        "name": "SaaS & Analytics Workbench Layout",
        "description": "Header bar, metric summary cards, filterable data workbench/table, and detail inspection drawer.",
        "category": "B2B & Analytics",
        "slots": [
            {"name": "header", "purpose": "Workspace brand, user profile, global search"},
            {"name": "kpi_bar", "purpose": "4-up key performance metric cards"},
            {"name": "main_content", "purpose": "Filterable data table / interactive chart list"},
            {"name": "modal_drawer", "purpose": "Entity detail drawer and edit modal"}
        ]
    },
    "custom_novel": {
        "id": "custom_novel",
        "name": "Novel Custom Layout",
        "description": "Flexible multi-region layout customized dynamically for unique, non-standard business concepts.",
        "category": "Novel & Custom",
        "slots": [
            {"name": "header", "purpose": "App brand and primary actions"},
            {"name": "main_content", "purpose": "Custom interactive workbench / workspace area"},
            {"name": "modal_drawer", "purpose": "Contextual action modal or drawer"}
        ]
    }
}


def get_category_layout(category_id: str) -> Dict[str, Any]:
    """Retrieve category layout definition or fallback to custom_novel."""
    return CATEGORY_PAGE_LAYOUTS.get(category_id, CATEGORY_PAGE_LAYOUTS["custom_novel"])
