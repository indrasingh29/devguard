from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.finding import Finding
from app.schemas.finding import FindingCategory, FindingResponse, SeverityLevel

router = APIRouter(tags=["Findings"])

@router.get("/reviews/{job_id}/findings", response_model=List[FindingResponse])
def get_job_findings(
    job_id: int,
    severity: Optional[SeverityLevel] = Query(None),
    category: Optional[FindingCategory] = Query(None),
    detection_source: Optional[str] = Query(None),
    file_path: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    stmt = select(Finding).where(Finding.review_job_id == job_id)

    if severity:
        stmt = stmt.where(Finding.severity == severity)
    if category:
        stmt = stmt.where(Finding.category == category)
    if detection_source:
        stmt = stmt.where(Finding.detection_source == detection_source)
    if file_path:
        stmt = stmt.where(Finding.file_path.ilike(f"%{file_path}%"))

    findings = db.scalars(stmt).all()
    results = []
    for f in findings:
        feedback_type = f.feedback[0].feedback_type if f.feedback else None
        resp = FindingResponse.model_validate(f)
        resp.feedback_type = feedback_type
        results.append(resp)

    return results

@router.get("/findings/{finding_id}", response_model=FindingResponse)
def get_finding_by_id(finding_id: int, db: Session = Depends(get_db)):
    finding = db.scalar(select(Finding).where(Finding.id == finding_id))
    if not finding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    feedback_type = finding.feedback[0].feedback_type if finding.feedback else None
    resp = FindingResponse.model_validate(finding)
    resp.feedback_type = feedback_type
    return resp
