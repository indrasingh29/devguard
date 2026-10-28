from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.finding import Finding

class ReviewFeedback(Base, TimestampMixin):
    __tablename__ = "review_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    finding_id: Mapped[int] = mapped_column(Integer, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False)  # helpful, false_positive, ignored
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    finding: Mapped["Finding"] = relationship("Finding", back_populates="feedback")
