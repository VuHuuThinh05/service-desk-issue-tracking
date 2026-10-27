
from uuid import uuid4

from app.models.user import User


EMPLOYEE_PASSWORD = "EmployeePassword123!"


def login(client, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_list_users(client, admin_user, employee_user):
    admin, admin_password = admin_user
    token = login(client, admin.email, admin_password)

    response = client.get(
        "/api/v1/users",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    users = response.json()
    assert any(user["id"] == str(admin.id) for user in users)
    assert any(user["id"] == str(employee_user.id) for user in users)

    for user in users:
        assert "password_hash" not in user


def test_employee_cannot_list_users(client, employee_user):
    token = login(client, employee_user.email, EMPLOYEE_PASSWORD)

    response = client.get(
        "/api/v1/users",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_admin_can_deactivate_another_user(
    client,
    admin_user,
    employee_user,
):
    admin, admin_password = admin_user
    token = login(client, admin.email, admin_password)

    response = client.patch(
        f"/api/v1/users/{employee_user.id}/status",
        headers=auth_headers(token),
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_employee_cannot_change_user_status(
    client,
    employee_user,
    second_employee,
):
    token = login(client, employee_user.email, EMPLOYEE_PASSWORD)

    response = client.patch(
        f"/api/v1/users/{second_employee.id}/status",
        headers=auth_headers(token),
        json={"is_active": False},
    )

    assert response.status_code == 403


def test_updating_nonexistent_user_returns_404(
    client,
    admin_user,
):
    admin, admin_password = admin_user
    token = login(client, admin.email, admin_password)

    response = client.patch(
        f"/api/v1/users/{uuid4()}/status",
        headers=auth_headers(token),
        json={"is_active": False},
    )

    assert response.status_code == 404


def test_admin_cannot_deactivate_own_account(
    client,
    admin_user,
):
    admin, admin_password = admin_user
    token = login(client, admin.email, admin_password)

    response = client.patch(
        f"/api/v1/users/{admin.id}/status",
        headers=auth_headers(token),
        json={"is_active": False},
    )

    assert response.status_code == 400
