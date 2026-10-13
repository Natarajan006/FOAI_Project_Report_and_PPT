"""
Explainable AI module — converts Forward Chaining results into
human-readable explanations, reasons, and improvement suggestions.
"""

from typing import Any


REASON_LABELS = {
    "age_requirement_satisfied": "Age requirement satisfied",
    "age_limit_satisfied": "Age limit satisfied",
    "income_requirement_satisfied": "Income requirement satisfied",
    "good_credit_score": "Credit requirement satisfied (good score)",
    "excellent_credit_score": "Excellent credit score",
    "stable_employment": "Employment requirement satisfied (salaried)",
    "employment_stability_satisfied": "Employment duration requirement satisfied",
    "self_employed_stability_satisfied": "Self-employed stability satisfied",
    "debt_ratio_acceptable": "Debt ratio acceptable",
    "repayment_history_satisfied": "Repayment history acceptable",
    "positive_cash_flow": "Positive cash flow",
    "loan_affordability_satisfied": "Loan affordability satisfied",
    "core_eligibility_met": "Core eligibility criteria met",
    "low_risk_profile": "Low risk profile",
    "poor_credit_score": "Poor credit score",
    "high_debt_ratio": "High debt-to-income ratio",
    "low_income": "Income below minimum threshold",
    "high_loan_amount": "Requested loan amount is high",
    "high_emi_burden": "Estimated EMI burden is high",
    "poor_repayment_history": "Poor repayment history",
    "unemployed_applicant": "Applicant is unemployed",
    "high_risk_combination": "High-risk combination of factors",
    "borderline_credit_score": "Borderline credit score",
    "borderline_dti": "Borderline debt-to-income ratio",
    "requires_manual_review": "Manual review required",
    "average_repayment_history": "Average repayment history",
}


POSITIVE_FACTS = {
    "age_requirement_satisfied",
    "age_limit_satisfied",
    "income_requirement_satisfied",
    "good_credit_score",
    "excellent_credit_score",
    "stable_employment",
    "employment_stability_satisfied",
    "self_employed_stability_satisfied",
    "debt_ratio_acceptable",
    "repayment_history_satisfied",
    "positive_cash_flow",
    "loan_affordability_satisfied",
    "core_eligibility_met",
    "low_risk_profile",
}

NEGATIVE_FACTS = {
    "poor_credit_score",
    "high_debt_ratio",
    "low_income",
    "high_loan_amount",
    "high_emi_burden",
    "poor_repayment_history",
    "unemployed_applicant",
    "high_risk_combination",
}


def build_reasons(derived_facts: list[str], decision: str) -> list[str]:
    """Build checkmark-style reason list for the UI."""
    reasons = []
    for fact in derived_facts:
        if fact.startswith("final_"):
            continue
        label = REASON_LABELS.get(fact, fact.replace("_", " ").title())
        if fact in POSITIVE_FACTS:
            reasons.append(f"✓ {label}")
        elif fact in NEGATIVE_FACTS:
            reasons.append(f"✗ {label}")
        else:
            reasons.append(f"• {label}")
    return reasons


def generate_explanation(
    decision: str,
    triggered_rules: list[dict[str, Any]],
    derived_facts: list[str],
    financial_summary: dict[str, Any],
) -> str:
    """Generate a human-readable narrative explanation of the decision."""
    dti = financial_summary.get("debt_to_income_ratio", 0)
    credit = financial_summary.get("credit_score", 0)
    income = financial_summary.get("monthly_income", 0)
    emi = financial_summary.get("estimated_new_emi", 0)

    rule_ids = [r["rule_id"] for r in triggered_rules]

    intro = {
        "ELIGIBLE": (
            "Based on the Forward Chaining inference over the demo knowledge base, "
            "the applicant meets the core eligibility criteria."
        ),
        "NOT_ELIGIBLE": (
            "Based on the Forward Chaining inference over the demo knowledge base, "
            "the applicant does not meet one or more critical eligibility criteria."
        ),
        "MANUAL_REVIEW": (
            "Based on the Forward Chaining inference, the application has borderline "
            "or conflicting indicators and requires manual review by an administrator."
        ),
    }.get(decision, "Assessment completed.")

    details = (
        f" Demo credit score: {credit}. "
        f"Monthly income: ₹{income:,.2f}. "
        f"Estimated new EMI: ₹{emi:,.2f}. "
        f"Debt-to-Income (DTI) ratio: {dti}%. "
        f"Rules fired: {', '.join(rule_ids) if rule_ids else 'none'}."
    )

    disclaimer = (
        " NOTE: This is a DEMO assessment using sample rules and thresholds. "
        "It does not constitute real bank underwriting or financial advice."
    )

    return intro + details + disclaimer


