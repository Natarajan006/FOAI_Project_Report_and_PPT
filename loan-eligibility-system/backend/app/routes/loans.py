"""Loan application routes."""

from fastapi import APIRouter, Depends, Query

from app.schemas.loan import LoanApplicationCreate
from app.services import loan_service
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/loans", tags=["Loans"])


@router.post("")
async def create_loan(
    payload: LoanApplicationCreate,
    current_user: dict = Depends(get_current_user),
):
    """Submit a new loan application and run AI assessment."""
    return await loan_service.create_loan_application(current_user["id"], payload)


@router.get("")
async def list_loans(current_user: dict = Depends(get_current_user)):
    """List current user's loan applications."""
    return await loan_service.get_user_loans(current_user["id"])


@router.get("/dashboard/stats")
async def dashboard_stats(current_user: dict = Depends(get_current_user)):
    """User dashboard statistics."""
    return await loan_service.get_user_dashboard_stats(current_user["id"])


@router.get("/{loan_id}")
async def get_loan(loan_id: str, current_user: dict = Depends(get_current_user)):
    """Get a single loan application (owner only)."""
    is_admin = current_user.get("role") == "admin"
    return await loan_service.get_loan_by_id(
        loan_id, user_id=None if is_admin else current_user["id"], is_admin=is_admin
    )
