from sqlalchemy.orm import Session

from backend.db.models.user import User
from backend.security.password import hash_password, verify_password


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_user(
    db: Session,
    username: str,
    password: str,
    full_name: str,
    email: str | None = None,
    role: str = "user",
    system_username: str | None = None,
    is_active: bool = True,
) -> User:
    user = User(
        username=username,
        password_hash=hash_password(password),
        full_name=full_name,
        email=email,
        role=role,
        system_username=system_username,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
