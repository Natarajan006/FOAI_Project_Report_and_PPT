"""Authentication and user service."""

from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from fastapi import HTTPException, status

from app.database import get_db
from app.schemas.auth import UserRegister
from app.utils.security import create_access_token, hash_password, verify_password


def serialize_user(user: dict) -> dict:
    """Convert MongoDB user doc to safe API dict (no password)."""
    return {
        "id": str(user["_id"]),
        "full_name": user["full_name"],
        "email": user["email"],
        "phone": user["phone"],
        "role": user["role"],
        "created_at": user["created_at"],
        "is_active": user.get("is_active", True),
    }


async def register_user(payload: UserRegister) -> dict:
    """Register a new user with hashed password."""
    db = get_db()
    existing = await db.users.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    doc = {
        "full_name": payload.full_name.strip(),
        "email": payload.email.lower(),
        "phone": payload.phone,
        "password_hash": hash_password(payload.password),
        "role": "user",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(doc)
    doc["_id"] = result.inserted_id

    await db.audit_logs.insert_one(
        {
            "action": "user_registered",
            "user_id": str(result.inserted_id),
            "email": doc["email"],
            "timestamp": datetime.now(timezone.utc),
        }
    )

    user = serialize_user(doc)
    token = create_access_token(
        {"sub": user["id"], "role": user["role"], "email": user["email"]}
    )
    return {"access_token": token, "token_type": "bearer", "user": user}


async def login_user(email: str, password: str) -> dict:
    """Authenticate user and return JWT + user info."""
    db = get_db()
    user = await db.users.find_one({"email": email.lower()})
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    await db.audit_logs.insert_one(
        {
            "action": "user_login",
            "user_id": str(user["_id"]),
            "email": user["email"],
            "timestamp": datetime.now(timezone.utc),
        }
    )

    serialized = serialize_user(user)
    token = create_access_token(
        {
            "sub": serialized["id"],
            "role": serialized["role"],
            "email": serialized["email"],
        }
    )
    return {"access_token": token, "token_type": "bearer", "user": serialized}


async def update_profile(user_id: str, updates: dict[str, Any]) -> dict:
    """Update user profile fields (never password here)."""
    db = get_db()
    clean = {k: v for k, v in updates.items() if v is not None}
    if not clean:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        return serialize_user(user)

    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": clean})
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    return serialize_user(user)


async def list_users(skip: int = 0, limit: int = 50) -> list[dict]:
    """Admin: list users without password hashes."""
    db = get_db()
    cursor = db.users.find({}, {"password_hash": 0}).skip(skip).limit(limit)
    users = []
    async for u in cursor:
        u["id"] = str(u["_id"])
        del u["_id"]
        users.append(u)
    return users
