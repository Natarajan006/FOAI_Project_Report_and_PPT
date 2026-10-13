"""Assessment and report routes."""

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.schemas.loan import EvaluateRequest
from app.services import loan_service
from app.services.report_service import generate_assessment_pdf
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])


@router.post("/evaluate")
async def evaluate(
    payload: EvaluateRequest, current_user: dict = Depends(get_current_user)
):
    """Run Forward Chaining assessment on an existing application."""
    is_admin = current_user.get("role") == "admin"
    # Verify ownership unless admin
    await loan_service.get_loan_by_id(
        payload.application_id,
        user_id=None if is_admin else current_user["id"],
        is_admin=is_admin,
    )
    return await loan_service.evaluate_application(
        current_user["id"] if not is_admin else (
            (await loan_service.get_loan_by_id(payload.application_id, is_admin=True))["user_id"]
        ),
        payload.application_id,
    )


@router.get("/history")
async def assessment_history(current_user: dict = Depends(get_current_user)):
    """List all assessments for the current user."""
    return await loan_service.get_user_assessments(current_user["id"])


@router.get("/{assessment_id}")
async def get_assessment(
    assessment_id: str, current_user: dict = Depends(get_current_user)
):
    """Get assessment details."""
    is_admin = current_user.get("role") == "admin"
    return await loan_service.get_assessment(
        assessment_id,
        user_id=None if is_admin else current_user["id"],
        is_admin=is_admin,
    )


@router.get("/{assessment_id}/report")
async def download_report(
    assessment_id: str, current_user: dict = Depends(get_current_user)
):
    """Download PDF assessment report."""
    is_admin = current_user.get("role") == "admin"
    assessment = await loan_service.get_assessment(
        assessment_id,
        user_id=None if is_admin else current_user["id"],
        is_admin=is_admin,
    )
    application = await loan_service.get_loan_by_id(
        assessment["application_id"],
        user_id=None if is_admin else current_user["id"],
        is_admin=is_admin,
    )
    pdf_bytes = generate_assessment_pdf(application, assessment)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="assessment_{assessment_id}.pdf"'
        },
    )
