"""AI advisor, what-if, and EMI calculator routes."""

from fastapi import APIRouter, Depends, HTTPException

from app.ai.agent import get_agent
from app.schemas.loan import AdvisorRequest, EMIRequest, EMIResponse, WhatIfRequest
from app.services import loan_service
from app.utils.deps import get_current_user
from app.utils.finance import (
    calculate_emi,
    calculate_total_interest,
    calculate_total_repayment,
)

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/advisor")
async def advisor(payload: AdvisorRequest, current_user: dict = Depends(get_current_user)):
    """AI Loan Advisor — guidance only; does not decide eligibility."""
    agent = get_agent()
    context = payload.context or {}
    if payload.application_id:
        app = await loan_service.get_loan_by_id(
            payload.application_id, user_id=current_user["id"]
        )
        context["application"] = app
    return await agent.advise(payload.message, context)


@router.post("/what-if")
async def what_if(payload: WhatIfRequest, current_user: dict = Depends(get_current_user)):
    """What-If Simulator — re-run Forward Chaining with modified parameters."""
    agent = get_agent()

    if payload.application_id:
        base = await loan_service.get_loan_by_id(
            payload.application_id, user_id=current_user["id"]
        )
    elif payload.base_facts:
        base = payload.base_facts
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide application_id or base_facts for simulation.",
        )

    overrides = {
        k: v
        for k, v in payload.model_dump().items()
        if k not in ("application_id", "base_facts") and v is not None
    }
    return await agent.what_if(base, overrides)


@router.post("/emi", response_model=EMIResponse)
async def emi_calculator(payload: EMIRequest):
    """Standalone EMI calculator (public within authenticated session optional)."""
    emi = calculate_emi(payload.loan_amount, payload.interest_rate, payload.tenure_months)
    total_interest = calculate_total_interest(emi, payload.tenure_months, payload.loan_amount)
    total_repayment = calculate_total_repayment(emi, payload.tenure_months)
    return EMIResponse(
        emi=emi,
        total_interest=total_interest,
        total_repayment=total_repayment,
        loan_amount=payload.loan_amount,
        interest_rate=payload.interest_rate,
        tenure_months=payload.tenure_months,
    )


@router.post("/emi/public", response_model=EMIResponse)
async def emi_calculator_public(payload: EMIRequest):
    """Public EMI calculator — no auth required."""
    return await emi_calculator(payload)
