from datetime import datetime

from pydantic import BaseModel


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    level: str = "info"
    is_active: bool = True
    start_at: datetime | None = None
    end_at: datetime | None = None


class AnnouncementUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    level: str | None = None
    is_active: bool | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None


class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: str
    level: str
    is_active: bool
    start_at: datetime | None = None
    end_at: datetime | None = None
    created_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
