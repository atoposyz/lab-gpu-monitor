from datetime import datetime

from sqlalchemy.orm import Session

from backend.db.models.announcement import Announcement


def list_active_announcements(db: Session) -> list[Announcement]:
    now = datetime.utcnow()
    query = db.query(Announcement).filter(Announcement.is_active.is_(True))
    query = query.filter(
        (Announcement.start_at.is_(None)) | (Announcement.start_at <= now),
        (Announcement.end_at.is_(None)) | (Announcement.end_at >= now),
    )
    return query.order_by(Announcement.created_at.desc()).all()


def create_announcement(db: Session, creator_id: int, payload: dict) -> Announcement:
    announcement = Announcement(
        title=payload.get("title"),
        content=payload.get("content"),
        level=payload.get("level", "info"),
        is_active=payload.get("is_active", True),
        start_at=payload.get("start_at"),
        end_at=payload.get("end_at"),
        created_by_user_id=creator_id,
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


def update_announcement(db: Session, announcement: Announcement, payload: dict) -> Announcement:
    if payload.get("title") is not None:
        announcement.title = payload["title"]
    if payload.get("content") is not None:
        announcement.content = payload["content"]
    if payload.get("level") is not None:
        announcement.level = payload["level"]
    if payload.get("is_active") is not None:
        announcement.is_active = payload["is_active"]
    if payload.get("start_at") is not None:
        announcement.start_at = payload["start_at"]
    if payload.get("end_at") is not None:
        announcement.end_at = payload["end_at"]
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


def disable_announcement(db: Session, announcement: Announcement) -> Announcement:
    announcement.is_active = False
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


def get_announcement_by_id(db: Session, announcement_id: int) -> Announcement | None:
    return db.query(Announcement).filter(Announcement.id == announcement_id).first()
