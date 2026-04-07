import argparse

from backend.db.base import Base
from backend.db.session import SessionLocal, engine
from backend.services.auth_service import create_user


def main() -> None:
    parser = argparse.ArgumentParser(description="Create initial admin account")
    parser.add_argument("--username", required=True, help="管理员用户名")
    parser.add_argument("--password", required=True, help="管理员密码")
    parser.add_argument("--full-name", required=True, help="管理员显示姓名")
    parser.add_argument("--email", required=False, help="管理员邮箱")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        user = create_user(
            db,
            username=args.username,
            password=args.password,
            full_name=args.full_name,
            email=args.email,
            role="admin",
        )
        print(f"Admin user created: id={user.id}, username={user.username}")


if __name__ == "__main__":
    main()
