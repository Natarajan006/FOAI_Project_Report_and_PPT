"""
Knowledge Base manager — loads, validates, and supplies rules
to the Forward Chaining inference engine.
"""

from copy import deepcopy
from typing import Any, Optional

from app.ai.rules import SAMPLE_RULES
from app.database import get_db

ALLOWED_OPERATORS = {">=", "<=", ">", "<", "==", "!=", "in", "not_in"}


def validate_rule(rule: dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a rule structure so invalid rules cannot crash the inference engine.
    Returns (is_valid, error_message).
    """
    required = ["rule_id", "name", "conditions", "conclusion", "priority", "explanation"]
    for key in required:
        if key not in rule:
            return False, f"Missing required field: {key}"

    if not isinstance(rule["conditions"], list) or len(rule["conditions"]) == 0:
        return False, "Rule must have at least one condition"

    for cond in rule["conditions"]:
        if not isinstance(cond, dict):
            return False, "Each condition must be a dictionary"
        if "field" not in cond or "operator" not in cond or "value" not in cond:
            return False, "Condition must have field, operator, and value"
        if cond["operator"] not in ALLOWED_OPERATORS:
            return False, f"Invalid operator: {cond['operator']}"

    if not isinstance(rule["priority"], int) or rule["priority"] < 1:
        return False, "Priority must be a positive integer"

    return True, ""


class KnowledgeBase:
    """
    Manages the rule set used by Forward Chaining.

    Rules can be loaded from MongoDB (admin-managed) or fall back
    to the in-code SAMPLE_RULES for demo/offline use.
    """

    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []

    async def load_from_db(self) -> list[dict[str, Any]]:
        """Load enabled rules from MongoDB, sorted by priority."""
        db = get_db()
        cursor = db.rules.find({"enabled": True}).sort("priority", 1)
        rules = []
        async for doc in cursor:
            rule = {
                "rule_id": doc["rule_id"],
                "name": doc["name"],
                "conditions": doc["conditions"],
                "conclusion": doc["conclusion"],
                "priority": doc["priority"],
                "explanation": doc["explanation"],
                "enabled": doc.get("enabled", True),
                "category": doc.get("category", "general"),
            }
            valid, _ = validate_rule(rule)
            if valid:
                rules.append(rule)
        self._rules = rules
        return rules

    def load_sample_rules(self) -> list[dict[str, Any]]:
        """Load built-in sample rules (used for seeding and tests)."""
        self._rules = deepcopy(SAMPLE_RULES)
        return self._rules

    def get_rules(self) -> list[dict[str, Any]]:
        """Return currently loaded rules."""
        return self._rules

    def get_rule_by_id(self, rule_id: str) -> Optional[dict[str, Any]]:
        """Find a single rule by its ID."""
        for rule in self._rules:
            if rule["rule_id"] == rule_id:
                return rule
        return None


async def get_active_rules() -> list[dict[str, Any]]:
    """
    Convenience: load rules from DB; if empty, use sample rules.
    """
    kb = KnowledgeBase()
    try:
        rules = await kb.load_from_db()
        if rules:
            return rules
    except Exception:
        pass
    return kb.load_sample_rules()
