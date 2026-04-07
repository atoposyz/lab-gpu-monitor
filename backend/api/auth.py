from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.schemas.auth import LoginRequest, LoginResponse
from backend.schemas.user import UserOut
from backend.security.deps import get_current_active_user, get_db
from backend.services.auth_service import authenticate_user
from backend.services.audit_service import create_audit_log
from backend.security.jwt import create_access_token

router = APIRouter(prefix="/api/auth")


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(subject=str(user.id))
    create_audit_log(
        db,
        actor_user_id=user.id,
        action="user_login",
        target_type="user",
        target_id=str(user.id),
        detail_json={
            "username": user.username,
            "role": user.role,
        },
    )

    return LoginResponse(
        access_token=access_token,
        user=UserOut.from_orm(user),
    )


@router.get("/me", response_model=UserOut)
def read_current_user(current_user=Depends(get_current_active_user)):
    return current_user
