from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    email: str | None = None
    role: str
    system_username: str | None = None
    is_active: bool

    model_config = {
        "from_attributes": True,
    }
