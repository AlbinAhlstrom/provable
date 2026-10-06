"""
Provable Wayfinder Engine — Architectural Decision Mapping & BDD Frontier Navigation.

Implements the "Plan, Don't Do" paradigm:
1. Destination: The Bounded Context & North Star Vision.
2. The Frontier: Actionable, unblocked architectural decision tickets presented as prefilled BDD templates.
3. Fog of War: Downstream dependencies locked until upstream decisions are established.
4. Deterministic Translation: Locked decisions compile directly into Living Deck RuleCards and TDD tests.
"""

import re
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


class WayfinderTicketType(str, Enum):
    GRILL = "GRILL"
    PROTOTYPE = "PROTOTYPE"
    RESEARCH = "RESEARCH"
    TASK = "TASK"


class WayfinderTicketStatus(str, Enum):
    LOCKED = "LOCKED"
    FRONTIER = "FRONTIER"
    FOG = "FOG"


@dataclass
class BddClause:
    given: str
    when: str
    then: str
    unless: Optional[str] = None

    def to_gherkin_text(self) -> str:
        lines = [
            f"GIVEN {self.given}",
            f"WHEN {self.when}",
            f"THEN {self.then}"
        ]
        if self.unless:
            lines.append(f"UNLESS {self.unless}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BddClause":
        return cls(
            given=data.get("given", ""),
            when=data.get("when", ""),
            then=data.get("then", ""),
            unless=data.get("unless")
        )


@dataclass
class BddPreset:
    id: str
    label: str
    bdd: BddClause
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "bdd": self.bdd.to_dict(),
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BddPreset":
        return cls(
            id=data["id"],
            label=data["label"],
            bdd=BddClause.from_dict(data["bdd"]),
            description=data.get("description")
        )


@dataclass
class WayfinderTicket:
    id: str
    title: str
    ticket_type: str  # WayfinderTicketType
    status: str       # WayfinderTicketStatus
    target_aggregate: str
    rationale: str
    depends_on: List[str] = field(default_factory=list)
    bdd_template: Optional[BddClause] = None
    presets: List[BddPreset] = field(default_factory=list)
    schema_preview: Optional[Dict[str, Any]] = None
    resolved_bdd: Optional[BddClause] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "ticket_type": self.ticket_type,
            "status": self.status,
            "target_aggregate": self.target_aggregate,
            "rationale": self.rationale,
            "depends_on": self.depends_on,
            "bdd_template": self.bdd_template.to_dict() if self.bdd_template else None,
            "presets": [p.to_dict() for p in self.presets],
            "schema_preview": self.schema_preview,
            "resolved_bdd": self.resolved_bdd.to_dict() if self.resolved_bdd else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WayfinderTicket":
        return cls(
            id=data["id"],
            title=data["title"],
            ticket_type=data["ticket_type"],
            status=data["status"],
            target_aggregate=data.get("target_aggregate", "ApplicationDomain"),
            rationale=data.get("rationale", ""),
            depends_on=data.get("depends_on", []),
            bdd_template=BddClause.from_dict(data["bdd_template"]) if data.get("bdd_template") else None,
            presets=[BddPreset.from_dict(p) for p in data.get("presets", [])],
            schema_preview=data.get("schema_preview"),
            resolved_bdd=BddClause.from_dict(data["resolved_bdd"]) if data.get("resolved_bdd") else None
        )


@dataclass
class WayfinderGraphState:
    pitch: str
    brand_name: str
    tickets: List[WayfinderTicket] = field(default_factory=list)
    progress_pct: int = 0
    is_synthesis_ready: bool = False

    def get_frontier_tickets(self) -> List[WayfinderTicket]:
        return [t for t in self.tickets if t.status == WayfinderTicketStatus.FRONTIER.value]

    def get_fog_tickets(self) -> List[WayfinderTicket]:
        return [t for t in self.tickets if t.status == WayfinderTicketStatus.FOG.value]

    def get_locked_tickets(self) -> List[WayfinderTicket]:
        return [t for t in self.tickets if t.status == WayfinderTicketStatus.LOCKED.value]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pitch": self.pitch,
            "brand_name": self.brand_name,
            "tickets": [t.to_dict() for t in self.tickets],
            "frontier": [t.to_dict() for t in self.get_frontier_tickets()],
            "fog": [t.to_dict() for t in self.get_fog_tickets()],
            "locked": [t.to_dict() for t in self.get_locked_tickets()],
            "progress_pct": self.progress_pct,
            "is_synthesis_ready": self.is_synthesis_ready
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WayfinderGraphState":
        return cls(
            pitch=data.get("pitch", ""),
            brand_name=data.get("brand_name", "ProvableApp"),
            tickets=[WayfinderTicket.from_dict(t) for t in data.get("tickets", [])],
            progress_pct=data.get("progress_pct", 0),
            is_synthesis_ready=data.get("is_synthesis_ready", False)
        )


def _extract_primary_noun(pitch: str) -> str:
    words = [w for w in re.findall(r'[A-Za-z]+', pitch) if len(w) > 3]
    blacklist = {"with", "this", "that", "from", "have", "some", "such", "engine", "system", "app", "application", "tool"}
    candidates = [w.capitalize() for w in words if w.lower() not in blacklist]
    return candidates[0] if candidates else "Item"


def _detect_domain_category(pitch: str) -> str:
    lower = pitch.lower()
    game_keywords = {"chess", "checkers", "game", "play", "match", "cards", "poker", "puzzle", "quiz", "battle", "duel", "board"}
    ordering_keywords = {"pizza", "food", "restaurant", "cafe", "coffee", "roastery", "bakery", "menu", "cart", "order", "shop", "store", "delivery", "checkout", "subscription", "e-commerce", "ecommerce", "dishes"}
    booking_keywords = {"hotel", "room", "book", "booking", "reserve", "reservation", "stay", "salon", "clinic", "appointment", "rental", "hostel", "housekeeping"}
    productivity_keywords = {"task", "todo", "kanban", "project", "tracker", "workflow", "note", "notes", "list", "issue", "bug", "ticket"}

    words = set(re.findall(r'[a-z]+', lower))
    if words & game_keywords:
        return "GAME"
    if words & ordering_keywords:
        return "ORDERING"
    if words & booking_keywords:
        return "BOOKING"
    if words & productivity_keywords:
        return "PRODUCTIVITY"
    return "GENERAL"


def generate_wayfinder_graph(pitch: str) -> WayfinderGraphState:
    """
    Deconstructs a pitch into a 3-zone Wayfinder Graph grounded in human behavior:
    - Root decision tickets placed on the FRONTIER asking foundational user experience questions.
    - Downstream tickets placed in the FOG OF WAR with explicit causal dependencies.
    - Each ticket is prefilled with plain-English BDD Mad-Libs (Dan North principle: no tech jargon).
    """
    noun = _extract_primary_noun(pitch)
    category = _detect_domain_category(pitch)
    brand = f"{noun}Craft"

    if category == "GAME":
        # Frontier 1: Player Model & Interaction
        t1 = WayfinderTicket(
            id="wf-001-player-model",
            title="Who is Playing?",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FRONTIER.value,
            target_aggregate=noun,
            rationale="Determines whether players compete against a computer, share one screen, or play with friends online.",
            depends_on=[],
            bdd_template=BddClause(
                given="a local two-player game is started on the same device",
                when="the active player completes their move",
                then="alternate the turn to the opposing player on the shared board without requiring network login",
                unless="the game is over"
            ),
            presets=[
                BddPreset(
                    id="p_pass_and_play",
                    label="👥 Two Players on One Screen (Pass & Play)",
                    bdd=BddClause(
                        given="a local two-player game is started on the same device",
                        when="the active player completes their move",
                        then="alternate the turn to the opposing player on the shared board without requiring network login",
                        unless="the game is over"
                    ),
                    description="Two people take turns on the same phone, tablet, or laptop."
                ),
                BddPreset(
                    id="p_solo_vs_bot",
                    label="🤖 Solo Play (Against the Computer)",
                    bdd=BddClause(
                        given="a solo match against the computer opponent is active",
                        when="the human player completes a legal move",
                        then="the computer opponent calculates and executes its countermove automatically",
                        unless="the match has concluded in checkmate or stalemate"
                    ),
                    description="Play alone against a computer opponent at your own pace."
                ),
                BddPreset(
                    id="p_online_friends",
                    label="🌐 Play with a Friend Online",
                    bdd=BddClause(
                        given="a player initiates an online multiplayer match",
                        when="the host creates a game room",
                        then="generate a unique shareable invite link connecting the remote opponent to the live board",
                        unless="the game room already has two active connected players"
                    ),
                    description="Send an invitation link to play remotely with friends."
                )
            ]
        )

        # Frontier 2: Move Guidance & Rules
        t2 = WayfinderTicket(
            id="wf-002-move-guidance",
            title="Move Guidance & Rule Enforcement",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FRONTIER.value,
            target_aggregate=noun,
            rationale="Defines whether the board visually guides players on legal moves or keeps a clean board.",
            depends_on=[],
            bdd_template=BddClause(
                given="it is the active player's turn",
                when="the player selects a piece of their color",
                then="visually highlight all legal destination squares for that piece",
                unless="the selected piece has zero legal moves available"
            ),
            presets=[
                BddPreset(
                    id="p_guided_moves",
                    label="⭐ Guided Assistance (Highlight Legal Squares)",
                    bdd=BddClause(
                        given="it is the active player's turn",
                        when="the player selects a piece of their color",
                        then="visually highlight all legal destination squares for that piece",
                        unless="the selected piece has zero legal moves available"
                    ),
                    description="Visual dots and highlights guide players on allowable moves."
                ),
                BddPreset(
                    id="p_strict_board",
                    label="♟️ Classic Clean Board (Validation on Drop)",
                    bdd=BddClause(
                        given="it is the active player's turn with strict rules enabled",
                        when="the player attempts to place a piece on an illegal square",
                        then="reject the move, return the piece to its original square, and keep the active player's turn unchanged",
                        unless="the destination square is legally valid for that piece"
                    ),
                    description="Pure traditional board game experience without visual assist dots."
                )
            ]
        )

        # Fog 3: Taking Back Moves (Undo)
        t3 = WayfinderTicket(
            id="wf-003-undo",
            title="Taking Back Moves (Undo)",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Sets whether players can undo mistakes or if moves are permanent.",
            depends_on=["wf-001-player-model"],
            bdd_template=BddClause(
                given="at least one move has been completed in the active match",
                when="a player clicks the 'Take Back' button",
                then="revert the board state to the preceding turn and restore the previous player's turn",
                unless="the game has already ended in checkmate or draw"
            ),
            presets=[
                BddPreset(
                    id="p_undo_friendly",
                    label="⏪ Friendly Take-Backs (Undo Button)",
                    bdd=BddClause(
                        given="at least one move has been completed in the active match",
                        when="a player clicks the 'Take Back' button",
                        then="revert the board state to the preceding turn and restore the previous player's turn",
                        unless="the game has already ended in checkmate or draw"
                    ),
                    description="Casual learning sandbox where you can rethink your move."
                ),
                BddPreset(
                    id="p_undo_strict",
                    label="🔒 Strict Permanent Moves (No Take-Backs)",
                    bdd=BddClause(
                        given="strict permanent move mode is enabled",
                        when="a player attempts to undo or rewind a completed move",
                        then="prevent take-backs and keep the current board state unchanged",
                        unless="both players agree to reset the match from the beginning"
                    ),
                    description="Tournament-style discipline where every move counts."
                )
            ]
        )

        # Fog 4: Board Orientation & View
        t4 = WayfinderTicket(
            id="wf-004-board-view",
            title="Board Orientation & Perspective",
            ticket_type=WayfinderTicketType.PROTOTYPE.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Determines whether the board flips for each player or stays static.",
            depends_on=["wf-001-player-model"],
            bdd_template=BddClause(
                given="fixed perspective mode is active",
                when="the active turn alternates to the other player",
                then="maintain a static board orientation with White at rank 1 without auto-flipping",
                unless="a player manually clicks the 'Flip Board' toggle"
            ),
            presets=[
                BddPreset(
                    id="p_board_static",
                    label="🧭 Fixed Player Perspective",
                    bdd=BddClause(
                        given="fixed perspective mode is active",
                        when="the active turn alternates to the other player",
                        then="maintain a static board orientation with White at rank 1 without auto-flipping",
                        unless="a player manually clicks the 'Flip Board' toggle"
                    ),
                    description="Traditional static orientation."
                ),
                BddPreset(
                    id="p_board_flip",
                    label="🔄 Auto-Rotate Board for Current Player",
                    bdd=BddClause(
                        given="auto-rotate perspective mode is active in pass-and-play",
                        when="the active turn alternates to the other player",
                        then="rotate the board 180 degrees so the active player's pieces face their side of the screen",
                        unless="the player has locked the board orientation in settings"
                    ),
                    description="Ideal when sitting across from each other with a shared screen."
                )
            ]
        )

        # Fog 5: Turn Timers & Clocks
        t5 = WayfinderTicket(
            id="wf-005-timers",
            title="Turn Timers & Clocks",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Defines whether players play against a ticking clock or enjoy untimed moves.",
            depends_on=["wf-002-move-guidance"],
            bdd_template=BddClause(
                given="relaxed untimed mode is selected",
                when="the game board renders and turns progress",
                then="allow unlimited thinking time without displaying countdown clocks or time-out forfeits",
                unless="a timer duration is explicitly configured in settings"
            ),
            presets=[
                BddPreset(
                    id="p_timer_relaxed",
                    label="☕ Relaxed Untimed Play",
                    bdd=BddClause(
                        given="relaxed untimed mode is selected",
                        when="the game board renders and turns progress",
                        then="allow unlimited thinking time without displaying countdown clocks or time-out forfeits",
                        unless="a timer duration is explicitly configured in settings"
                    ),
                    description="No clock ticking down. Pure casual enjoyment."
                ),
                BddPreset(
                    id="p_timer_active",
                    label="⏱️ Active Countdown Clock",
                    bdd=BddClause(
                        given="an active countdown clock is enabled for both players",
                        when="the active player's remaining clock time reaches zero",
                        then="declare a time-out forfeit victory for the opponent and end the match",
                        unless="the opponent has insufficient mating material resulting in a draw"
                    ),
                    description="Fast-paced match with a ticking clock."
                )
            ]
        )

        # Fog 6: Game Over & Victory Moments
        t6 = WayfinderTicket(
            id="wf-006-game-over",
            title="Game Over & Victory Celebrations",
            ticket_type=WayfinderTicketType.PROTOTYPE.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Shapes what happens when checkmate, stalemate, or resignation occurs.",
            depends_on=["wf-003-undo"],
            bdd_template=BddClause(
                given="the active player's king is in check with zero legal escaping moves",
                when="the checkmate position is registered on the board",
                then="declare checkmate, display a victory banner announcing the winning color, and provide a 'New Game' button",
                unless="the position is a stalemate resulting in a draw"
            ),
            presets=[
                BddPreset(
                    id="p_gameover_banner",
                    label="🏆 Celebration Banner & Rematch Button",
                    bdd=BddClause(
                        given="the active player's king is in check with zero legal escaping moves",
                        when="the checkmate position is registered on the board",
                        then="declare checkmate, display a victory banner announcing the winning color, and provide a 'New Game' button",
                        unless="the position is a stalemate resulting in a draw"
                    ),
                    description="Clear, celebratory conclusion with seamless restart."
                ),
                BddPreset(
                    id="p_gameover_review",
                    label="📊 Move History & Review Sheet",
                    bdd=BddClause(
                        given="a match concludes in checkmate, stalemate, or resignation",
                        when="the game over summary screen is displayed",
                        then="display the complete chronological move history list allowing stepping forward and backward through the game",
                        unless="a new game is immediately started"
                    ),
                    description="Review what happened and learn from key moments."
                )
            ]
        )

    elif category == "ORDERING":
        # Frontier 1: Ordering Experience
        t1 = WayfinderTicket(
            id="wf-001-ordering-flow",
            title="Customer Ordering Experience",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FRONTIER.value,
            target_aggregate=noun,
            rationale="Determines whether customers can place orders instantly as guests or need accounts.",
            depends_on=[],
            bdd_template=BddClause(
                given="a customer adds items to their order",
                when="they proceed to checkout",
                then="let them enter delivery details and place the order immediately without creating an account",
                unless="required delivery fields are missing"
            ),
            presets=[
                BddPreset(
                    id="p_guest_checkout",
                    label="⚡ Instant Guest Checkout",
                    bdd=BddClause(
                        given="a customer adds items to their order",
                        when="they proceed to checkout",
                        then="let them enter delivery details and place the order immediately without creating an account",
                        unless="required delivery fields are missing"
                    ),
                    description="Frictionless fast checkout for first-time or hungry customers."
                ),
                BddPreset(
                    id="p_customer_profiles",
                    label="👤 Saved Customer Profiles",
                    bdd=BddClause(
                        given="a returning customer places an order",
                        when="payment succeeds",
                        then="save their favorite items and address for 1-click reordering next time",
                        unless="customer chooses to checkout as guest"
                    ),
                    description="Convenient re-ordering for loyal customers."
                )
            ]
        )

        # Frontier 2: Item Customization
        t2 = WayfinderTicket(
            id="wf-002-customization",
            title="Item Customization & Options",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FRONTIER.value,
            target_aggregate=noun,
            rationale="Defines whether items can be customized with toppings/options or are fixed.",
            depends_on=[],
            bdd_template=BddClause(
                given="a customer chooses an item from the menu",
                when="they select custom options or sizes",
                then="update the preview and recalculate the live price instantly",
                unless="maximum allowed selections are exceeded"
            ),
            presets=[
                BddPreset(
                    id="p_custom_options",
                    label="🍕 Interactive Customizer (Sizes & Toppings)",
                    bdd=BddClause(
                        given="a customer chooses an item from the menu",
                        when="they select custom options or sizes",
                        then="update the preview and recalculate the live price instantly",
                        unless="maximum allowed selections are exceeded"
                    ),
                    description="Full customization drawer with live price updates."
                ),
                BddPreset(
                    id="p_fixed_items",
                    label="📦 Simple Quick-Add (Fixed Menu Items)",
                    bdd=BddClause(
                        given="a customer browsing the catalog",
                        when="they tap Add on any item",
                        then="add the item directly to the basket with standard ingredients",
                        unless="the item is marked out of stock"
                    ),
                    description="Fast, single-tap ordering with fixed items."
                )
            ]
        )

        # Fog 3: Live Order Tracking
        t3 = WayfinderTicket(
            id="wf-003-tracking",
            title="Live Order Tracking & Milestones",
            ticket_type=WayfinderTicketType.PROTOTYPE.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Configures how customers see their order progress after ordering.",
            depends_on=["wf-001-ordering-flow"],
            bdd_template=BddClause(
                given="an order is successfully placed",
                when="the kitchen updates the order status",
                then="advance the progress bar on the customer's live tracking screen",
                unless="the order was canceled"
            ),
            presets=[
                BddPreset(
                    id="p_live_tracker",
                    label="📍 Live Progress Tracker (Received ➔ Cooking ➔ Ready)",
                    bdd=BddClause(
                        given="an order is successfully placed",
                        when="the kitchen updates the order status",
                        then="advance the progress bar on the customer's live tracking screen",
                        unless="the order was canceled"
                    ),
                    description="Visual milestone bar showing live cooking and delivery progress."
                ),
                BddPreset(
                    id="p_simple_confirmation",
                    label="✉️ Simple Order Receipt & Confirmation",
                    bdd=BddClause(
                        given="order submission succeeds",
                        when="payment clears",
                        then="show an order confirmation number and estimated arrival time",
                        unless=None
                    ),
                    description="Clean, simple confirmation without live tracking steps."
                )
            ]
        )

        # Fog 4: Order Changes & Cancellations
        t4 = WayfinderTicket(
            id="wf-004-modifications",
            title="Order Modifications & Grace Period",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Sets whether customers can tweak items after placing an order.",
            depends_on=["wf-001-ordering-flow"],
            bdd_template=BddClause(
                given="an order has just been placed",
                when="customer wants to change an item within 5 minutes",
                then="allow updating toppings or delivery address",
                unless="the kitchen has already started preparing the food"
            ),
            presets=[
                BddPreset(
                    id="p_grace_changes",
                    label="⏱️ 5-Minute Grace Period Changes",
                    bdd=BddClause(
                        given="an order has just been placed",
                        when="customer wants to change an item within 5 minutes",
                        then="allow updating toppings or delivery address",
                        unless="the kitchen has already started preparing the food"
                    ),
                    description="Peace of mind for accidental clicks or forgotten items."
                ),
                BddPreset(
                    id="p_firm_submission",
                    label="🔒 Firm Order Submission",
                    bdd=BddClause(
                        given="an order is submitted",
                        when="the customer confirms payment",
                        then="lock the order immediately and instruct the user to call the store for changes",
                        unless=None
                    ),
                    description="Prevents kitchen confusion once an order ticket prints."
                )
            ]
        )

        # Fog 5: Special Offers & Discounts
        t5 = WayfinderTicket(
            id="wf-005-promos",
            title="Special Offers & Discounts",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Determines whether promo codes and automated free-shipping thresholds apply.",
            depends_on=["wf-002-customization"],
            bdd_template=BddClause(
                given="a customer enters a promo code or spends over $30",
                when="reviewing the cart total",
                then="apply the percentage discount and highlight savings in green",
                unless="the promo code has expired"
            ),
            presets=[
                BddPreset(
                    id="p_promo_discounts",
                    label="🏷️ Promo Codes & Automatic Discounts",
                    bdd=BddClause(
                        given="a customer enters a promo code or spends over $30",
                        when="reviewing the cart total",
                        then="apply the percentage discount and highlight savings in green",
                        unless="the promo code has expired"
                    ),
                    description="Incentivize larger orders with coupons and free delivery."
                ),
                BddPreset(
                    id="p_flat_pricing",
                    label="💵 Transparent Flat Pricing",
                    bdd=BddClause(
                        given="items are in the cart",
                        when="viewing the total",
                        then="display standard menu prices without coupon code inputs",
                        unless=None
                    ),
                    description="No coupon boxes, maintaining clean straightforward pricing."
                )
            ]
        )

        # Fog 6: Dietary Badges & Allergens
        t6 = WayfinderTicket(
            id="wf-006-dietary",
            title="Dietary Badges & Information",
            ticket_type=WayfinderTicketType.PROTOTYPE.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Configures how allergen and dietary tags are displayed to shoppers.",
            depends_on=["wf-003-tracking"],
            bdd_template=BddClause(
                given="a customer views menu items",
                when="browsing or adding to cart",
                then="display clear badges for Vegetarian, Gluten-Free, or Spicy options",
                unless=None
            ),
            presets=[
                BddPreset(
                    id="p_dietary_badges",
                    label="🥗 Dietary Badges & Filter Tags",
                    bdd=BddClause(
                        given="a customer views menu items",
                        when="browsing or adding to cart",
                        then="display clear badges for Vegetarian, Gluten-Free, or Spicy options",
                        unless=None
                    ),
                    description="Helps diners quickly find food matching their dietary needs."
                ),
                BddPreset(
                    id="p_clean_menu",
                    label="⚡ Clean Standard Menu Presentation",
                    bdd=BddClause(
                        given="menu is displayed",
                        when="customer browses",
                        then="show photos, titles, and descriptions without dietary filter tags",
                        unless=None
                    ),
                    description="Simple, uncluttered menu presentation."
                )
            ]
        )

    elif category == "BOOKING":
        # Frontier 1: Reservation Experience
        t1 = WayfinderTicket(
            id="wf-001-booking-flow",
            title="Reservation Experience",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FRONTIER.value,
            target_aggregate=noun,
            rationale="Determines whether guests receive instant confirmation or wait for host approval.",
            depends_on=[],
            bdd_template=BddClause(
                given="a guest selects open dates and a room",
                when="they enter their details and click Reserve",
                then="confirm the reservation immediately and block those dates on the calendar",
                unless="another guest completed booking those dates moments earlier"
            ),
            presets=[
                BddPreset(
                    id="p_instant_booking",
                    label="📅 Instant Online Confirmation",
                    bdd=BddClause(
                        given="a guest selects open dates and a room",
                        when="they enter their details and click Reserve",
                        then="confirm the reservation immediately and block those dates on the calendar",
                        unless="another guest completed booking those dates moments earlier"
                    ),
                    description="Fast, automated confirmation without waiting for host review."
                ),
                BddPreset(
                    id="p_request_to_book",
                    label="📝 Request to Book (Host Approval)",
                    bdd=BddClause(
                        given="a guest selects dates",
                        when="they submit a stay request",
                        then="hold the dates as Pending and notify the manager to accept or decline",
                        unless="the request expires after 24 hours"
                    ),
                    description="Gives operators control over who books each stay."
                )
            ]
        )

        # Frontier 2: Guest Information & Intake
        t2 = WayfinderTicket(
            id="wf-002-guest-intake",
            title="Guest Information & Intake",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FRONTIER.value,
            target_aggregate=noun,
            rationale="Defines what information is collected from the guest during booking.",
            depends_on=[],
            bdd_template=BddClause(
                given="a guest reserving a stay",
                when="filling out their booking form",
                then="require only their full name, email, and mobile phone number",
                unless=None
            ),
            presets=[
                BddPreset(
                    id="p_fast_intake",
                    label="⚡ Fast Contact Intake (Name, Email & Phone)",
                    bdd=BddClause(
                        given="a guest reserving a stay",
                        when="filling out their booking form",
                        then="require only their full name, email, and mobile phone number",
                        unless=None
                    ),
                    description="Minimal 3-field form to maximize booking completion."
                ),
                BddPreset(
                    id="p_detailed_intake",
                    label="📋 Detailed Stay Questionnaire",
                    bdd=BddClause(
                        given="a guest completes a booking",
                        when="entering information",
                        then="ask for estimated arrival time, dietary preferences, and room notes",
                        unless="guest chooses to skip optional questions"
                    ),
                    description="Helps staff prepare personalized experiences ahead of arrival."
                )
            ]
        )

        # Fog 3: Cancellation & Date Changes
        t3 = WayfinderTicket(
            id="wf-003-cancellation",
            title="Cancellation & Date Changes",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Sets whether guests can cancel or change dates self-service.",
            depends_on=["wf-001-booking-flow"],
            bdd_template=BddClause(
                given="an active reservation",
                when="guest requests date changes at least 24 hours prior to check-in",
                then="allow picking new dates without extra fees",
                unless="check-in is less than 24 hours away"
            ),
            presets=[
                BddPreset(
                    id="p_free_changes",
                    label="🔄 Free Flexible Changes (Up to 24h Before Check-in)",
                    bdd=BddClause(
                        given="an active reservation",
                        when="guest requests date changes at least 24 hours prior to check-in",
                        then="allow picking new dates without extra fees",
                        unless="check-in is less than 24 hours away"
                    ),
                    description="Traveler-friendly policy with self-service changes."
                ),
                BddPreset(
                    id="p_firm_booking",
                    label="🔒 Firm Non-Refundable Rates",
                    bdd=BddClause(
                        given="a reservation is confirmed",
                        when="a guest attempts to cancel",
                        then="retain the reservation deposit and keep dates reserved",
                        unless="host manually grants an exception"
                    ),
                    description="Protects room revenue for popular peak dates."
                )
            ]
        )

        # Fog 4: Double-Booking & Conflict Guard
        t4 = WayfinderTicket(
            id="wf-004-conflict-guard",
            title="Double-Booking & Conflict Prevention",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Guarantees rooms are not double-booked when two people view simultaneously.",
            depends_on=["wf-001-booking-flow"],
            bdd_template=BddClause(
                given="a guest is viewing room dates",
                when="another customer confirms payment for the same night",
                then="mark the night as Unavailable on the calendar and notify the viewing guest",
                unless="the previous transaction fails"
            ),
            presets=[
                BddPreset(
                    id="p_date_lock",
                    label="🛡️ Real-Time Date Lock",
                    bdd=BddClause(
                        given="a guest is viewing room dates",
                        when="another customer confirms payment for the same night",
                        then="mark the night as Unavailable on the calendar and notify the viewing guest",
                        unless="the previous transaction fails"
                    ),
                    description="Guarantees two guests are never booked into the same room."
                ),
                BddPreset(
                    id="p_group_capacity",
                    label="👥 Multi-Room Group Allocations",
                    bdd=BddClause(
                        given="a group booking multiple rooms",
                        when="selecting quantity",
                        then="allow booking up to available room inventory for that category",
                        unless="requested rooms exceed available count"
                    ),
                    description="Enables booking multiple rooms for family trips or events."
                )
            ]
        )

        # Fog 5: Reminders & Calendar Sync
        t5 = WayfinderTicket(
            id="wf-005-reminders",
            title="Arrival Reminders & Calendar Export",
            ticket_type=WayfinderTicketType.TASK.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Defines whether guests receive automatic arrival reminders and calendar invites.",
            depends_on=["wf-002-guest-intake"],
            bdd_template=BddClause(
                given="an upcoming stay",
                when="24 hours remain before check-in time",
                then="send an automated reminder message with directions and door code instructions",
                unless="guest opted out of notifications"
            ),
            presets=[
                BddPreset(
                    id="p_automated_reminders",
                    label="📲 Automated Stay Reminders (SMS / Email)",
                    bdd=BddClause(
                        given="an upcoming stay",
                        when="24 hours remain before check-in time",
                        then="send an automated reminder message with directions and door code instructions",
                        unless="guest opted out of notifications"
                    ),
                    description="Ensures smooth arrivals with zero confusion."
                ),
                BddPreset(
                    id="p_calendar_invite",
                    label="📄 Calendar Invite Export (.ics)",
                    bdd=BddClause(
                        given="booking is confirmed",
                        when="confirmation displays",
                        then="provide a 1-click Add to Calendar button for Google and Apple calendars",
                        unless=None
                    ),
                    description="Simple calendar synchronization."
                )
            ]
        )

        # Fog 6: Housekeeping & Room Readiness
        t6 = WayfinderTicket(
            id="wf-006-room-readiness",
            title="Housekeeping & Room Readiness",
            ticket_type=WayfinderTicketType.PROTOTYPE.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Shapes whether room readiness gates guest check-in.",
            depends_on=["wf-003-cancellation"],
            bdd_template=BddClause(
                given="a room after guest departure",
                when="cleaning staff finishes preparing the room",
                then="mark room status as Clean and ready for next check-in",
                unless="maintenance repairs are required"
            ),
            presets=[
                BddPreset(
                    id="p_clean_tracker",
                    label="🧹 Housekeeping Clean Status Tracker",
                    bdd=BddClause(
                        given="a room after guest departure",
                        when="cleaning staff finishes preparing the room",
                        then="mark room status as Clean and ready for next check-in",
                        unless="maintenance repairs are required"
                    ),
                    description="Prevents checking guests into rooms before they are spotless."
                ),
                BddPreset(
                    id="p_auto_availability",
                    label="⚡ Automatic Check-in Availability",
                    bdd=BddClause(
                        given="check-in day arrives",
                        when="official check-in time passes",
                        then="allow guest check-in automatically",
                        unless="booking has an outstanding balance"
                    ),
                    description="Automated workflow for self-service properties."
                )
            ]
        )

    else:
        # PRODUCTIVITY / GENERAL
        # Frontier 1: Item Workflow
        t1 = WayfinderTicket(
            id="wf-001-workflow",
            title="Item Workflow & Completion",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FRONTIER.value,
            target_aggregate=noun,
            rationale="Determines how items move from initial creation to completion.",
            depends_on=[],
            bdd_template=BddClause(
                given=f"an active {noun.lower()} on the list",
                when="user clicks mark complete",
                then="mark the item as completed and strike it through",
                unless="the item is locked or archived"
            ),
            presets=[
                BddPreset(
                    id="p_simple_complete",
                    label="📋 Simple Check-Off (Open ➔ Done)",
                    bdd=BddClause(
                        given=f"an active {noun.lower()} on the list",
                        when="user clicks mark complete",
                        then="mark the item as completed and strike it through",
                        unless="the item is locked or archived"
                    ),
                    description="Simple, satisfying checklist workflow."
                ),
                BddPreset(
                    id="p_multi_stage",
                    label="📌 Multi-Stage Progress (To Do ➔ In Progress ➔ Completed)",
                    bdd=BddClause(
                        given=f"work begins on a {noun.lower()}",
                        when="status is updated",
                        then="move the card to In Progress and show who is working on it",
                        unless=None
                    ),
                    description="Track progress across stages for organized projects."
                )
            ]
        )

        # Frontier 2: Organization & Finding Items
        t2 = WayfinderTicket(
            id="wf-002-organization",
            title="Organization & Categorization",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FRONTIER.value,
            target_aggregate=noun,
            rationale="Defines how users categorize and filter items.",
            depends_on=[],
            bdd_template=BddClause(
                given=f"a {noun.lower()} on the board",
                when="user assigns a category tag or label",
                then="display a color badge and let users filter by that tag",
                unless=None
            ),
            presets=[
                BddPreset(
                    id="p_color_tags",
                    label="🏷️ Color Tags & Custom Labels",
                    bdd=BddClause(
                        given=f"a {noun.lower()} on the board",
                        when="user assigns a category tag or label",
                        then="display a color badge and let users filter by that tag",
                        unless=None
                    ),
                    description="Flexible labeling for quick visual filtering."
                ),
                BddPreset(
                    id="p_fast_search",
                    label="📁 Clean Flat List with Real-Time Search",
                    bdd=BddClause(
                        given=f"a collection of {noun.lower()} items",
                        when="user types into the search bar",
                        then="filter the list in real time to show only matching items",
                        unless="search box is empty"
                    ),
                    description="Minimalist, distraction-free interface."
                )
            ]
        )

        # Fog 3: Deadlines & Reminders
        t3 = WayfinderTicket(
            id="wf-003-deadlines",
            title="Due Dates & Deadlines",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Sets whether items have strict deadlines or calm backlogs.",
            depends_on=["wf-001-workflow"],
            bdd_template=BddClause(
                given=f"a {noun.lower()} with a deadline",
                when="the due date passes without completion",
                then="highlight the item in red and place it at the top of the view",
                unless="user marked the item complete"
            ),
            presets=[
                BddPreset(
                    id="p_due_date_alerts",
                    label="⏰ Due Dates with Overdue Highlighting",
                    bdd=BddClause(
                        given=f"a {noun.lower()} with a deadline",
                        when="the due date passes without completion",
                        then="highlight the item in red and place it at the top of the view",
                        unless="user marked the item complete"
                    ),
                    description="Keep important deadlines front and center."
                ),
                BddPreset(
                    id="p_calm_backlog",
                    label="📝 Flexible Backlog (No Date Pressure)",
                    bdd=BddClause(
                        given=f"items on the {noun.lower()} list",
                        when="reordering priorities",
                        then="allow manual drag and drop reordering without date constraints",
                        unless=None
                    ),
                    description="Calm, priority-driven list without deadline stress."
                )
            ]
        )

        # Fog 4: Completed Item Handling
        t4 = WayfinderTicket(
            id="wf-004-archive",
            title="Completed Items Handling",
            ticket_type=WayfinderTicketType.PROTOTYPE.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Determines whether completed items auto-archive or stay visible.",
            depends_on=["wf-001-workflow"],
            bdd_template=BddClause(
                given="items are marked complete",
                when="the view is refreshed or 24 hours pass",
                then="move completed items to a collapsible archive section",
                unless="user toggles Show Completed"
            ),
            presets=[
                BddPreset(
                    id="p_auto_archive",
                    label="📦 Clean Archive (Hide Completed)",
                    bdd=BddClause(
                        given="items are marked complete",
                        when="the view is refreshed or 24 hours pass",
                        then="move completed items to a collapsible archive section",
                        unless="user toggles Show Completed"
                    ),
                    description="Keeps daily workspace tidy and focused."
                ),
                BddPreset(
                    id="p_always_visible",
                    label="👁️ Always Visible with Strikethrough",
                    bdd=BddClause(
                        given=f"a {noun.lower()} is completed",
                        when="viewing the list",
                        then="keep it visible on the list with a checkmark and strike-through text",
                        unless=None
                    ),
                    description="Celebrate progress by seeing everything done today."
                )
            ]
        )

        # Fog 5: Inline Editing & Safety
        t5 = WayfinderTicket(
            id="wf-005-editing",
            title="Inline Editing & Undo Protection",
            ticket_type=WayfinderTicketType.GRILL.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Defines how items are edited and protected against accidental deletion.",
            depends_on=["wf-002-organization"],
            bdd_template=BddClause(
                given=f"a {noun.lower()} title needs adjusting",
                when="user clicks on the title",
                then="let them edit text inline, with an Undo banner if deleted by mistake",
                unless=None
            ),
            presets=[
                BddPreset(
                    id="p_inline_undo",
                    label="✏️ Instant Inline Editing with Undo Safety",
                    bdd=BddClause(
                        given=f"a {noun.lower()} title needs adjusting",
                        when="user clicks on the title",
                        then="let them edit text inline, with an Undo banner if deleted by mistake",
                        unless=None
                    ),
                    description="Fast frictionless typing with an undo safety net."
                ),
                BddPreset(
                    id="p_modal_details",
                    label="📝 Detailed Drawer for Notes & Context",
                    bdd=BddClause(
                        given=f"user taps a {noun.lower()}",
                        when="detail pane opens",
                        then="allow adding longer descriptions, notes, and attachments",
                        unless=None
                    ),
                    description="Rich notes and context for each item."
                )
            ]
        )

        # Fog 6: Activity History
        t6 = WayfinderTicket(
            id="wf-006-activity",
            title="Recent Activity & Change History",
            ticket_type=WayfinderTicketType.TASK.value,
            status=WayfinderTicketStatus.FOG.value,
            target_aggregate=noun,
            rationale="Configures whether changes are logged for review.",
            depends_on=["wf-003-deadlines"],
            bdd_template=BddClause(
                given=f"a {noun.lower()} is added, completed, or renamed",
                when="the change occurs",
                then="record a quick timestamped log entry so users can review what changed",
                unless=None
            ),
            presets=[
                BddPreset(
                    id="p_activity_log",
                    label="📜 Recent Changes Activity Log",
                    bdd=BddClause(
                        given=f"a {noun.lower()} is added, completed, or renamed",
                        when="the change occurs",
                        then="record a quick timestamped log entry so users can review what changed",
                        unless=None
                    ),
                    description="Clear audit history of all project changes."
                ),
                BddPreset(
                    id="p_silent_fast",
                    label="⚡ Silent Fast Updates (No Logging)",
                    bdd=BddClause(
                        given=f"a {noun.lower()} is modified",
                        when="changes are saved",
                        then="update immediately without keeping a changelog",
                        unless=None
                    ),
                    description="Lightweight, minimal overhead."
                )
            ]
        )

    tickets = [t1, t2, t3, t4, t5, t6]
    return WayfinderGraphState(
        pitch=pitch,
        brand_name=brand,
        tickets=tickets,
        progress_pct=0,
        is_synthesis_ready=False
    )


def lock_wayfinder_ticket(
    graph: WayfinderGraphState,
    ticket_id: str,
    resolved_bdd: BddClause
) -> WayfinderGraphState:
    """
    Locks a ticket with its finalized BDD clause and recomputes the DAG:
    1. Sets target ticket status to LOCKED with resolved_bdd.
    2. Any ticket in FOG whose dependencies are now all LOCKED moves to FRONTIER!
    3. Recalculates progress percentage and synthesis readiness.
    """
    target = next((t for t in graph.tickets if t.id == ticket_id), None)
    if not target:
        raise ValueError(f"Ticket '{ticket_id}' not found in Wayfinder graph.")

    target.status = WayfinderTicketStatus.LOCKED.value
    target.resolved_bdd = resolved_bdd

    # Identify all locked ticket IDs
    locked_ids = {t.id for t in graph.tickets if t.status == WayfinderTicketStatus.LOCKED.value}

    # Evaluate FOG tickets to see if they can now advance to FRONTIER
    for t in graph.tickets:
        if t.status == WayfinderTicketStatus.FOG.value:
            if all(dep in locked_ids for dep in t.depends_on):
                t.status = WayfinderTicketStatus.FRONTIER.value

    # Update metrics
    total_count = len(graph.tickets)
    locked_count = len(locked_ids)
    graph.progress_pct = int((locked_count / total_count) * 100) if total_count > 0 else 100
    graph.is_synthesis_ready = locked_count >= 2

    return graph


def sync_locked_tickets_to_rule_deck(graph: WayfinderGraphState, uow: Any) -> int:
    """
    Translates all locked Wayfinder tickets directly into active RuleCard entities
    in the Living Deck, ensuring zero translation loss between the UI and TDD machine.
    """
    from domain.model import RuleCard
    from service_layer import services

    locked_tickets = graph.get_locked_tickets()
    synced_count = 0

    for t in locked_tickets:
        bdd = t.resolved_bdd or t.bdd_template
        if not bdd:
            continue

        card_type_str = "VIEW" if t.ticket_type == WayfinderTicketType.PROTOTYPE.value else "LOGIC"

        card = RuleCard(
            id=f"rule-{t.id}",
            title=t.title,
            card_type=card_type_str,
            target=t.target_aggregate,
            given_clause=bdd.given,
            when_clause=bdd.when,
            then_clause=bdd.then,
            unless_clause=bdd.unless or "",
            is_active=True
        )
        services.add_rule_card(card, uow)
        synced_count += 1

    return synced_count
