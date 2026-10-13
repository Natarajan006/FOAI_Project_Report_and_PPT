"""Rule management schemas for admin knowledge-base CRUD."""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, field_validator


ALLOWED_OPERATORS = {">=", "<=", ">", "<", "==", "!=", "in", "not_in"}


class RuleCondition(BaseModel):
    """Single condition within a rule."""

    field: str = Field(..., min_length=1, max_length=100)
    operator: Literal[">=", "<=", ">", "<", "==", "!=", "in", "not_in"]
    value: Any


class RuleCreate(BaseModel):
    """Create a new forward-chaining rule."""

    rule_id: str = Field(..., min_length=2, max_length=20, pattern=r"^R\d{3,}$")
    name: str = Field(..., min_length=3, max_length=150)
    conditions: list[RuleCondition] = Field(..., min_length=1)
    conclusion: str = Field(..., min_length=2, max_length=100)
    priority: int = Field(1, ge=1, le=100)
    explanation: str = Field(..., min_length=5, max_length=500)
    enabled: bool = True
    category: Optional[str] = Field("general", max_length=50)

    @field_validator("conditions")
    @classmethod
    def validate_conditions(cls, v: list[RuleCondition]) -> list[RuleCondition]:
        if not v:
            raise ValueError("At least one condition is required")
        for cond in v:
            if cond.operator not in ALLOWED_OPERATORS:
                raise ValueError(f"Invalid operator: {cond.operator}")
        return v


class RuleUpdate(BaseModel):
    """Update an existing rule (partial)."""

    name: Optional[str] = Field(None, min_length=3, max_length=150)
    conditions: Optional[list[RuleCondition]] = None
    conclusion: Optional[str] = Field(None, min_length=2, max_length=100)
    priority: Optional[int] = Field(None, ge=1, le=100)
    explanation: Optional[str] = Field(None, min_length=5, max_length=500)
    enabled: Optional[bool] = None
    category: Optional[str] = Field(None, max_length=50)


class RuleResponse(BaseModel):
    """Rule response for API."""

    id: str
    rule_id: str
    name: str
    conditions: list[dict[str, Any]]
    conclusion: str
    priority: int
    explanation: str
    enabled: bool
    category: str = "general"
