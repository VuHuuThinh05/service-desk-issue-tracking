from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserPublic


router = APIRouter(prefix="/auth", tags=["Xác thực"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Đăng nhập bằng email và mật khẩu."""

    user = db.scalar(
        select(User).where(User.email == payload.email)
    )

    if (
        user is None
        or not verify_password(payload.password, user.password_hash)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        user_id=user.id,
        role=user.role,
    )

    return TokenResponse(
        access_token=token,
        user=UserPublic.model_validate(user),
    )


@router.get("/me", response_model=UserPublic)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    """Trả về thông tin tài khoản từ token hiện tại."""

    return UserPublic.model_validate(current_user)