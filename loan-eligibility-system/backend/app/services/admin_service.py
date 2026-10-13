"""Admin services: analytics, applications, rules, reviews."""

from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from fastapi import HTTPException, status

from app.ai.knowledge_base import validate_rule
from app.database import get_db
from app.services.loan_service import _serialize_application, _serialize_assessment


async def _get_applicant_contact(user_id: str) -> dict:
    """Fetch applicant contact details (never includes password)."""
    db = get_db()
    if not ObjectId.is_valid(user_id):
        return {"email": None, "phone": None, "full_name": None}
    user = await db.users.find_one(
        {"_id": ObjectId(user_id)}, {"password_hash": 0}
    )
    if not user:
        return {"email": None, "phone": None, "full_name": None}
    return {
        "email": user.get("email"),
        "phone": user.get("phone"),
        "full_name": user.get("full_name"),
        "user_id": str(user["_id"]),
    }


async def get_admin_dashboard_stats() -> dict:
    db = get_db()
    total_users = await db.users.count_documents({"role": "user"})
    apps = await db.loan_applications.find().to_list(5000)
    assessments = await db.assessments.find().to_list(5000)

    eligible = sum(1 for a in apps if a.get("status") == "eligible")
    not_eligible = sum(1 for a in apps if a.get("status") == "not_eligible")
    manual = sum(1 for a in apps if a.get("status") == "manual_review")
    submitted = sum(1 for a in apps if a.get("status") == "submitted")
    approved = sum(1 for a in apps if a.get("admin_decision") == "approved")
    rejected = sum(1 for a in apps if a.get("admin_decision") == "rejected")
    pending_approval = sum(
        1
        for a in apps
        if a.get("status") in ("manual_review", "eligible", "submitted")
        and a.get("admin_decision") not in ("approved", "rejected")
    )

    amounts = [a.get("requested_amount", 0) for a in apps]
    scores = [a.get("credit_score", 0) for a in apps]
    avg_amount = round(sum(amounts) / len(amounts), 2) if amounts else 0
    avg_credit = round(sum(scores) / len(scores), 2) if scores else 0

    # Distributions for charts
    loan_types: dict[str, int] = {}
    employment: dict[str, int] = {}
    risk_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    monthly: dict[str, int] = {}

    for a in apps:
        lt = a.get("loan_type", "Other")
        loan_types[lt] = loan_types.get(lt, 0) + 1
        et = a.get("employment_type", "Other")
        employment[et] = employment.get(et, 0) + 1
        created = a.get("created_at")
        if created:
            key = created.strftime("%Y-%m")
            monthly[key] = monthly.get(key, 0) + 1

    for asmt in assessments:
        rl = asmt.get("risk_level", "MEDIUM")
        if rl in risk_dist:
            risk_dist[rl] += 1

    # Recent items needing admin action
    pending_apps = [
        a
        for a in apps
        if a.get("status") in ("manual_review", "eligible", "submitted")
        and a.get("admin_decision") not in ("approved", "rejected")
    ]
    pending_apps.sort(key=lambda x: x.get("created_at") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    recent_pending = []
    for a in pending_apps[:8]:
        contact = await _get_applicant_contact(a.get("user_id", ""))
        recent_pending.append(
            {
                "id": str(a["_id"]),
                "full_name": a.get("full_name"),
                "loan_type": a.get("loan_type"),
                "requested_amount": a.get("requested_amount"),
                "status": a.get("status"),
                "credit_score": a.get("credit_score"),
                "created_at": a.get("created_at"),
                "email": contact.get("email"),
                "phone": contact.get("phone"),
            }
        )

    return {
        "total_users": total_users,
        "total_applications": len(apps),
        "eligible": eligible,
        "not_eligible": not_eligible,
        "manual_review": manual,
        "submitted": submitted,
        "pending_approval": pending_approval,
        "admin_approved": approved,
        "admin_rejected": rejected,
        "average_loan_amount": avg_amount,
        "average_credit_score": avg_credit,
        "eligibility_distribution": {
            "Eligible": eligible,
            "Not Eligible": not_eligible,
            "Manual Review": manual,
        },
        "loan_type_distribution": loan_types,
        "risk_distribution": risk_dist,
        "employment_distribution": employment,
        "monthly_applications": dict(sorted(monthly.items())),
        "pending_queue": recent_pending,
    }


async def list_all_applications(
    status_filter: Optional[str] = None,
    risk_filter: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[dict]:
    db = get_db()
    query: dict[str, Any] = {}
    if status_filter:
        query["status"] = status_filter
    if search:
        query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"loan_type": {"$regex": search, "$options": "i"}},
            {"purpose": {"$regex": search, "$options": "i"}},
        ]

    cursor = db.loan_applications.find(query).sort("created_at", -1).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        app = _serialize_application(doc)
        app["admin_decision"] = doc.get("admin_decision")
        app["admin_notes"] = doc.get("admin_notes")
        app["contact_count"] = doc.get("contact_count", 0)
        contact = await _get_applicant_contact(app["user_id"])
        app["applicant_email"] = contact.get("email")
        app["applicant_phone"] = contact.get("phone")
        # Attach latest assessment summary
        asmt = await db.assessments.find_one(
            {"application_id": app["id"]}, sort=[("timestamp", -1)]
        )
        if asmt:
            if risk_filter and asmt.get("risk_level") != risk_filter:
                continue
            app["latest_decision"] = asmt.get("decision")
            app["latest_risk"] = asmt.get("risk_level")
            app["assessment_id"] = str(asmt["_id"])
            app["reviewed"] = asmt.get("reviewed", False)
        elif risk_filter:
            continue
        results.append(app)
    return results


