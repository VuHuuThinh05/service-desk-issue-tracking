from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Băm mật khẩu bằng thuật toán an toàn."""
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    """So sánh mật khẩu người dùng nhập với bản băm đã lưu."""
    return password_hasher.verify(plain_password, password_hash)


def create_access_token(
    user_id: UUID,
    role: str,
) -> str:
    """Tạo JWT có thời hạn cho người dùng đã xác thực."""
    now = datetime.now(timezone.utc)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )