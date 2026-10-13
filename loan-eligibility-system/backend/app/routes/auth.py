"""Authentication routes."""

from fastapi import APIRouter, Depends

from app.schemas.auth import ProfileUpdate, TokenResponse, UserLogin, UserRegister, UserResponse
from app.services import auth_service
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister):
    """Register a new user account."""
    return await auth_service.register_user(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    """Login and receive a JWT access token."""
    return await auth_service.login_user(payload.email, payload.password)


@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return auth_service.serialize_user(current_user)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout endpoint. JWT is stateless; client must discard the token.
    Server acknowledges logout for audit/UX consistency.
    """
    return {"message": "Logged out successfully. Please discard your access token."}


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    payload: ProfileUpdate, current_user: dict = Depends(get_current_user)
):
    """Update current user profile."""
    return await auth_service.update_profile(
        current_user["id"], payload.model_dump(exclude_unset=True)
    )
