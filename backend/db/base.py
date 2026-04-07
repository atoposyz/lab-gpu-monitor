from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

import backend.db.models  # noqa: F401
