from getpass import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User


DEMO_USERS = [
    {
        "full_name": "System Administrator",
        "email": "admin@servicedesk.local",
        "role": "ADMIN",
    },
    {
        "full_name": "Support Agent One",
        "email": "agent1@servicedesk.local",
        "role": "SUPPORT_AGENT",
    },
    {
        "full_name": "Support Agent Two",
        "email": "agent2@servicedesk.local",
        "role": "SUPPORT_AGENT",
    },
    {
        "full_name": "Employee One",
        "email": "employee1@servicedesk.local",
        "role": "EMPLOYEE",
    },
    {
        "full_name": "Employee Two",
        "email": "employee2@servicedesk.local",
        "role": "EMPLOYEE",
    },
    {
        "full_name": "Employee Three",
        "email": "employee3@servicedesk.local",
        "role": "EMPLOYEE",
    },
]


def main() -> None:
    password = getpass("Nhap mat khau dung cho cac tai khoan demo: ")
    confirmation = getpass("Nhap lai mat khau de xac nhan: ")

    if len(password) < 12:
        raise SystemExit("Mat khau phai co it nhat 12 ky tu.")

    if password != confirmation:
        raise SystemExit("Hai mat khau khong khop. Khong tao tai khoan.")

    db = SessionLocal()
    created = 0
    skipped = 0

    try:
        for item in DEMO_USERS:
            existing_user = db.scalar(
                select(User).where(User.email == item["email"])
            )

            if existing_user is not None:
                print(f"Da ton tai, bo qua: {item['email']}")
                skipped += 1
                continue

            user = User(
                full_name=item["full_name"],
                email=item["email"],
                password_hash=hash_password(password),
                role=item["role"],
                is_active=True,
            )

            db.add(user)
            created += 1

        db.commit()

        print("\nHoan tat tao du lieu demo.")
        print(f"So tai khoan moi: {created}")
        print(f"So tai khoan bo qua: {skipped}")
        print("\nDanh sach tai khoan:")

        for item in DEMO_USERS:
            print(f"- {item['email']} | {item['role']}")

        print("\nMat khau khong duoc hien thi.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()