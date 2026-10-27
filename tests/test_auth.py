from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.models.user import User


def test_login_success(client, admin_user):
    user, password = admin_user

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": password,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == user.email
    assert data["user"]["role"] == "ADMIN"
    assert "access_token" in data
    assert "password_hash" not in data["user"]


def test_login_wrong_password(client, admin_user):
    user, _ = admin_user

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 401


def test_me_without_token(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_with_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_me_with_valid_token(client, admin_user):
    user, password = admin_user

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == user.email
    assert response.json()["role"] == "ADMIN"


def test_me_with_expired_token(client, admin_user):
    user, _ = admin_user

    expired_token = jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role,
            "iat": datetime.now(timezone.utc) - timedelta(minutes=10),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401


def test_inactive_user_cannot_login(client, db_session, admin_user):
    user, password = admin_user

    user.is_active = False
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": password,
        },
    )

    assert response.status_code == 401