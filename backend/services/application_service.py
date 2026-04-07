from datetime import datetime
from typing import Iterable

from sqlalchemy.orm import Session

from backend.db.models.application import AccountApplication


def create_application(db: Session, actor_user_id: int, payload: dict) -> AccountApplication:
    application = AccountApplication(
        applicant_name=payload.get("applicant_name"),
        email=payload.get("email"),
        student_id=payload.get("student_id"),
        supervisor=payload.get("supervisor"),
        lab=payload.get("lab"),
        requested_username=payload.get("requested_username"),
        ssh_public_key=payload.get("ssh_public_key"),
        need_gpu=payload.get("need_gpu", True),
        purpose=payload.get("purpose"),
        status="pending",
        created_by_user_id=actor_user_id,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def get_user_applications(db: Session, user_id: int) -> list[AccountApplication]:
    return (
        db.query(AccountApplication)
        .filter(AccountApplication.created_by_user_id == user_id)
        .order_by(AccountApplication.created_at.desc())
        .all()
    )


def get_application_by_id(db: Session, application_id: int) -> AccountApplication | None:
    return db.query(AccountApplication).filter(AccountApplication.id == application_id).first()


def list_applications(db: Session, status: str | None = None) -> list[AccountApplication]:
    query = db.query(AccountApplication)
    if status:
        query = query.filter(AccountApplication.status == status)
    return query.order_by(AccountApplication.created_at.desc()).all()


def approve_application(db: Session, application: AccountApplication, reviewer_id: int, review_comment: str) -> AccountApplication:
    application.status = "approved"
    application.reviewer_id = reviewer_id
    application.review_comment = review_comment
    application.reviewed_at = datetime.utcnow()
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def reject_application(db: Session, application: AccountApplication, reviewer_id: int, review_comment: str) -> AccountApplication:
    application.status = "rejected"
    application.reviewer_id = reviewer_id
    application.review_comment = review_comment
    application.reviewed_at = datetime.utcnow()
    db.add(application)
    db.commit()
    db.refresh(application)
    return application
