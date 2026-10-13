"""
Rule-based Risk Analysis module.

Produces LOW / MEDIUM / HIGH risk levels with explanatory factors.
This is NOT a real banking risk score — demo only.
"""

from typing import Any


def analyze_risk(
    decision: str,
    derived_facts: list[str],
    financial_summary: dict[str, Any],
) -> dict[str, Any]:
    """
    Determine risk level from derived facts and financial metrics.

    Returns: { risk_level, risk_factors, disclaimer }
    """
    facts = set(derived_facts)
    factors: list[str] = []
    score = 0  # internal demo score; higher = riskier

    dti = financial_summary.get("debt_to_income_ratio", 0)
    credit = financial_summary.get("credit_score", 700)
    requested = financial_summary.get("requested_amount", 0)
    max_aff = financial_summary.get("max_affordable", 1) or 1

    # Fact-based scoring
    if "poor_credit_score" in facts:
        score += 40
        factors.append("Poor demo credit score")
    if "high_debt_ratio" in facts:
        score += 35
        factors.append("Debt ratio exceeds the high-risk demo threshold")
    if "high_risk_combination" in facts:
        score += 30
        factors.append("High-risk combination of poor credit and high debt")
    if "unemployed_applicant" in facts:
        score += 40
        factors.append("Applicant is unemployed")
    if "poor_repayment_history" in facts:
        score += 25
        factors.append("Poor previous loan repayment history")
    if "low_income" in facts:
        score += 20
        factors.append("Income below demo minimum threshold")
    if "high_loan_amount" in facts:
        score += 15
        factors.append("Requested loan amount is relatively high")
    if "high_emi_burden" in facts:
        score += 15
        factors.append("Estimated EMI is high relative to income")
    if "borderline_credit_score" in facts:
        score += 15
        factors.append("Credit score is in the borderline range")
    if "borderline_dti" in facts:
        score += 15
        factors.append("Debt ratio is close to the threshold")
    if "average_repayment_history" in facts:
        score += 10
        factors.append("Average repayment history")

    # Metric-based nudges
    if dti > 45 and "Debt ratio" not in " ".join(factors):
        score += 10
        factors.append(f"DTI is elevated at {dti}%")
    if credit < 650 and "credit" not in " ".join(factors).lower():
        score += 10
        factors.append(f"Demo credit score ({credit}) is below preferred range")
    if requested > max_aff * 1.2:
        score += 10
        if "Requested loan amount is relatively high" not in factors:
            factors.append("Requested loan amount exceeds estimated affordable range")

    # Positive mitigators
    if "low_risk_profile" in facts:
        score = max(0, score - 25)
    if "excellent_credit_score" in facts:
        score = max(0, score - 10)

    if score >= 50:
        level = "HIGH"
    elif score >= 20:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Align with decision when clearly negative
    if decision == "NOT_ELIGIBLE" and level == "LOW":
        level = "HIGH"
        if not factors:
            factors.append("Application marked not eligible by Forward Chaining rules")
    if decision == "MANUAL_REVIEW" and level == "LOW":
        level = "MEDIUM"
        if not factors:
            factors.append("Application flagged for manual review")

    if not factors:
        factors.append("No significant risk factors identified under demo rules")

    return {
        "risk_level": level,
        "risk_factors": factors,
        "disclaimer": (
            "This is a DEMO rule-based risk analysis. "
            "It is NOT a real banking risk score."
        ),
    }
