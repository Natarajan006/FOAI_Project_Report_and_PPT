"""Loan application and assessment services."""

from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from fastapi import HTTPException, status

from app.ai.agent import get_agent
from app.config import get_settings
from app.database import get_db
from app.schemas.loan import LoanApplicationCreate

settings = get_settings()


def _serialize_application(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "user_id": doc["user_id"],
        "full_name": doc["full_name"],
        "age": doc["age"],
        "gender": doc.get("gender"),
        "employment_type": doc["employment_type"],
        "monthly_income": doc["monthly_income"],
        "monthly_expenses": doc["monthly_expenses"],
        "existing_emi": doc["existing_emi"],
        "credit_score": doc["credit_score"],
        "employment_duration": doc["employment_duration"],
        "repayment_history": doc["repayment_history"],
        "loan_type": doc["loan_type"],
        "requested_amount": doc["requested_amount"],
        "tenure_months": doc["tenure_months"],
        "purpose": doc["purpose"],
        "interest_rate": doc["interest_rate"],
        "status": doc.get("status", "submitted"),
        "admin_decision": doc.get("admin_decision"),
        "admin_notes": doc.get("admin_notes"),
        "created_at": doc["created_at"],
        "updated_at": doc.get("updated_at"),
    }


def _serialize_assessment(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "application_id": doc["application_id"],
        "user_id": doc["user_id"],
        "decision": doc["decision"],
        "risk_level": doc["risk_level"],
        "triggered_rules": doc.get("triggered_rules", []),
        "derived_facts": doc.get("derived_facts", []),
        "explanation": doc.get("explanation", ""),
        "reasons": doc.get("reasons", []),
        "risk_factors": doc.get("risk_factors", []),
        "suggestions": doc.get("suggestions", []),
        "financial_summary": doc.get("financial_summary", {}),
        "loan_recommendation": doc.get("loan_recommendation"),
        "missing_fields": doc.get("missing_fields"),
        "timestamp": doc["timestamp"],
        "reviewed": doc.get("reviewed", False),
        "reviewed_by": doc.get("reviewed_by"),
        "review_notes": doc.get("review_notes"),
        "trace": doc.get("trace", []),
    }


async def create_loan_application(
    user_id: str, payload: LoanApplicationCreate, auto_assess: bool = True
) -> dict:
    """Create a loan application and optionally run AI assessment."""
    db = get_db()
    interest = payload.interest_rate
    if interest is None:
        interest = settings.default_interest_rates.get(payload.loan_type, 12.0)

    doc = {
        "user_id": user_id,
        "full_name": payload.full_name,
        "age": payload.age,
        "gender": payload.gender,
        "employment_type": payload.employment_type,
        "monthly_income": payload.monthly_income,
        "monthly_expenses": payload.monthly_expenses,
        "existing_emi": payload.existing_emi,
        "credit_score": payload.credit_score,
        "employment_duration": payload.employment_duration,
        "repayment_history": payload.repayment_history,
        "loan_type": payload.loan_type,
        "requested_amount": payload.requested_amount,
        "tenure_months": payload.tenure_months,
        "purpose": payload.purpose,
        "interest_rate": interest,
        "status": "submitted",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    result = await db.loan_applications.insert_one(doc)
    doc["_id"] = result.inserted_id
    application = _serialize_application(doc)

    assessment = None
    if auto_assess:
        assessment = await evaluate_application(user_id, str(result.inserted_id))

    return {"application": application, "assessment": assessment}


async def get_user_loans(user_id: str) -> list[dict]:
    db = get_db()
    cursor = db.loan_applications.find({"user_id": user_id}).sort("created_at", -1)
    return [_serialize_application(doc) async for doc in cursor]


async def get_loan_by_id(loan_id: str, user_id: Optional[str] = None, is_admin: bool = False) -> dict:
    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail="Invalid application ID.")
    db = get_db()
    query: dict[str, Any] = {"_id": ObjectId(loan_id)}
    if not is_admin and user_id:
        query["user_id"] = user_id
    doc = await db.loan_applications.find_one(query)
    if not doc:
        raise HTTPException(status_code=404, detail="Loan application not found.")
    return _serialize_application(doc)


