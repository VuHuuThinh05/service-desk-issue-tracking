import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app
from app.models.user import User
import app.models  # Đăng ký tất cả model với SQLAlchemy


@pytest.fixture
def db_session():
    """Tạo database SQLite riêng cho mỗi bài test."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

@pytest.fixture
def client(db_session: Session):
    """Tạo HTTP client và chuyển kết nối DB sang database kiểm thử."""

    def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(fastapi_app) as test_client:
            yield test_client
    finally:
        fastapi_app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session: Session):
    """Tạo một tài khoản Admin phục vụ kiểm thử."""

    password = "TestPassword123!"

    user = User(
        full_name="Test Administrator",
        email="admin-test@example.com",
        password_hash=hash_password(password),
        role="ADMIN",
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user, password

@pytest.fixture
def employee_user(db_session: Session):
    user = User(
        full_name="Test Employee",
        email="employee-test@example.com",
        password_hash=hash_password("EmployeePassword123!"),
        role="EMPLOYEE",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def second_employee(db_session: Session):
    user = User(
        full_name="Second Employee",
        email="employee2-test@example.com",
        password_hash=hash_password("EmployeePassword123!"),
        role="EMPLOYEE",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def support_agent(db_session: Session):
    user = User(
        full_name="Test Support Agent",
        email="agent-test@example.com",
        password_hash=hash_password("AgentPassword123!"),
        role="SUPPORT_AGENT",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user