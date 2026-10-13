"""
Agentic AI Workflow for Loan Eligibility Assessment
====================================================
The agent orchestrates the assessment pipeline but does NOT decide eligibility.

Workflow:
1. Understand the request
2. Check required information
3. Identify missing information
4. Ask for missing information (halt assessment)
5. Validate collected information
6. Calculate derived financial values (EMI, DTI)
7. Invoke the Forward Chaining engine  ← authoritative decision
8. Analyze resulting facts
9. Classify Eligible / Not Eligible / Manual Review (from FC only)
10. Generate explanation
11. Suggest improvements
12. Return structured result for storage

LangGraph is optional; this agent implements the same workflow as a clear
state-machine pipeline that is easy to explain in a viva.
"""

from typing import Any, Optional

from app.ai.explanation import (
    build_reasons,
    compare_assessments,
    generate_explanation,
    generate_suggestions,
)
from app.ai.fact_generator import (
    build_financial_summary,
    check_missing_fields,
    generate_facts,
)
from app.ai.forward_chaining import run_forward_chaining
from app.ai.knowledge_base import get_active_rules
from app.ai.risk_analysis import analyze_risk


class LoanAssessmentAgent:
    """
    Agentic workflow manager.

    The agent collects, validates, calculates, and explains.
    The Forward Chaining engine alone produces the eligibility decision.
    """

    async def assess(self, applicant_data: dict[str, Any]) -> dict[str, Any]:
        """
        Run the full assessment workflow.
        If information is missing, returns a missing-info response without deciding.
        """
        # Step 1–3: Check for missing information
        missing = check_missing_fields(applicant_data)
        if missing:
            return {
                "status": "missing_information",
                "decision": None,
                "missing_fields": missing,
                "message": (
                    "Additional information required:\n"
                    + "\n".join(f"• {f}" for f in missing)
                    + "\n\nPlease provide these details to continue."
                ),
                "explanation": "Assessment paused — required facts are incomplete.",
                "triggered_rules": [],
                "derived_facts": [],
                "reasons": [],
                "suggestions": [
                    "Provide the missing fields listed above to continue the assessment."
                ],
                "risk_level": None,
                "risk_factors": [],
                "financial_summary": {},
            }

        # Step 5: Basic validation already done by Pydantic at API layer;
        # agent still guards critical numeric ranges for robustness.
        validation_error = self._validate(applicant_data)
        if validation_error:
            return {
                "status": "validation_error",
                "decision": None,
                "message": validation_error,
                "missing_fields": [],
                "explanation": validation_error,
                "triggered_rules": [],
                "derived_facts": [],
                "reasons": [],
                "suggestions": [],
                "risk_level": None,
                "risk_factors": [],
                "financial_summary": {},
            }

        # Step 6: Generate facts (includes EMI + DTI calculations)
        facts = generate_facts(applicant_data)
        financial_summary = build_financial_summary(facts)

        # Step 7: Load KB and invoke Forward Chaining (authoritative)
        rules = await get_active_rules()
        fc_result = run_forward_chaining(facts, rules)

        decision = fc_result["decision"]  # Agent must NOT override this
        derived = fc_result["derived_facts"]
        triggered = fc_result["triggered_rules"]

        # Step 8–10: Analyze, explain, suggest
        risk = analyze_risk(decision, derived, financial_summary)
        reasons = build_reasons(derived, decision)
        explanation = generate_explanation(
            decision, triggered, derived, financial_summary
        )
        suggestions = generate_suggestions(decision, derived, financial_summary)

        return {
            "status": "completed",
            "decision": decision,
            "risk_level": risk["risk_level"],
            "risk_factors": risk["risk_factors"],
            "triggered_rules": triggered,
            "derived_facts": derived,
            "facts": fc_result["facts"],
            "trace": fc_result["trace"],
            "explanation": explanation,
            "reasons": reasons,
            "suggestions": suggestions,
            "financial_summary": financial_summary,
            "loan_recommendation": financial_summary.get("loan_recommendation"),
            "missing_fields": [],
            "message": f"Assessment complete. Decision: {decision}",
            "disclaimer": (
                "Decision produced by deterministic Forward Chaining over demo rules. "
                "Not real bank underwriting."
            ),
        }

    async def what_if(
        self,
        base_data: dict[str, Any],
        overrides: dict[str, Any],
    ) -> dict[str, Any]:
        """
        What-If Simulator: modify parameters and re-run Forward Chaining.
        Shows before/after decisions and which rules changed.
        """
        # Baseline assessment
        before = await self.assess(base_data)
        if before.get("status") != "completed":
            return before

        # Apply overrides
        modified = {**base_data}
        changes: dict[str, Any] = {}
        for key, new_val in overrides.items():
            if new_val is not None and key in modified and modified[key] != new_val:
                changes[key] = {"from": modified[key], "to": new_val}
                modified[key] = new_val
            elif new_val is not None and key not in modified:
                changes[key] = {"from": None, "to": new_val}
                modified[key] = new_val

        after = await self.assess(modified)
        if after.get("status") != "completed":
            return after

        comparison = compare_assessments(before, after, changes)

        return {
            "status": "completed",
            "current_result": {
                "decision": before["decision"],
                "risk_level": before["risk_level"],
                "triggered_rules": before["triggered_rules"],
                "explanation": before["explanation"],
                "financial_summary": before["financial_summary"],
            },
            "after_change": {
                "decision": after["decision"],
                "risk_level": after["risk_level"],
                "triggered_rules": after["triggered_rules"],
                "explanation": after["explanation"],
                "financial_summary": after["financial_summary"],
                "reasons": after["reasons"],
                "suggestions": after["suggestions"],
            },
            "comparison": comparison,
            "message": (
                f"CURRENT: {before['decision']} → AFTER CHANGE: {after['decision']}"
            ),
        }

    async def advise(
        self, message: str, context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        AI Loan Advisor — rule/FAQ style guidance (no LLM required).
        Helps users understand the process; never decides eligibility.
        """
        msg = message.lower()
        context = context or {}
        replies = []

        if any(w in msg for w in ["eligible", "eligibility", "qualify", "qualify"]):
            replies.append(
                "Eligibility is determined by our Forward Chaining engine using demo rules "
                "(age, income, credit score, DTI, employment, repayment history). "
                "Submit a loan application or use Eligibility Assessment to get a decision."
            )
        if any(w in msg for w in ["dti", "debt", "ratio"]):
            replies.append(
                "Debt-to-Income (DTI) = (Existing EMI + New EMI) / Monthly Income × 100. "
                "Demo threshold for acceptable DTI is ≤ 40%."
            )
        if any(w in msg for w in ["emi", "installment"]):
            replies.append(
                "Use the EMI Calculator to estimate monthly payments. "
                "EMI depends on loan amount, interest rate, and tenure."
            )
        if any(w in msg for w in ["credit", "score", "cibil"]):
            replies.append(
                "This demo uses a manually entered Demo Credit Score (300–900). "
                "Good credit starts at 700; excellent at 750. "
                "No real credit bureau is accessed."
            )
        if any(w in msg for w in ["improve", "suggest", "advice", "help"]):
            replies.append(
                "Try the What-If Simulator to see how changing loan amount, tenure, "
                "income, or credit score affects the Forward Chaining decision."
            )
        if any(w in msg for w in ["manual", "review"]):
            replies.append(
                "Manual Review is triggered for borderline credit (600–699) or "
                "borderline DTI (40–50%). An admin will review those applications."
            )
        if any(w in msg for w in ["rule", "forward", "chaining", "how"]):
            replies.append(
                "Forward Chaining starts with your facts, fires matching rules, "
                "adds derived facts, and repeats until no new facts appear. "
                "The final decision facts map to ELIGIBLE / NOT ELIGIBLE / MANUAL REVIEW."
            )
        if any(w in msg for w in ["recommend", "amount", "how much"]):
            replies.append(
                "Loan amount recommendations are demo estimates based on income, "
                "existing EMI, credit score, and tenure — not financial advice."
            )

        if not replies:
            replies.append(
                "I can help with eligibility process, DTI, EMI, credit score, "
                "What-If simulation, and how Forward Chaining works. "
                "Ask a specific question, or apply for a loan to get an assessment."
            )

        replies.append(
            "Reminder: I do not decide eligibility — the Forward Chaining engine does."
        )

        return {
            "reply": "\n\n".join(replies),
            "context_used": bool(context),
            "disclaimer": "Demo advisor responses only. Not financial advice.",
        }

    def _validate(self, data: dict[str, Any]) -> Optional[str]:
        """Agent-level validation guard."""
        credit = data.get("credit_score")
        if credit is not None and (credit < 300 or credit > 900):
            return "Credit score must be between 300 and 900."
        age = data.get("age")
        if age is not None and (age < 18 or age > 80):
            return "Age must be between 18 and 80."
        income = data.get("monthly_income")
        if income is not None and income <= 0:
            return "Monthly income must be positive."
        amount = data.get("requested_amount")
        if amount is not None and amount <= 0:
            return "Requested loan amount must be positive."
        return None


# Singleton-style accessor
_agent: Optional[LoanAssessmentAgent] = None


def get_agent() -> LoanAssessmentAgent:
    global _agent
    if _agent is None:
        _agent = LoanAssessmentAgent()
    return _agent
