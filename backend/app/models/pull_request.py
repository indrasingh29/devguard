from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.review_job import ReviewJob

class PullRequest(Base, TimestampMixin):
    __tablename__ = "pull_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    repository_id: Mapped[int] = mapped_column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="open")  # open, closed, merged
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    base_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    head_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    html_url: Mapped[str] = mapped_column(String(500), nullable=False)
    diff_url: Mapped[str] = mapped_column(String(500), nullable=False)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="pull_requests")
    review_jobs: Mapped[List["ReviewJob"]] = relationship(
        "ReviewJob", back_populates="pull_request", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("repository_id", "number", name="uq_repo_pr_number"),
    )