async def evaluate_application(user_id: str, application_id: str) -> dict:
    """Run the Agentic AI workflow + Forward Chaining on an application."""
    application = await get_loan_by_id(application_id, user_id=user_id)
    agent = get_agent()
    result = await agent.assess(application)

    if result.get("status") == "missing_information":
        return {
            **result,
            "id": None,
            "application_id": application_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc),
            "reviewed": False,
        }

    if result.get("status") != "completed":
        raise HTTPException(status_code=400, detail=result.get("message", "Assessment failed."))

    db = get_db()
    assessment_doc = {
        "application_id": application_id,
        "user_id": user_id,
        "decision": result["decision"],
        "risk_level": result["risk_level"],
        "triggered_rules": result["triggered_rules"],
        "derived_facts": result["derived_facts"],
        "explanation": result["explanation"],
        "reasons": result["reasons"],
        "risk_factors": result["risk_factors"],
        "suggestions": result["suggestions"],
        "financial_summary": result["financial_summary"],
        "loan_recommendation": result.get("loan_recommendation"),
        "trace": result.get("trace", []),
        "timestamp": datetime.now(timezone.utc),
        "reviewed": False,
        "reviewed_by": None,
        "review_notes": None,
    }
    insert = await db.assessments.insert_one(assessment_doc)
    assessment_doc["_id"] = insert.inserted_id

    # Update application status based on decision
    status_map = {
        "ELIGIBLE": "eligible",
        "NOT_ELIGIBLE": "not_eligible",
        "MANUAL_REVIEW": "manual_review",
    }
    await db.loan_applications.update_one(
        {"_id": ObjectId(application_id)},
        {
            "$set": {
                "status": status_map.get(result["decision"], "submitted"),
                "updated_at": datetime.now(timezone.utc),
                "latest_assessment_id": str(insert.inserted_id),
            }
        },
    )

    await db.audit_logs.insert_one(
        {
            "action": "assessment_completed",
            "user_id": user_id,
            "application_id": application_id,
            "decision": result["decision"],
            "timestamp": datetime.now(timezone.utc),
        }
    )

    return _serialize_assessment(assessment_doc)


async def get_assessment(assessment_id: str, user_id: Optional[str] = None, is_admin: bool = False) -> dict:
    if not ObjectId.is_valid(assessment_id):
        raise HTTPException(status_code=400, detail="Invalid assessment ID.")
    db = get_db()
    query: dict[str, Any] = {"_id": ObjectId(assessment_id)}
    if not is_admin and user_id:
        query["user_id"] = user_id
    doc = await db.assessments.find_one(query)
    if not doc:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return _serialize_assessment(doc)


async def get_user_assessments(user_id: str) -> list[dict]:
    db = get_db()
    cursor = db.assessments.find({"user_id": user_id}).sort("timestamp", -1)
    return [_serialize_assessment(doc) async for doc in cursor]


async def get_user_dashboard_stats(user_id: str) -> dict:
    db = get_db()
    apps = await db.loan_applications.find({"user_id": user_id}).to_list(500)
    assessments = await db.assessments.find({"user_id": user_id}).sort("timestamp", -1).to_list(500)

    total = len(apps)
    eligible = sum(1 for a in apps if a.get("status") == "eligible")
    pending = sum(1 for a in apps if a.get("status") in ("submitted", "manual_review"))
    latest = _serialize_assessment(assessments[0]) if assessments else None
    latest_app = _serialize_application(apps[0]) if apps else None

    return {
        "total_applications": total,
        "eligible_applications": eligible,
        "pending_reviews": pending,
        "latest_assessment": latest,
        "latest_application": latest_app,
        "eligibility_status": latest["decision"] if latest else "N/A",
        "loan_amount": latest_app["requested_amount"] if latest_app else 0,
        "credit_score": latest_app["credit_score"] if latest_app else None,
        "risk_level": latest["risk_level"] if latest else None,
        "application_status": latest_app["status"] if latest_app else "N/A",
        "admin_decision": latest_app.get("admin_decision") if latest_app else None,
        "admin_notes": latest_app.get("admin_notes") if latest_app else None,
    }
