from datetime import datetime

from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    applicant_name: str
    email: str
    student_id: str | None = None
    supervisor: str | None = None
    lab: str | None = None
    requested_username: str | None = None
    ssh_public_key: str | None = None
    need_gpu: bool = True
    purpose: str | None = None


class ApplicationOut(BaseModel):
    id: int
    applicant_name: str
    email: str
    student_id: str | None = None
    supervisor: str | None = None
    lab: str | None = None
    requested_username: str | None = None
    ssh_public_key: str | None = None
    need_gpu: bool
    purpose: str | None = None
    status: str
    reviewer_id: int | None = None
    review_comment: str | None = None
    created_by_user_id: int | None = None
    created_at: datetime
    reviewed_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }


class ApplicationReviewRequest(BaseModel):
    review_comment: str
