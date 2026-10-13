"""
Fact Generator — converts applicant data into working-memory facts
for the Forward Chaining engine, including derived financial values.
"""

from typing import Any, Optional

from app.config import get_settings
from app.utils.finance import (
    calculate_dti,
    calculate_emi,
    estimate_max_affordable_loan,
    recommend_loan_range,
)

settings = get_settings()

# Required fields for a complete assessment
REQUIRED_FIELDS = [
    "age",
    "monthly_income",
    "monthly_expenses",
    "existing_emi",
    "credit_score",
    "employment_type",
    "employment_duration",
    "repayment_history",
    "loan_type",
    "requested_amount",
    "tenure_months",
]


def check_missing_fields(data: dict[str, Any]) -> list[str]:
    """Return list of human-readable names for missing required fields."""
    label_map = {
        "age": "Age",
        "monthly_income": "Monthly Income",
        "monthly_expenses": "Monthly Expenses",
        "existing_emi": "Existing Monthly EMI",
        "credit_score": "Credit Score",
        "employment_type": "Employment Type",
        "employment_duration": "Employment Duration",
        "repayment_history": "Previous Loan Repayment History",
        "loan_type": "Loan Type",
        "requested_amount": "Requested Loan Amount",
        "tenure_months": "Loan Tenure",
    }
    missing = []
    for field in REQUIRED_FIELDS:
        value = data.get(field)
        if value is None or value == "":
            missing.append(label_map.get(field, field))
    return missing


def get_interest_rate(data: dict[str, Any]) -> float:
    """Resolve interest rate from data or demo defaults by loan type."""
    if data.get("interest_rate"):
        return float(data["interest_rate"])
    loan_type = data.get("loan_type", "Personal Loan")
    return float(settings.default_interest_rates.get(loan_type, 12.0))


def generate_facts(applicant_data: dict[str, Any]) -> dict[str, Any]:
    """
    Build the initial fact set (working memory) for Forward Chaining.

    Steps:
    1. Copy raw applicant fields.
    2. Calculate EMI, DTI, affordability thresholds.
    3. Add helper thresholds used by dynamic rules.
    """
    interest_rate = get_interest_rate(applicant_data)
    tenure = int(applicant_data.get("tenure_months", 12))
    principal = float(applicant_data.get("requested_amount", 0))
    income = float(applicant_data.get("monthly_income", 0))
    existing_emi = float(applicant_data.get("existing_emi", 0))

    new_emi = calculate_emi(principal, interest_rate, tenure)
    dti = calculate_dti(existing_emi, new_emi, income)
    max_affordable = estimate_max_affordable_loan(
        income, existing_emi, interest_rate, tenure, max_dti_percent=40.0
    )

    # Demo thresholds relative to income (used by high-loan / high-EMI rules)
    high_loan_threshold = income * 60  # ~5 years of income
    high_emi_threshold = income * 0.5  # 50% of income as EMI

    facts: dict[str, Any] = {
        # Raw facts
        "age": int(applicant_data.get("age", 0)),
        "gender": applicant_data.get("gender"),
        "employment_type": applicant_data.get("employment_type"),
        "monthly_income": income,
        "monthly_expenses": float(applicant_data.get("monthly_expenses", 0)),
        "existing_emi": existing_emi,
        "credit_score": int(applicant_data.get("credit_score", 0)),
        "employment_duration": int(applicant_data.get("employment_duration", 0)),
        "repayment_history": applicant_data.get("repayment_history"),
        "loan_type": applicant_data.get("loan_type"),
        "requested_amount": principal,
        "tenure_months": tenure,
        "purpose": applicant_data.get("purpose", ""),
        "interest_rate": interest_rate,
        # Derived financial facts
        "estimated_new_emi": new_emi,
        "debt_to_income_ratio": dti,
        "max_affordable": max_affordable,
        # Dynamic thresholds for cross-field rules
        "high_loan_threshold": high_loan_threshold,
        "high_emi_threshold": high_emi_threshold,
    }

    return facts


def build_financial_summary(facts: dict[str, Any]) -> dict[str, Any]:
    """Create a financial summary dict for API/report responses."""
    recommendation = recommend_loan_range(
        monthly_income=facts["monthly_income"],
        existing_emi=facts["existing_emi"],
        credit_score=facts["credit_score"],
        annual_rate=facts["interest_rate"],
        tenure_months=facts["tenure_months"],
    )
    return {
        "monthly_income": facts["monthly_income"],
        "monthly_expenses": facts["monthly_expenses"],
        "existing_emi": facts["existing_emi"],
        "estimated_new_emi": facts["estimated_new_emi"],
        "debt_to_income_ratio": facts["debt_to_income_ratio"],
        "credit_score": facts["credit_score"],
        "interest_rate": facts["interest_rate"],
        "requested_amount": facts["requested_amount"],
        "max_affordable": facts["max_affordable"],
        "loan_recommendation": recommendation,
    }
