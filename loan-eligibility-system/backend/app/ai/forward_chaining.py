"""
Forward Chaining Inference Engine
==================================
This is the AUTHORITATIVE decision component for loan eligibility.

Algorithm:
1. Receive applicant facts (working memory).
2. Load rules from the knowledge base.
3. Evaluate rules against current facts.
4. Fire satisfied rules (add conclusions as derived facts).
5. Continue until no new facts can be derived (fixed point).
6. Determine final eligibility from derived decision facts.
7. Record every rule that fired.
8. Return explanation-ready results.

Do NOT hard-code one giant if/else. Rules are modular and data-driven.
"""

from copy import deepcopy
from typing import Any, Optional


class ForwardChainingEngine:
    """
    Classic data-driven forward chaining (modus ponens style).

    Working Memory (facts) starts with applicant data.
    Rules whose conditions are all true are "fired", and their
    conclusions are asserted into working memory.
    Iteration continues until quiescence (no new facts).
    """

    def __init__(self, rules: list[dict[str, Any]], max_iterations: int = 50):
        self.rules = sorted(rules, key=lambda r: r.get("priority", 1))
        self.max_iterations = max_iterations
        self.fired_rules: list[dict[str, Any]] = []
        self.derived_facts: list[str] = []
        self.facts: dict[str, Any] = {}
        self.trace: list[str] = []  # step-by-step for viva/demo

    def _resolve_value(self, value: Any) -> Any:
        """
        Resolve special placeholder references like __monthly_income__
        to the corresponding fact value. Enables cross-field comparisons.
        """
        if isinstance(value, str) and value.startswith("__") and value.endswith("__"):
            field_name = value[2:-2]
            return self.facts.get(field_name)
        return value

    def _evaluate_condition(self, condition: dict[str, Any]) -> bool:
        """Evaluate a single condition against working memory."""
        field = condition["field"]
        operator = condition["operator"]
        expected = self._resolve_value(condition["value"])

        # If the field is not in facts yet, treat boolean conclusions carefully
        if field not in self.facts:
            # For != True checks on missing derived facts, treat as True (fact not set)
            if operator == "!=" and expected is True:
                return True
            if operator == "==" and expected is False:
                return True
            return False

        actual = self.facts[field]

        try:
            if operator == ">=":
                return actual >= expected
            if operator == "<=":
                return actual <= expected
            if operator == ">":
                return actual > expected
            if operator == "<":
                return actual < expected
            if operator == "==":
                return actual == expected
            if operator == "!=":
                return actual != expected
            if operator == "in":
                return actual in (expected if isinstance(expected, (list, tuple, set)) else [expected])
            if operator == "not_in":
                return actual not in (expected if isinstance(expected, (list, tuple, set)) else [expected])
        except TypeError:
            # Incomparable types — condition fails safely
            return False

        return False

    def _rule_satisfied(self, rule: dict[str, Any]) -> bool:
        """A rule is satisfied when ALL its conditions are true (AND logic)."""
        return all(self._evaluate_condition(c) for c in rule["conditions"])

    def _fire_rule(self, rule: dict[str, Any]) -> bool:
        """
        Fire a rule: assert its conclusion into working memory.
        Returns True if a NEW fact was added.
        """
        conclusion = rule["conclusion"]
        already_known = self.facts.get(conclusion) is True

        if already_known:
            return False

        self.facts[conclusion] = True
        self.derived_facts.append(conclusion)
        self.fired_rules.append(
            {
                "rule_id": rule["rule_id"],
                "name": rule["name"],
                "conclusion": conclusion,
                "explanation": rule["explanation"],
                "priority": rule.get("priority", 1),
                "category": rule.get("category", "general"),
            }
        )
        self.trace.append(
            f"FIRED {rule['rule_id']} ({rule['name']}) → {conclusion}"
        )
        return True

    def run(self, initial_facts: dict[str, Any]) -> dict[str, Any]:
        """
        Execute forward chaining until no new facts can be derived.

        Returns a result dictionary with decision, fired rules, facts, etc.
        """
        self.facts = deepcopy(initial_facts)
        self.fired_rules = []
        self.derived_facts = []
        self.trace = ["=== Forward Chaining Started ==="]

        # Track which rules have already been fired to avoid re-firing
        fired_ids: set[str] = set()

        for iteration in range(1, self.max_iterations + 1):
            self.trace.append(f"--- Iteration {iteration} ---")
            new_fact_added = False

            for rule in self.rules:
                if not rule.get("enabled", True):
                    continue
                rid = rule["rule_id"]
                # Allow same rule_id conclusions from different rules, but
                # don't re-fire the exact same rule instance
                rule_key = f"{rid}:{rule['conclusion']}"
                if rule_key in fired_ids:
                    continue

                if self._rule_satisfied(rule):
                    if self._fire_rule(rule):
                        fired_ids.add(rule_key)
                        new_fact_added = True
                    else:
                        fired_ids.add(rule_key)

            if not new_fact_added:
                self.trace.append("Quiescence reached — no new facts derived.")
                break
        else:
            self.trace.append("Max iterations reached.")

        decision = self._determine_decision()
        self.trace.append(f"=== Final Decision: {decision} ===")

        return {
            "decision": decision,
            "triggered_rules": self.fired_rules,
            "derived_facts": self.derived_facts,
            "facts": self.facts,
            "trace": self.trace,
        }

    def _determine_decision(self) -> str:
        """
        Map derived decision facts to ELIGIBLE / NOT_ELIGIBLE / MANUAL_REVIEW.

        Priority: NOT_ELIGIBLE > MANUAL_REVIEW > ELIGIBLE > default MANUAL_REVIEW
        (conservative default when core rules don't clearly decide).
        """
        if self.facts.get("final_not_eligible"):
            return "NOT_ELIGIBLE"
        if self.facts.get("final_manual_review"):
            return "MANUAL_REVIEW"
        if self.facts.get("final_eligible"):
            return "ELIGIBLE"

        # Fallback heuristics if decision rules didn't fire
        if self.facts.get("high_risk_combination") or self.facts.get("poor_credit_score"):
            return "NOT_ELIGIBLE"
        if self.facts.get("requires_manual_review") or self.facts.get("borderline_dti"):
            return "MANUAL_REVIEW"
        if self.facts.get("core_eligibility_met"):
            return "ELIGIBLE"

        # Insufficient positive evidence → manual review (safe default for demo)
        return "MANUAL_REVIEW"


def run_forward_chaining(
    facts: dict[str, Any], rules: list[dict[str, Any]]
) -> dict[str, Any]:
    """Convenience wrapper to run the forward chaining engine."""
    engine = ForwardChainingEngine(rules)
    return engine.run(facts)
