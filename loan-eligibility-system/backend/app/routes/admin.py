"""Admin routes — protected by require_admin (403 for non-admins).

Admin console focuses on:
- Viewing loan applications
- Approving / rejecting applications
- Contacting applicants
- Rule & user management
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.schemas.loan import ApproveApplicationRequest, ContactApplicantRequest, ReviewRequest
from app.schemas.rules import RuleCreate, RuleUpdate
from app.services import admin_service, auth_service
from app.utils.deps import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard")
async def admin_dashboard(admin: dict = Depends(require_admin)):
    """Admin operations dashboard — pending queue + analytics."""
    return await admin_service.get_admin_dashboard_stats()


@router.get("/users")
async def admin_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: dict = Depends(require_admin),
):
    """List all users (passwords never included)."""
    return await auth_service.list_users(skip=skip, limit=limit)


@router.get("/applications")
async def admin_applications(
    status: Optional[str] = None,
    risk: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: dict = Depends(require_admin),
):
    """View/search/filter all loan applications with contact info."""
    return await admin_service.list_all_applications(
        status_filter=status, risk_filter=risk, search=search, skip=skip, limit=limit
    )


@router.get("/applications/{loan_id}")
async def admin_application_detail(loan_id: str, admin: dict = Depends(require_admin)):
    """View applicant details, contact info, AI reasoning, and contact history."""
    return await admin_service.get_application_detail(loan_id)


@router.post("/applications/{loan_id}/decision")
async def decide_application(
    loan_id: str,
    payload: ApproveApplicationRequest,
    admin: dict = Depends(require_admin),
):
    """Approve, reject, or request more information for a loan application."""
    return await admin_service.approve_application(
        loan_id, admin["id"], payload.action, payload.notes
    )


@router.post("/applications/{loan_id}/contact")
async def contact_applicant(
    loan_id: str,
    payload: ContactApplicantRequest,
    admin: dict = Depends(require_admin),
):
    """Log contact with applicant and return email/phone/WhatsApp links."""
    return await admin_service.contact_applicant(
        loan_id,
        admin["id"],
        payload.channel,
        payload.message,
        payload.subject,
    )


@router.get("/contacts")
async def list_contacts(admin: dict = Depends(require_admin)):
    """List applicants available to contact."""
    return await admin_service.list_contactable_applicants()


@router.post("/assessments/{assessment_id}/review")
async def review_assessment(
    assessment_id: str,
    payload: ReviewRequest,
    admin: dict = Depends(require_admin),
):
    """Mark manual review as reviewed; optional decision override."""
    return await admin_service.review_assessment(
        assessment_id, admin["id"], payload.notes, payload.decision_override
    )


@router.get("/rules")
async def get_rules(admin: dict = Depends(require_admin)):
    """List all knowledge-base rules."""
    return await admin_service.list_rules()


@router.post("/rules")
async def add_rule(payload: RuleCreate, admin: dict = Depends(require_admin)):
    """Add a new Forward Chaining rule."""
    data = payload.model_dump()
    data["conditions"] = [
        c.model_dump() if hasattr(c, "model_dump") else c for c in payload.conditions
    ]
    return await admin_service.create_rule(data)


@router.put("/rules/{rule_id}")
async def edit_rule(
    rule_id: str, payload: RuleUpdate, admin: dict = Depends(require_admin)
):
    """Edit an existing rule (enable/disable, conditions, etc.)."""
    updates = payload.model_dump(exclude_unset=True)
    if "conditions" in updates and updates["conditions"] is not None:
        updates["conditions"] = [
            c.model_dump() if hasattr(c, "model_dump") else c
            for c in payload.conditions
        ]
    return await admin_service.update_rule(rule_id, updates)


@router.delete("/rules/{rule_id}")
async def remove_rule(rule_id: str, admin: dict = Depends(require_admin)):
    """Delete a rule from the knowledge base."""
    return await admin_service.delete_rule(rule_id)
