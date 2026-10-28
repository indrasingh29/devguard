from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.feedback import ReviewFeedback
    from app.models.review_job import ReviewJob

class Finding(Base, TimestampMixin):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    review_job_id: Mapped[int] = mapped_column(Integer, ForeignKey("review_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    line_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    line_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # critical, high, medium, low, info
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # security, bug_risk, error_handling, maintainability, test_insufficiency, secret_leak
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    suggested_remediation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detection_source: Mapped[str] = mapped_column(String(50), nullable=False)  # deterministic, bandit, ast_check, regex_secret, llm_suggestion
    confidence: Mapped[str] = mapped_column(String(50), default="high")  # deterministic, high, medium, low
    rule_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    review_job: Mapped["ReviewJob"] = relationship("ReviewJob", back_populates="findings")
    feedback: Mapped[List["ReviewFeedback"]] = relationship(
        "ReviewFeedback", back_populates="finding", cascade="all, delete-orphan"
    )
