from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas.application import ApplicationCreate, ApplicationOut
from backend.security.deps import get_current_active_user, get_db
from backend.services.application_service import (
    create_application,
    get_application_by_id,
    get_user_applications,
)
from backend.services.audit_service import create_audit_log

router = APIRouter(prefix="/api")


@router.post("/applications", response_model=ApplicationOut)
def create_application_endpoint(
    payload: ApplicationCreate,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    application = create_application(db, current_user.id, payload.model_dump())
    create_audit_log(
        db,
        actor_user_id=current_user.id,
        action="application_submit",
        target_type="account_application",
        target_id=str(application.id),
        detail_json={
            "applicant_name": application.applicant_name,
            "email": application.email,
            "status": application.status,
        },
    )
    return application


@router.get("/applications/me", response_model=list[ApplicationOut])
def list_user_applications(
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return get_user_applications(db, current_user.id)


@router.get("/applications/{application_id}", response_model=ApplicationOut)
def get_application(
    application_id: int,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    application = get_application_by_id(db, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.created_by_user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this application")
    return application