def generate_suggestions(
    decision: str,
    derived_facts: list[str],
    financial_summary: dict[str, Any],
) -> list[str]:
    """Suggest possible improvements based on which negative facts fired."""
    suggestions: list[str] = []
    facts_set = set(derived_facts)
    rec = financial_summary.get("loan_recommendation", {})

    if "poor_credit_score" in facts_set or "borderline_credit_score" in facts_set:
        suggestions.append(
            "Improve your demo credit score (e.g., toward 700+) and re-run the assessment."
        )
    if "high_debt_ratio" in facts_set or "borderline_dti" in facts_set:
        suggestions.append(
            "Reduce existing EMI obligations or request a smaller loan amount to lower DTI below 40%."
        )
    if "high_loan_amount" in facts_set or "loan_affordability_satisfied" not in facts_set:
        max_amt = rec.get("recommended_max") or financial_summary.get("max_affordable", 0)
        suggestions.append(
            f"Consider reducing the requested amount. Demo recommended max: ₹{max_amt:,.2f}."
        )
    if "low_income" in facts_set:
        suggestions.append(
            "Increase documented monthly income or apply with a co-applicant (demo suggestion)."
        )
    if "high_emi_burden" in facts_set:
        suggestions.append(
            "Increase loan tenure or reduce principal to lower the estimated EMI."
        )
    if "poor_repayment_history" in facts_set:
        suggestions.append(
            "Improve repayment history before reapplying."
        )
    if "unemployed_applicant" in facts_set:
        suggestions.append(
            "Secure stable employment before applying for a loan."
        )
    if decision == "ELIGIBLE":
        suggestions.append(
            "You may proceed with the application. Keep documents ready for verification."
        )
    if decision == "MANUAL_REVIEW":
        suggestions.append(
            "An administrator will review your application. You may also try the What-If Simulator."
        )
    if not suggestions:
        suggestions.append(
            "Review your financial details and try the What-If Simulator to explore alternatives."
        )

    suggestions.append(
        "Disclaimer: Suggestions are demo-only and not financial advice."
    )
    return suggestions


def compare_assessments(
    before: dict[str, Any], after: dict[str, Any], changes: dict[str, Any]
) -> dict[str, Any]:
    """
    Compare two FC results for the What-If Simulator.
    Identifies which rules changed and explains the shift.
    """
    before_rules = {r["rule_id"] for r in before.get("triggered_rules", [])}
    after_rules = {r["rule_id"] for r in after.get("triggered_rules", [])}

    newly_fired = sorted(after_rules - before_rules)
    no_longer_fired = sorted(before_rules - after_rules)

    change_lines = []
    for key, vals in changes.items():
        if isinstance(vals, dict) and "from" in vals and "to" in vals:
            change_lines.append(f"{key}: {vals['from']} → {vals['to']}")

    reason_parts = []
    if newly_fired:
        reason_parts.append(f"Newly fired rules: {', '.join(newly_fired)}")
    if no_longer_fired:
        reason_parts.append(f"Rules no longer fired: {', '.join(no_longer_fired)}")

    # Heuristic narrative
    narrative = "Parameter changes altered which Forward Chaining rules were satisfied."
    if before.get("decision") != after.get("decision"):
        narrative = (
            f"Result changed from {before.get('decision')} to {after.get('decision')}. "
        )
        if "debt_to_income_ratio" in str(changes) or any(
            "amount" in k.lower() or "emi" in k.lower() or "tenure" in k.lower()
            for k in changes
        ):
            narrative += (
                "Estimated EMI and/or debt-to-income ratio crossed a demo threshold, "
                "changing eligibility-related rules."
            )

    return {
        "before_decision": before.get("decision"),
        "after_decision": after.get("decision"),
        "parameter_changes": change_lines,
        "newly_fired_rules": newly_fired,
        "no_longer_fired_rules": no_longer_fired,
        "reason": narrative + (" " + "; ".join(reason_parts) if reason_parts else ""),
    }
