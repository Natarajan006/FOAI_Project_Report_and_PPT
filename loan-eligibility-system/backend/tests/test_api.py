"""
API-level tests using FastAPI TestClient with mocked DB where needed.
Core auth/authorization and validation behaviour.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.users = MagicMock()
    db.users.find_one = AsyncMock(return_value=None)
    db.users.insert_one = AsyncMock(return_value=MagicMock(inserted_id=MagicMock(__str__=lambda s: "507f1f77bcf86cd799439011")))
    db.users.create_index = AsyncMock()
    db.rules = MagicMock()
    db.rules.create_index = AsyncMock()
    db.loan_applications = MagicMock()
    db.loan_applications.create_index = AsyncMock()
    db.assessments = MagicMock()
    db.assessments.create_index = AsyncMock()
    db.audit_logs = MagicMock()
    db.audit_logs.create_index = AsyncMock()
    db.audit_logs.insert_one = AsyncMock()
    return db


@pytest.fixture
def client(mock_db):
    with patch("app.database.connect_db", new_callable=AsyncMock), \
         patch("app.database.close_db", new_callable=AsyncMock), \
         patch("app.database.get_db", return_value=mock_db), \
         patch("app.utils.deps.get_db", return_value=mock_db):
        from app.main import app
        with TestClient(app) as c:
            yield c, mock_db


class TestHealth:
    def test_root(self, client):
        c, _ = client
        res = c.get("/")
        assert res.status_code == 200
        assert "status" in res.json()

    def test_health(self, client):
        c, _ = client
        res = c.get("/api/health")
        assert res.status_code == 200


class TestAuthValidation:
    def test_register_invalid_email(self, client):
        c, _ = client
        res = c.post(
            "/api/auth/register",
            json={
                "full_name": "Test User",
                "email": "not-an-email",
                "phone": "9876543210",
                "password": "Weak1",
                "confirm_password": "Weak1",
            },
        )
        assert res.status_code == 422

    def test_login_missing_fields(self, client):
        c, _ = client
        res = c.post("/api/auth/login", json={})
        assert res.status_code == 422


class TestUnauthorized:
    def test_me_without_token(self, client):
        c, _ = client
        res = c.get("/api/auth/me")
        assert res.status_code == 401

    def test_admin_without_token(self, client):
        c, _ = client
        res = c.get("/api/admin/users")
        assert res.status_code == 401

    def test_loans_without_token(self, client):
        c, _ = client
        res = c.get("/api/loans")
        assert res.status_code == 401


class TestEMIEndpoint:
    def test_emi_valid(self, client):
        c, _ = client
        res = c.post(
            "/api/ai/emi/public",
            json={"loan_amount": 100000, "interest_rate": 10, "tenure_months": 12},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["emi"] > 0
        assert data["total_repayment"] > data["loan_amount"]

    def test_emi_invalid(self, client):
        c, _ = client
        res = c.post(
            "/api/ai/emi/public",
            json={"loan_amount": -100, "interest_rate": 10, "tenure_months": 12},
        )
        assert res.status_code == 422
