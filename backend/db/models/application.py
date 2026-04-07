from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.db.base import Base


class AccountApplication(Base):
    __tablename__ = "account_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False)
    student_id = Column(String(64), nullable=True)
    supervisor = Column(String(128), nullable=True)
    lab = Column(String(128), nullable=True)
    requested_username = Column(String(64), nullable=True)
    ssh_public_key = Column(Text, nullable=True)
    need_gpu = Column(Boolean, nullable=False, default=True)
    purpose = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_comment = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    reviewer = relationship("User", foreign_keys=[reviewer_id])
    creator = relationship("User", foreign_keys=[created_by_user_id])
