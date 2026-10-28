from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.feedback import ReviewFeedback
from app.models.finding import Finding
from app.schemas.feedback import FeedbackCreateRequest, FeedbackResponse

router = APIRouter(prefix="/findings", tags=["Finding Feedback"])

@router.post("/{finding_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_finding_feedback(
    finding_id: int,
    req: FeedbackCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Submit user feedback on a finding (helpful, false_positive, ignored) to audit quality.
    """
    finding = db.scalar(select(Finding).where(Finding.id == finding_id))
    if not finding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    existing_feedback = db.scalar(select(ReviewFeedback).where(ReviewFeedback.finding_id == finding_id))
    if existing_feedback:
        existing_feedback.feedback_type = req.feedback_type
        existing_feedback.comment = req.comment
        db.commit()
        db.refresh(existing_feedback)
        return existing_feedback

    new_feedback = ReviewFeedback(
        finding_id=finding_id,
        feedback_type=req.feedback_type,
        comment=req.comment,
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback
