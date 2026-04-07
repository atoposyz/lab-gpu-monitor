from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas.announcement import AnnouncementCreate, AnnouncementOut, AnnouncementUpdate
from backend.security.deps import get_current_active_user, require_admin, get_db
from backend.services.announcement_service import (
    create_announcement,
    disable_announcement,
    get_announcement_by_id,
    list_active_announcements,
    update_announcement,
)
from backend.services.audit_service import create_audit_log

router = APIRouter(prefix="/api")


@router.get("/announcements", response_model=list[AnnouncementOut])
def list_announcements(db: Session = Depends(get_db)):
    return list_active_announcements(db)


@router.post("/admin/announcements", response_model=AnnouncementOut)
def create_announcement_endpoint(
    payload: AnnouncementCreate,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    announcement = create_announcement(db, current_user.id, payload.model_dump())
    create_audit_log(
        db,
        actor_user_id=current_user.id,
        action="announcement_create",
        target_type="announcement",
        target_id=str(announcement.id),
        detail_json={
            "title": announcement.title,
            "level": announcement.level,
            "is_active": announcement.is_active,
        },
    )
    return announcement


@router.put("/admin/announcements/{announcement_id}", response_model=AnnouncementOut)
def update_announcement_endpoint(
    announcement_id: int,
    payload: AnnouncementUpdate,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    announcement = get_announcement_by_id(db, announcement_id)
    if announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")

    before = {
        "title": announcement.title,
        "content": announcement.content,
        "level": announcement.level,
        "is_active": announcement.is_active,
        "start_at": str(announcement.start_at) if announcement.start_at else None,
        "end_at": str(announcement.end_at) if announcement.end_at else None,
    }
    announcement = update_announcement(db, announcement, payload.model_dump(exclude_none=True))
    create_audit_log(
        db,
        actor_user_id=current_user.id,
        action="announcement_update",
        target_type="announcement",
        target_id=str(announcement.id),
        detail_json={
            "before": before,
            "after": {
                "title": announcement.title,
                "level": announcement.level,
                "is_active": announcement.is_active,
            },
        },
    )
    return announcement


@router.post("/admin/announcements/{announcement_id}/disable", response_model=AnnouncementOut)
def disable_announcement_endpoint(
    announcement_id: int,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    announcement = get_announcement_by_id(db, announcement_id)
    if announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    announcement = disable_announcement(db, announcement)
    create_audit_log(
        db,
        actor_user_id=current_user.id,
        action="announcement_disable",
        target_type="announcement",
        target_id=str(announcement.id),
        detail_json={
            "title": announcement.title, "is_active": announcement.is_active},
    )
    return announcement
