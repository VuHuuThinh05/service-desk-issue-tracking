from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.ticket_event import TicketEvent
from app.models.user import User


EMPLOYEE_PASSWORD = "EmployeePassword123!"
AGENT_PASSWORD = "AgentPassword123!"


def login(client, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_ticket(client, token: str) -> dict:
    response = client.post(
        "/api/v1/tickets",
        headers=auth_headers(token),
        json={
            "title": "Không thể kết nối máy in",
            "description": "Máy tính không thể kết nối máy in tại văn phòng.",
            "category": "Hardware",
            "priority": "HIGH",
        },
    )
    assert response.status_code == 201
    return response.json()


def assign_ticket(client, admin_token: str, ticket_id: str, agent_id) -> None:
    response = client.post(
        f"/api/v1/tickets/{ticket_id}/assign",
        headers=auth_headers(admin_token),
        json={"assignee_id": str(agent_id)},
    )
    assert response.status_code == 200


def change_status(
    client,
    agent_token: str,
    ticket_id: str,
    new_status: str,
):
    return client.post(
        f"/api/v1/tickets/{ticket_id}/transitions",
        headers=auth_headers(agent_token),
        json={"status": new_status},
    )


def test_employee_can_create_ticket(
    client,
    employee_user,
    db_session: Session,
):
    token = login(client, employee_user.email, EMPLOYEE_PASSWORD)
    ticket = create_ticket(client, token)

    assert ticket["requester_id"] == str(employee_user.id)
    assert ticket["status"] == "OPEN"
    assert ticket["priority"] == "HIGH"
    assert ticket["assignee_id"] is None

    events = db_session.scalars(
        select(TicketEvent).where(
            TicketEvent.ticket_id == UUID(ticket["id"])
        )
    ).all()

    assert len(events) == 1
    assert events[0].event_type == "TICKET_CREATED"


def test_employee_cannot_view_another_employees_ticket(
    client,
    employee_user,
    second_employee,
):
    token1 = login(client, employee_user.email, EMPLOYEE_PASSWORD)
    token2 = login(client, second_employee.email, EMPLOYEE_PASSWORD)
    ticket = create_ticket(client, token1)

    response = client.get(
        f"/api/v1/tickets/{ticket['id']}",
        headers=auth_headers(token2),
    )

    assert response.status_code == 404


def test_employee_list_only_own_tickets(
    client,
    employee_user,
    second_employee,
):
    token1 = login(client, employee_user.email, EMPLOYEE_PASSWORD)
    token2 = login(client, second_employee.email, EMPLOYEE_PASSWORD)
    create_ticket(client, token1)

    response = client.get(
        "/api/v1/tickets",
        headers=auth_headers(token2),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_agent_cannot_create_ticket(client, support_agent):
    token = login(client, support_agent.email, AGENT_PASSWORD)

    response = client.post(
        "/api/v1/tickets",
        headers=auth_headers(token),
        json={
            "title": "Yêu cầu hỗ trợ",
            "description": "Kiểm tra thiết bị tại văn phòng.",
            "category": "Hardware",
            "priority": "MEDIUM",
        },
    )

    assert response.status_code == 403


def test_admin_assigns_ticket_and_agent_resolves_it(
    client,
    admin_user,
    employee_user,
    support_agent,
    db_session: Session,
):
    admin, admin_password = admin_user
    admin_token = login(client, admin.email, admin_password)
    employee_token = login(client, employee_user.email, EMPLOYEE_PASSWORD)
    agent_token = login(client, support_agent.email, AGENT_PASSWORD)

    ticket = create_ticket(client, employee_token)
    ticket_id = ticket["id"]

    assign_ticket(client, admin_token, ticket_id, support_agent.id)

    agent_tickets = client.get(
        "/api/v1/tickets",
        headers=auth_headers(agent_token),
    )
    assert agent_tickets.status_code == 200
    assert any(item["id"] == ticket_id for item in agent_tickets.json())

    response = change_status(client, agent_token, ticket_id, "RESOLVED")
    assert response.status_code == 200
    assert response.json()["status"] == "RESOLVED"
    assert response.json()["resolved_at"] is not None

    events = db_session.scalars(
        select(TicketEvent)
        .where(TicketEvent.ticket_id == UUID(ticket_id))
        .order_by(TicketEvent.created_at.asc())
    ).all()

    event_types = [event.event_type for event in events]
    assert event_types.count("TICKET_CREATED") == 1
    assert event_types.count("TICKET_ASSIGNED") == 1
    assert event_types.count("STATUS_CHANGED") == 2


def test_employee_cannot_assign_ticket(
    client,
    employee_user,
    support_agent,
):
    token = login(client, employee_user.email, EMPLOYEE_PASSWORD)
    ticket = create_ticket(client, token)

    response = client.post(
        f"/api/v1/tickets/{ticket['id']}/assign",
        headers=auth_headers(token),
        json={"assignee_id": str(support_agent.id)},
    )

    assert response.status_code == 403


def test_invalid_status_transition_is_rejected(
    client,
    admin_user,
    employee_user,
    support_agent,
):
    admin, admin_password = admin_user
    admin_token = login(client, admin.email, admin_password)
    employee_token = login(client, employee_user.email, EMPLOYEE_PASSWORD)
    agent_token = login(client, support_agent.email, AGENT_PASSWORD)

    ticket = create_ticket(client, employee_token)
    assign_ticket(client, admin_token, ticket["id"], support_agent.id)

    response = change_status(client, agent_token, ticket["id"], "OPEN")

    assert response.status_code == 409
    assert "IN_PROGRESS" in response.json()["detail"]


def test_employee_cannot_view_another_ticket_comments(
    client,
    employee_user,
    second_employee,
):
    token1 = login(client, employee_user.email, EMPLOYEE_PASSWORD)
    token2 = login(client, second_employee.email, EMPLOYEE_PASSWORD)
    ticket = create_ticket(client, token1)

    response = client.get(
        f"/api/v1/tickets/{ticket['id']}/comments",
        headers=auth_headers(token2),
    )

    assert response.status_code == 404


def test_employee_cannot_view_another_ticket_events(
    client,
    employee_user,
    second_employee,
):
    token1 = login(client, employee_user.email, EMPLOYEE_PASSWORD)
    token2 = login(client, second_employee.email, EMPLOYEE_PASSWORD)
    ticket = create_ticket(client, token1)

    response = client.get(
        f"/api/v1/tickets/{ticket['id']}/events",
        headers=auth_headers(token2),
    )

    assert response.status_code == 404


def test_closed_ticket_rejects_new_comment(
    client,
    admin_user,
    employee_user,
    support_agent,
):
    admin, admin_password = admin_user
    admin_token = login(client, admin.email, admin_password)
    employee_token = login(client, employee_user.email, EMPLOYEE_PASSWORD)
    agent_token = login(client, support_agent.email, AGENT_PASSWORD)

    ticket = create_ticket(client, employee_token)
    ticket_id = ticket["id"]
    assign_ticket(client, admin_token, ticket_id, support_agent.id)

    for new_status in ("RESOLVED", "CLOSED"):
        response = change_status(client, agent_token, ticket_id, new_status)
        assert response.status_code == 200, response.text

    response = client.post(
        f"/api/v1/tickets/{ticket_id}/comments",
        headers=auth_headers(employee_token),
        json={"body": "Tôi muốn bổ sung thông tin."},
    )

    assert response.status_code == 409


def test_agent_cannot_resolve_ticket_assigned_to_another_agent(
    client,
    admin_user,
    employee_user,
    support_agent,
    db_session: Session,
):
    admin, admin_password = admin_user
    admin_token = login(client, admin.email, admin_password)
    employee_token = login(client, employee_user.email, EMPLOYEE_PASSWORD)

    other_agent = User(
        full_name="Other Support Agent",
        email="other-agent-test@example.com",
        password_hash=hash_password("OtherAgentPassword123!"),
        role="SUPPORT_AGENT",
        is_active=True,
    )
    db_session.add(other_agent)
    db_session.commit()
    db_session.refresh(other_agent)

    other_agent_token = login(
        client,
        other_agent.email,
        "OtherAgentPassword123!",
    )

    ticket = create_ticket(client, employee_token)
    assign_ticket(client, admin_token, ticket["id"], support_agent.id)

    response = change_status(
        client,
        other_agent_token,
        ticket["id"],
        "IN_PROGRESS",
    )

    assert response.status_code == 403


def test_resolved_ticket_can_be_reopened(
    client,
    admin_user,
    employee_user,
    support_agent,
):
    admin, admin_password = admin_user
    admin_token = login(client, admin.email, admin_password)
    employee_token = login(client, employee_user.email, EMPLOYEE_PASSWORD)
    agent_token = login(client, support_agent.email, AGENT_PASSWORD)

    ticket = create_ticket(client, employee_token)
    ticket_id = ticket["id"]
    assign_ticket(client, admin_token, ticket_id, support_agent.id)

    resolved = change_status(client, agent_token, ticket_id, "RESOLVED")
    assert resolved.status_code == 200
    assert resolved.json()["resolved_at"] is not None

    reopened = change_status(client, agent_token, ticket_id, "IN_PROGRESS")
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "IN_PROGRESS"
    assert reopened.json()["resolved_at"] is None


def test_closed_ticket_cannot_change_status(
    client,
    admin_user,
    employee_user,
    support_agent,
):
    admin, admin_password = admin_user
    admin_token = login(client, admin.email, admin_password)
    employee_token = login(client, employee_user.email, EMPLOYEE_PASSWORD)
    agent_token = login(client, support_agent.email, AGENT_PASSWORD)

    ticket = create_ticket(client, employee_token)
    ticket_id = ticket["id"]
    assign_ticket(client, admin_token, ticket_id, support_agent.id)

    for new_status in ("RESOLVED", "CLOSED"):
        response = change_status(client, agent_token, ticket_id, new_status)
        assert response.status_code == 200, response.text

    response = change_status(client, agent_token, ticket_id, "IN_PROGRESS")

    assert response.status_code == 409
