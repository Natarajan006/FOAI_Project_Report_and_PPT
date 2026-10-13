"""Loan application and assessment schemas."""

from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, field_validator


LOAN_TYPES = (
    "Personal Loan",
    "Education Loan",
    "Home Loan",
    "Vehicle Loan",
    "Business Loan",
)

EMPLOYMENT_TYPES = ("Salaried", "Self-Employed", "Business", "Unemployed")
REPAYMENT_HISTORY = ("Good", "Average", "Poor", "None")
DECISIONS = ("ELIGIBLE", "NOT_ELIGIBLE", "MANUAL_REVIEW")
RISK_LEVELS = ("LOW", "MEDIUM", "HIGH")


class LoanApplicationCreate(BaseModel):
    """Multi-step loan application form payload."""

    # Personal
    full_name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=18, le=80)
    gender: Optional[str] = Field(None, max_length=20)
    employment_type: Literal["Salaried", "Self-Employed", "Business", "Unemployed"]

    # Financial
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., ge=0)
    existing_emi: float = Field(..., ge=0)
    credit_score: int = Field(..., ge=300, le=900, description="Demo Credit Score (300-900)")
    employment_duration: int = Field(..., ge=0, description="Months of employment")
    repayment_history: Literal["Good", "Average", "Poor", "None"]

    # Loan
    loan_type: Literal[
        "Personal Loan", "Education Loan", "Home Loan", "Vehicle Loan", "Business Loan"
    ]
    requested_amount: float = Field(..., gt=0)
    tenure_months: int = Field(..., ge=6, le=360)
    purpose: str = Field(..., min_length=3, max_length=500)
    interest_rate: Optional[float] = Field(None, ge=1, le=30)

    @field_validator(
        "monthly_income",
        "monthly_expenses",
        "existing_emi",
        "requested_amount",
    )
    @classmethod
    def no_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Value cannot be negative")
        return v


class LoanApplicationResponse(BaseModel):
    """Loan application response."""

    id: str
    user_id: str
    full_name: str
    age: int
    gender: Optional[str] = None
    employment_type: str
    monthly_income: float
    monthly_expenses: float
    existing_emi: float
    credit_score: int
    employment_duration: int
    repayment_history: str
    loan_type: str
    requested_amount: float
    tenure_months: int
    purpose: str
    interest_rate: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class AssessmentResponse(BaseModel):
    """Full assessment result with explainable AI details."""

    id: str
    application_id: str
    user_id: str
    decision: Literal["ELIGIBLE", "NOT_ELIGIBLE", "MANUAL_REVIEW"]
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    triggered_rules: list[dict[str, Any]]
    derived_facts: list[str]
    explanation: str
    reasons: list[str]
    risk_factors: list[str]
    suggestions: list[str]
    financial_summary: dict[str, Any]
    loan_recommendation: Optional[dict[str, Any]] = None
    missing_fields: Optional[list[str]] = None
    timestamp: datetime
    reviewed: bool = False
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None


class EvaluateRequest(BaseModel):
    """Request to evaluate an existing loan application."""

    application_id: str


class WhatIfRequest(BaseModel):
    """What-If simulator payload — modify parameters and re-run FC engine."""

    application_id: Optional[str] = None
    # Override fields (all optional for simulation)
    monthly_income: Optional[float] = Field(None, gt=0)
    existing_emi: Optional[float] = Field(None, ge=0)
    credit_score: Optional[int] = Field(None, ge=300, le=900)
    requested_amount: Optional[float] = Field(None, gt=0)
    tenure_months: Optional[int] = Field(None, ge=6, le=360)
    interest_rate: Optional[float] = Field(None, ge=1, le=30)
    monthly_expenses: Optional[float] = Field(None, ge=0)
    age: Optional[int] = Field(None, ge=18, le=80)
    employment_type: Optional[str] = None
    employment_duration: Optional[int] = Field(None, ge=0)
    repayment_history: Optional[str] = None
    loan_type: Optional[str] = None
    # Base facts if no application_id
    base_facts: Optional[dict[str, Any]] = None


class AdvisorRequest(BaseModel):
    """AI Loan Advisor chat/query payload."""

    message: str = Field(..., min_length=1, max_length=2000)
    application_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None


class EMIRequest(BaseModel):
    """Standalone EMI calculator input."""

    loan_amount: float = Field(..., gt=0)
    interest_rate: float = Field(..., ge=0.1, le=50)
    tenure_months: int = Field(..., ge=1, le=480)


class EMIResponse(BaseModel):
    """EMI calculation result."""

    emi: float
    total_interest: float
    total_repayment: float
    loan_amount: float
    interest_rate: float
    tenure_months: int


class ReviewRequest(BaseModel):
    """Admin manual review action."""

    notes: Optional[str] = Field(None, max_length=1000)
    decision_override: Optional[Literal["ELIGIBLE", "NOT_ELIGIBLE", "MANUAL_REVIEW"]] = None


class ApproveApplicationRequest(BaseModel):
    """Admin final approval / rejection of a loan application."""

    action: Literal["approve", "reject", "request_info"]
    notes: Optional[str] = Field(None, max_length=1000)


class ContactApplicantRequest(BaseModel):
    """Admin contact / message log for an applicant."""

    channel: Literal["email", "phone", "message"] = "message"
    subject: Optional[str] = Field(None, max_length=200)
    message: str = Field(..., min_length=5, max_length=2000)
