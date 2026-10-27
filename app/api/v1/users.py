
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserPublic, UserStatusUpdate


router = APIRouter(prefix="/users", tags=["Users"])


def require_admin(current_user: User) -> None:
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Admin mới được quản lý người dùng.",
        )


@router.get("", response_model=list[UserPublic])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[User]:
    require_admin(current_user)

    return db.scalars(
        select(User).order_by(User.created_at.desc())
    ).all()


@router.post(
    "",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    require_admin(current_user)

    email = data.email.strip().lower()
    full_name = data.full_name.strip()

    if not full_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Họ tên không được để trống.",
        )

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email đã được sử dụng.",
        )

    user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=True,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Không thể tạo người dùng. Email có thể đã được sử dụng.",
        )


@router.patch("/{user_id}/status", response_model=UserPublic)
def update_user_status(
    user_id: UUID,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    require_admin(current_user)

    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng.",
        )

    if user.id == current_user.id and not data.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tự vô hiệu hóa tài khoản Admin đang đăng nhập.",
        )

    user.is_active = data.is_active
    db.commit()
    db.refresh(user)

    return user
