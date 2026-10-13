"""
Seed script — creates demo admin, users, rules, and sample applications.

DEMO CREDENTIALS (change before any real deployment!):
  Admin: admin@loanai.demo / Admin@12345
  User:  user1@loanai.demo / User@12345
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure backend root is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.rules import SAMPLE_RULES
from app.config import get_settings
from app.database import close_db, connect_db, get_db
from app.utils.security import hash_password

settings = get_settings()


DEMO_USERS = [
    {
        "full_name": "System Administrator",
        "email": "admin@loanai.demo",
        "phone": "9999999999",
        "password": "Admin@12345",
        "role": "admin",
    },
    {
        "full_name": "Rahul Sharma",
        "email": "user1@loanai.demo",
        "phone": "9876543210",
        "password": "User@12345",
        "role": "user",
    },
    {
        "full_name": "Priya Patel",
        "email": "user2@loanai.demo",
        "phone": "9876543211",
        "password": "User@12345",
        "role": "user",
    },
    {
        "full_name": "Amit Kumar",
        "email": "user3@loanai.demo",
        "phone": "9876543212",
        "password": "User@12345",
        "role": "user",
    },
]


async def seed():
    print("Connecting to MongoDB...")
    await connect_db()
    db = get_db()

    # Clear collections for a clean demo seed
    for col in ("users", "loan_applications", "assessments", "rules", "audit_logs"):
        await db[col].delete_many({})
    print("Cleared existing collections.")

    # Seed users
    user_ids = {}
    for u in DEMO_USERS:
        doc = {
            "full_name": u["full_name"],
            "email": u["email"],
            "phone": u["phone"],
            "password_hash": hash_password(u["password"]),
            "role": u["role"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }
        result = await db.users.insert_one(doc)
        user_ids[u["email"]] = str(result.inserted_id)
        print(f"  Created {u['role']}: {u['email']}")

    # Seed rules
    for rule in SAMPLE_RULES:
        rule_doc = {**rule, "created_at": datetime.now(timezone.utc)}
        await db.rules.insert_one(rule_doc)
    print(f"  Seeded {len(SAMPLE_RULES)} rules.")

    # Sample loan applications (will be assessed on first user submit in app;
    # here we insert raw apps for admin dashboard demo)
    samples = [
        {
            "user_id": user_ids["user1@loanai.demo"],
            "full_name": "Rahul Sharma",
            "age": 32,
            "gender": "Male",
            "employment_type": "Salaried",
            "monthly_income": 75000,
            "monthly_expenses": 25000,
            "existing_emi": 8000,
            "credit_score": 780,
            "employment_duration": 48,
            "repayment_history": "Good",
            "loan_type": "Home Loan",
            "requested_amount": 500000,
            "tenure_months": 120,
            "purpose": "Home renovation",
            "interest_rate": 8.5,
            "status": "submitted",
        },
        {
            "user_id": user_ids["user2@loanai.demo"],
            "full_name": "Priya Patel",
            "age": 28,
            "gender": "Female",
            "employment_type": "Salaried",
            "monthly_income": 45000,
            "monthly_expenses": 20000,
            "existing_emi": 5000,
            "credit_score": 680,
            "employment_duration": 24,
            "repayment_history": "Average",
            "loan_type": "Personal Loan",
            "requested_amount": 300000,
            "tenure_months": 36,
            "purpose": "Medical expenses",
            "interest_rate": 12.0,
            "status": "submitted",
        },
        {
            "user_id": user_ids["user3@loanai.demo"],
            "full_name": "Amit Kumar",
            "age": 45,
            "gender": "Male",
            "employment_type": "Self-Employed",
            "monthly_income": 20000,
            "monthly_expenses": 18000,
            "existing_emi": 12000,
            "credit_score": 550,
            "employment_duration": 8,
            "repayment_history": "Poor",
            "loan_type": "Business Loan",
            "requested_amount": 1500000,
            "tenure_months": 24,
            "purpose": "Business expansion",
            "interest_rate": 14.0,
            "status": "submitted",
        },
    ]

    from app.ai.agent import get_agent

    agent = get_agent()
    for sample in samples:
        sample["created_at"] = datetime.now(timezone.utc)
        sample["updated_at"] = datetime.now(timezone.utc)
        result = await db.loan_applications.insert_one(sample)
        app_id = str(result.inserted_id)

        # Run assessment
        result_assess = await agent.assess(sample)
        if result_assess.get("status") == "completed":
            assessment_doc = {
                "application_id": app_id,
                "user_id": sample["user_id"],
                "decision": result_assess["decision"],
                "risk_level": result_assess["risk_level"],
                "triggered_rules": result_assess["triggered_rules"],
                "derived_facts": result_assess["derived_facts"],
                "explanation": result_assess["explanation"],
                "reasons": result_assess["reasons"],
                "risk_factors": result_assess["risk_factors"],
                "suggestions": result_assess["suggestions"],
                "financial_summary": result_assess["financial_summary"],
                "loan_recommendation": result_assess.get("loan_recommendation"),
                "trace": result_assess.get("trace", []),
                "timestamp": datetime.now(timezone.utc),
                "reviewed": False,
            }
            ins = await db.assessments.insert_one(assessment_doc)
            status_map = {
                "ELIGIBLE": "eligible",
                "NOT_ELIGIBLE": "not_eligible",
                "MANUAL_REVIEW": "manual_review",
            }
            await db.loan_applications.update_one(
                {"_id": result.inserted_id},
                {
                    "$set": {
                        "status": status_map[result_assess["decision"]],
                        "latest_assessment_id": str(ins.inserted_id),
                    }
                },
            )
            print(f"  Application {sample['full_name']}: {result_assess['decision']}")

    await db.audit_logs.insert_one(
        {
            "action": "database_seeded",
            "timestamp": datetime.now(timezone.utc),
            "note": "Demo data seeded. Change credentials before deployment.",
        }
    )

    print("\n=== DEMO CREDENTIALS (change before deployment!) ===")
    print("Admin: admin@loanai.demo / Admin@12345")
    print("User:  user1@loanai.demo / User@12345")
    print("Seed completed successfully.")
    await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
