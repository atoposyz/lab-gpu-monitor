from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas.application import ApplicationOut, ApplicationReviewRequest
from backend.security.deps import get_db, require_admin
from backend.services.application_service import (
    approve_application,
    get_application_by_id,
    list_applications,
    reject_application,
)
from backend.services.audit_service import create_audit_log

router = APIRouter(prefix="/api/admin")


@router.get("/applications", response_model=list[ApplicationOut])
def list_applications_endpoint(
    status: str | None = None,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    return list_applications(db, status=status)


@router.post("/applications/{application_id}/approve", response_model=ApplicationOut)
def approve_application_endpoint(
    application_id: int,
    payload: ApplicationReviewRequest,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    application = get_application_by_id(db, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    updated = approve_application(db, application, current_user.id, payload.review_comment)
    create_audit_log(
        db,
        actor_user_id=current_user.id,
        action="application_approve",
        target_type="account_application",
        target_id=str(updated.id),
        detail_json={
            "review_comment": updated.review_comment,
            "status": updated.status,
        },
    )
    return updated


@router.post("/applications/{application_id}/reject", response_model=ApplicationOut)
def reject_application_endpoint(
    application_id: int,
    payload: ApplicationReviewRequest,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    application = get_application_by_id(db, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    updated = reject_application(db, application, current_user.id, payload.review_comment)
    create_audit_log(
        db,
        actor_user_id=current_user.id,
        action="application_reject",
        target_type="account_application",
        target_id=str(updated.id),
        detail_json={
            "review_comment": updated.review_comment,
            "status": updated.status,
        },
    )
    return updated
