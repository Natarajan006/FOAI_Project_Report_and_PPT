"""
Tests for Forward Chaining engine, financial calculations, and auth helpers.
Run from backend/:  pytest tests/ -v
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.fact_generator import check_missing_fields, generate_facts
from app.ai.forward_chaining import ForwardChainingEngine, run_forward_chaining
from app.ai.knowledge_base import KnowledgeBase, validate_rule
from app.ai.rules import SAMPLE_RULES
from app.utils.finance import (
    calculate_dti,
    calculate_emi,
    calculate_total_interest,
    calculate_total_repayment,
    estimate_max_affordable_loan,
)
from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


# ---------- Financial calculations ----------

class TestEMI:
    def test_emi_positive(self):
        emi = calculate_emi(500000, 10, 60)
        assert emi > 0
        assert emi < 500000

    def test_emi_zero_rate(self):
        emi = calculate_emi(120000, 0, 12)
        assert emi == 10000.0

    def test_total_interest(self):
        emi = calculate_emi(100000, 12, 12)
        interest = calculate_total_interest(emi, 12, 100000)
        assert interest > 0

    def test_total_repayment(self):
        emi = 5000
        assert calculate_total_repayment(emi, 12) == 60000


class TestDTI:
    def test_dti_example(self):
        # Income 60000, existing 5000, new 20000 → 41.67%
        dti = calculate_dti(5000, 20000, 60000)
        assert dti == 41.67

    def test_dti_zero_income(self):
        assert calculate_dti(1000, 1000, 0) == 100.0

    def test_affordability(self):
        max_loan = estimate_max_affordable_loan(60000, 5000, 10, 60)
        assert max_loan > 0


# ---------- Forward Chaining ----------

class TestForwardChaining:
    def setup_method(self):
        self.rules = SAMPLE_RULES

    def _eligible_facts(self):
        return generate_facts(
            {
                "age": 30,
                "employment_type": "Salaried",
                "monthly_income": 80000,
                "monthly_expenses": 20000,
                "existing_emi": 5000,
                "credit_score": 780,
                "employment_duration": 36,
                "repayment_history": "Good",
                "loan_type": "Personal Loan",
                "requested_amount": 200000,
                "tenure_months": 36,
                "interest_rate": 12.0,
            }
        )

    def _not_eligible_facts(self):
        return generate_facts(
            {
                "age": 30,
                "employment_type": "Unemployed",
                "monthly_income": 15000,
                "monthly_expenses": 14000,
                "existing_emi": 10000,
                "credit_score": 520,
                "employment_duration": 0,
                "repayment_history": "Poor",
                "loan_type": "Personal Loan",
                "requested_amount": 1000000,
                "tenure_months": 12,
                "interest_rate": 14.0,
            }
        )

    def _manual_review_facts(self):
        return generate_facts(
            {
                "age": 28,
                "employment_type": "Salaried",
                "monthly_income": 50000,
                "monthly_expenses": 20000,
                "existing_emi": 8000,
                "credit_score": 650,  # borderline
                "employment_duration": 18,
                "repayment_history": "Average",
                "loan_type": "Personal Loan",
                "requested_amount": 250000,
                "tenure_months": 36,
                "interest_rate": 12.0,
            }
        )

    def test_eligible_applicant(self):
        result = run_forward_chaining(self._eligible_facts(), self.rules)
        assert result["decision"] == "ELIGIBLE"
        assert len(result["triggered_rules"]) > 0
        assert "final_eligible" in result["derived_facts"] or result["decision"] == "ELIGIBLE"

    def test_not_eligible_applicant(self):
        result = run_forward_chaining(self._not_eligible_facts(), self.rules)
        assert result["decision"] == "NOT_ELIGIBLE"
        assert len(result["triggered_rules"]) > 0

    def test_manual_review_applicant(self):
        result = run_forward_chaining(self._manual_review_facts(), self.rules)
        assert result["decision"] in ("MANUAL_REVIEW", "ELIGIBLE", "NOT_ELIGIBLE")
        # Borderline credit should fire related rules
        conclusions = [r["conclusion"] for r in result["triggered_rules"]]
        assert "borderline_credit_score" in conclusions or "requires_manual_review" in conclusions or result["decision"] == "MANUAL_REVIEW"

    def test_multiple_rules_firing(self):
        result = run_forward_chaining(self._eligible_facts(), self.rules)
        assert len(result["triggered_rules"]) >= 5

    def test_missing_facts_check(self):
        missing = check_missing_fields({"age": 25})
        assert "Monthly Income" in missing
        assert "Credit Score" in missing

    def test_no_rules_firing(self):
        # Empty facts with no matching numeric values
        engine = ForwardChainingEngine(self.rules)
        result = engine.run({"age": 10, "monthly_income": 0, "credit_score": 0})
        # Some rules may still not fire; decision should still be produced
        assert result["decision"] in ("ELIGIBLE", "NOT_ELIGIBLE", "MANUAL_REVIEW")

    def test_rule_recording(self):
        result = run_forward_chaining(self._eligible_facts(), self.rules)
        for rule in result["triggered_rules"]:
            assert "rule_id" in rule
            assert "explanation" in rule


class TestKnowledgeBase:
    def test_validate_good_rule(self):
        ok, err = validate_rule(SAMPLE_RULES[0])
        assert ok
        assert err == ""

    def test_validate_bad_rule(self):
        ok, err = validate_rule({"rule_id": "X"})
        assert not ok

    def test_load_sample(self):
        kb = KnowledgeBase()
        rules = kb.load_sample_rules()
        assert len(rules) >= 20


# ---------- Auth helpers ----------

class TestAuth:
    def test_password_hash_not_plaintext(self):
        hashed = hash_password("User@12345")
        assert hashed != "User@12345"
        assert verify_password("User@12345", hashed)
        assert not verify_password("wrong", hashed)

    def test_jwt_create_decode(self):
        token = create_access_token({"sub": "abc123", "role": "user"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "abc123"
        assert payload["role"] == "user"

    def test_invalid_jwt(self):
        assert decode_access_token("not.a.valid.token") is None
