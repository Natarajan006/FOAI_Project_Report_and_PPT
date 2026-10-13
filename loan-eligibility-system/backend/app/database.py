"""MongoDB database connection using Motor (async driver)."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings

settings = get_settings()

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """Establish MongoDB connection and create indexes."""
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]

    # Unique index on email
    await db.users.create_index("email", unique=True)
    await db.rules.create_index("rule_id", unique=True)
    await db.loan_applications.create_index("user_id")
    await db.assessments.create_index("application_id")
    await db.assessments.create_index("user_id")
    await db.audit_logs.create_index("timestamp")
    await db.contact_logs.create_index("application_id")
    await db.contact_logs.create_index("timestamp")


async def close_db() -> None:
    """Close MongoDB connection."""
    global client, db
    if client:
        client.close()
    client = None
    db = None


def get_db() -> AsyncIOMotorDatabase:
    """Return the active database instance."""
    if db is None:
        raise RuntimeError("Database is not connected. Call connect_db() first.")
    return db