async def get_application_detail(loan_id: str) -> dict:
    """Full application + assessments + applicant contact for admin."""
    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail="Invalid application ID.")
    db = get_db()
    doc = await db.loan_applications.find_one({"_id": ObjectId(loan_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Loan application not found.")

    app = _serialize_application(doc)
    app["admin_decision"] = doc.get("admin_decision")
    app["admin_notes"] = doc.get("admin_notes")
    app["admin_reviewed_at"] = doc.get("admin_reviewed_at")
    app["admin_reviewed_by"] = doc.get("admin_reviewed_by")

    contact = await _get_applicant_contact(app["user_id"])
    assessments = []
    cursor = db.assessments.find({"application_id": loan_id}).sort("timestamp", -1)
    async for a in cursor:
        assessments.append(_serialize_assessment(a))

    contacts = []
    c_cursor = db.contact_logs.find({"application_id": loan_id}).sort("timestamp", -1)
    async for c in c_cursor:
        contacts.append(
            {
                "id": str(c["_id"]),
                "channel": c.get("channel"),
                "subject": c.get("subject"),
                "message": c.get("message"),
                "admin_id": c.get("admin_id"),
                "timestamp": c.get("timestamp"),
            }
        )

    return {
        "application": app,
        "applicant": contact,
        "assessments": assessments,
        "contact_history": contacts,
    }


async def approve_application(
    loan_id: str, admin_id: str, action: str, notes: Optional[str]
) -> dict:
    """
    Admin final decision on a loan application.
    approve → status eligible + admin_decision approved
    reject → status not_eligible + admin_decision rejected
    request_info → keep status, flag admin_decision request_info
    """
    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail="Invalid application ID.")
    db = get_db()
    doc = await db.loan_applications.find_one({"_id": ObjectId(loan_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Loan application not found.")

    if action == "approve":
        admin_decision = "approved"
        new_status = "eligible"
    elif action == "reject":
        admin_decision = "rejected"
        new_status = "not_eligible"
    else:
        admin_decision = "request_info"
        new_status = doc.get("status", "manual_review")

    updates = {
        "admin_decision": admin_decision,
        "admin_notes": notes,
        "admin_reviewed_by": admin_id,
        "admin_reviewed_at": datetime.now(timezone.utc),
        "status": new_status,
        "updated_at": datetime.now(timezone.utc),
    }
    await db.loan_applications.update_one({"_id": ObjectId(loan_id)}, {"$set": updates})

    # Sync latest assessment if present
    asmt = await db.assessments.find_one(
        {"application_id": loan_id}, sort=[("timestamp", -1)]
    )
    if asmt and action in ("approve", "reject"):
        decision = "ELIGIBLE" if action == "approve" else "NOT_ELIGIBLE"
        await db.assessments.update_one(
            {"_id": asmt["_id"]},
            {
                "$set": {
                    "decision": decision,
                    "reviewed": True,
                    "reviewed_by": admin_id,
                    "review_notes": notes,
                    "reviewed_at": datetime.now(timezone.utc),
                }
            },
        )

    await db.audit_logs.insert_one(
        {
            "action": f"application_{action}",
            "admin_id": admin_id,
            "application_id": loan_id,
            "notes": notes,
            "timestamp": datetime.now(timezone.utc),
        }
    )

    return await get_application_detail(loan_id)


async def contact_applicant(
    loan_id: str,
    admin_id: str,
    channel: str,
    message: str,
    subject: Optional[str] = None,
) -> dict:
    """Log an admin contact attempt and return mailto/tel helpers."""
    detail = await get_application_detail(loan_id)
    applicant = detail["applicant"]
    if not applicant.get("email") and not applicant.get("phone"):
        raise HTTPException(
            status_code=400,
            detail="Applicant contact details are not available.",
        )

    db = get_db()
    log = {
        "application_id": loan_id,
        "user_id": detail["application"]["user_id"],
        "admin_id": admin_id,
        "channel": channel,
        "subject": subject or f"Regarding your {detail['application'].get('loan_type', 'loan')} application",
        "message": message,
        "timestamp": datetime.now(timezone.utc),
    }
    result = await db.contact_logs.insert_one(log)
    await db.loan_applications.update_one(
        {"_id": ObjectId(loan_id)},
        {
            "$inc": {"contact_count": 1},
            "$set": {"last_contacted_at": datetime.now(timezone.utc)},
        },
    )
    await db.audit_logs.insert_one(
        {
            "action": "applicant_contacted",
            "admin_id": admin_id,
            "application_id": loan_id,
            "channel": channel,
            "timestamp": datetime.now(timezone.utc),
        }
    )

    email = applicant.get("email") or ""
    phone = applicant.get("phone") or ""
    subj = log["subject"]
    body = message
    mailto = f"mailto:{email}?subject={subj}&body={body}" if email else None
    tel = f"tel:{phone}" if phone else None

    return {
        "id": str(result.inserted_id),
        "message": "Contact logged successfully.",
        "applicant": applicant,
        "channel": channel,
        "mailto_link": mailto,
        "tel_link": tel,
        "whatsapp_link": f"https://wa.me/{phone.lstrip('+')}" if phone else None,
        "logged_at": log["timestamp"],
    }


async def list_contactable_applicants() -> list[dict]:
    """List applications with applicant contact info for the Contact page."""
    apps = await list_all_applications(limit=100)
    return [
        {
            "id": a["id"],
            "full_name": a["full_name"],
            "loan_type": a["loan_type"],
            "requested_amount": a["requested_amount"],
            "status": a["status"],
            "admin_decision": a.get("admin_decision"),
            "email": a.get("applicant_email"),
            "phone": a.get("applicant_phone"),
            "contact_count": a.get("contact_count", 0),
            "latest_decision": a.get("latest_decision"),
            "created_at": a.get("created_at"),
        }
        for a in apps
    ]


async def review_assessment(
    assessment_id: str, admin_id: str, notes: Optional[str], decision_override: Optional[str]
) -> dict:
    if not ObjectId.is_valid(assessment_id):
        raise HTTPException(status_code=400, detail="Invalid assessment ID.")
    db = get_db()
    doc = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    updates: dict[str, Any] = {
        "reviewed": True,
        "reviewed_by": admin_id,
        "review_notes": notes,
        "reviewed_at": datetime.now(timezone.utc),
    }
    if decision_override:
        updates["decision"] = decision_override
        status_map = {
            "ELIGIBLE": "eligible",
            "NOT_ELIGIBLE": "not_eligible",
            "MANUAL_REVIEW": "manual_review",
        }
        await db.loan_applications.update_one(
            {"_id": ObjectId(doc["application_id"])},
            {"$set": {"status": status_map[decision_override], "updated_at": datetime.now(timezone.utc)}},
        )

    await db.assessments.update_one({"_id": ObjectId(assessment_id)}, {"$set": updates})
    updated = await db.assessments.find_one({"_id": ObjectId(assessment_id)})

    await db.audit_logs.insert_one(
        {
            "action": "manual_review_completed",
            "admin_id": admin_id,
            "assessment_id": assessment_id,
            "notes": notes,
            "decision_override": decision_override,
            "timestamp": datetime.now(timezone.utc),
        }
    )
    return _serialize_assessment(updated)


# ---- Rule CRUD ----

def _serialize_rule(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "rule_id": doc["rule_id"],
        "name": doc["name"],
        "conditions": doc["conditions"],
        "conclusion": doc["conclusion"],
        "priority": doc["priority"],
        "explanation": doc["explanation"],
        "enabled": doc.get("enabled", True),
        "category": doc.get("category", "general"),
    }


async def list_rules() -> list[dict]:
    db = get_db()
    cursor = db.rules.find().sort("priority", 1)
    return [_serialize_rule(doc) async for doc in cursor]


async def create_rule(data: dict) -> dict:
    valid, err = validate_rule(data)
    if not valid:
        raise HTTPException(status_code=400, detail=f"Invalid rule: {err}")
    db = get_db()
    existing = await db.rules.find_one({"rule_id": data["rule_id"]})
    if existing:
        raise HTTPException(status_code=409, detail="Rule ID already exists.")
    data["created_at"] = datetime.now(timezone.utc)
    result = await db.rules.insert_one(data)
    data["_id"] = result.inserted_id
    return _serialize_rule(data)


async def update_rule(rule_mongo_id: str, updates: dict) -> dict:
    if not ObjectId.is_valid(rule_mongo_id):
        raise HTTPException(status_code=400, detail="Invalid rule ID.")
    db = get_db()
    existing = await db.rules.find_one({"_id": ObjectId(rule_mongo_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Rule not found.")

    clean = {k: v for k, v in updates.items() if v is not None}
    if "conditions" in clean:
        # Convert Pydantic models if needed
        clean["conditions"] = [
            c if isinstance(c, dict) else c.model_dump() for c in clean["conditions"]
        ]

    merged = {**existing, **clean}
    check = {
        "rule_id": merged["rule_id"],
        "name": merged["name"],
        "conditions": merged["conditions"],
        "conclusion": merged["conclusion"],
        "priority": merged["priority"],
        "explanation": merged["explanation"],
    }
    valid, err = validate_rule(check)
    if not valid:
        raise HTTPException(status_code=400, detail=f"Invalid rule: {err}")

    clean["updated_at"] = datetime.now(timezone.utc)
    await db.rules.update_one({"_id": ObjectId(rule_mongo_id)}, {"$set": clean})
    updated = await db.rules.find_one({"_id": ObjectId(rule_mongo_id)})
    return _serialize_rule(updated)


async def delete_rule(rule_mongo_id: str) -> dict:
    if not ObjectId.is_valid(rule_mongo_id):
        raise HTTPException(status_code=400, detail="Invalid rule ID.")
    db = get_db()
    result = await db.rules.delete_one({"_id": ObjectId(rule_mongo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Rule not found.")
    return {"message": "Rule deleted successfully."}
