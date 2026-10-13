"""Financial calculation helpers: EMI, DTI, loan affordability."""

from math import pow


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate Equated Monthly Installment (EMI).

    Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    where r = monthly interest rate, n = tenure in months.
    """
    if principal <= 0 or tenure_months <= 0:
        return 0.0
    if annual_rate <= 0:
        return round(principal / tenure_months, 2)

    monthly_rate = annual_rate / (12 * 100)
    factor = pow(1 + monthly_rate, tenure_months)
    emi = principal * monthly_rate * factor / (factor - 1)
    return round(emi, 2)


def calculate_total_interest(emi: float, tenure_months: int, principal: float) -> float:
    """Total interest payable over the loan tenure."""
    return round((emi * tenure_months) - principal, 2)


def calculate_total_repayment(emi: float, tenure_months: int) -> float:
    """Total amount repaid (principal + interest)."""
    return round(emi * tenure_months, 2)


def calculate_dti(
    existing_emi: float, new_emi: float, monthly_income: float
) -> float:
    """
    Debt-to-Income ratio (%) =
    (Existing EMI + Estimated New EMI) / Monthly Income × 100
    """
    if monthly_income <= 0:
        return 100.0
    dti = ((existing_emi + new_emi) / monthly_income) * 100
    return round(dti, 2)


def estimate_max_affordable_loan(
    monthly_income: float,
    existing_emi: float,
    annual_rate: float,
    tenure_months: int,
    max_dti_percent: float = 40.0,
) -> float:
    """
    Estimate maximum affordable loan amount based on demo DTI threshold.

    Available EMI budget = (max_dti% of income) - existing EMI
    Then reverse-calculate principal from EMI formula.
    """
    if monthly_income <= 0 or tenure_months <= 0:
        return 0.0

    max_total_emi = (max_dti_percent / 100.0) * monthly_income
    available_emi = max_total_emi - existing_emi
    if available_emi <= 0:
        return 0.0

    if annual_rate <= 0:
        return round(available_emi * tenure_months, 2)

    monthly_rate = annual_rate / (12 * 100)
    factor = pow(1 + monthly_rate, tenure_months)
    # EMI = P * r * factor / (factor - 1)  =>  P = EMI * (factor - 1) / (r * factor)
    principal = available_emi * (factor - 1) / (monthly_rate * factor)
    return round(max(0.0, principal), 2)


def recommend_loan_range(
    monthly_income: float,
    existing_emi: float,
    credit_score: int,
    annual_rate: float,
    tenure_months: int,
) -> dict:
    """
    Demo loan amount recommendation based on income, EMI, credit score, tenure.

    Clearly labeled as demo recommendation — NOT financial advice.
    """
    max_affordable = estimate_max_affordable_loan(
        monthly_income, existing_emi, annual_rate, tenure_months, max_dti_percent=40.0
    )

    # Credit score adjusts the recommended range (demo heuristic)
    if credit_score >= 750:
        multiplier = 0.95
    elif credit_score >= 700:
        multiplier = 0.85
    elif credit_score >= 650:
        multiplier = 0.70
    elif credit_score >= 600:
        multiplier = 0.55
    else:
        multiplier = 0.40

    recommended_max = round(max_affordable * multiplier, 2)
    recommended_min = round(recommended_max * 0.75, 2)

    return {
        "recommended_min": recommended_min,
        "recommended_max": recommended_max,
        "estimated_maximum_affordable": max_affordable,
        "disclaimer": (
            "This is a DEMO recommendation based on sample DTI thresholds. "
            "It is NOT financial advice and does not represent real bank underwriting."
        ),
    }
