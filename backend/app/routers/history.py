from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AnalysisResult, ResearchIdea

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=List[dict])
def get_analysis_history(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Returns a list of previous research analyses with dates, ideas, and composite scores."""
    results = (
        db.query(AnalysisResult, ResearchIdea)
        .join(ResearchIdea, AnalysisResult.idea_id == ResearchIdea.id)
        .order_by(AnalysisResult.created_at.desc())
        .limit(limit)
        .all()
    )

    history_items = []
    for analysis, idea in results:
        composite = round(
            (analysis.academic_score * 0.3 + analysis.industry_score * 0.25 + analysis.societal_score * 0.25 + analysis.future_score * 0.2), 1
        )
        history_items.append({
            "analysis_id": analysis.id,
            "idea_id": idea.id,
            "idea": idea.idea_text,
            "domain": idea.domain,
            "keywords": idea.keywords,
            "total_papers": analysis.total_papers_analyzed,
            "deduplicated_papers": analysis.deduplicated_papers_count,
            "composite_score": composite,
            "academic_score": analysis.academic_score,
            "industry_score": analysis.industry_score,
            "societal_score": analysis.societal_score,
            "future_score": analysis.future_score,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        })

    return history_items


@router.get("/{analysis_id}", response_model=dict)
def get_history_detail(analysis_id: int, db: Session = Depends(get_db)):
    """Retrieves full metadata of a saved analysis."""
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    idea = db.query(ResearchIdea).filter(ResearchIdea.id == analysis.idea_id).first()
    return {
        "analysis_id": analysis.id,
        "idea": idea.idea_text if idea else "Unknown",
        "domain": idea.domain if idea else "General",
        "keywords": idea.keywords if idea else [],
        "academic_score": analysis.academic_score,
        "industry_score": analysis.industry_score,
        "societal_score": analysis.societal_score,
        "future_score": analysis.future_score,
        "evidence_academic": analysis.evidence_academic,
        "evidence_industry": analysis.evidence_industry,
        "evidence_societal": analysis.evidence_societal,
        "evidence_future": analysis.evidence_future,
        "explanation": analysis.explanation_narrative,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
    }


@router.delete("/{analysis_id}", response_model=dict)
def delete_history_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Deletes a saved analysis and removes its idea if it has no other analyses."""
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    idea_id = analysis.idea_id
    db.delete(analysis)
    db.flush()

    has_other_analyses = (
        db.query(AnalysisResult.id)
        .filter(AnalysisResult.idea_id == idea_id)
        .first()
    )
    if not has_other_analyses:
        idea = db.query(ResearchIdea).filter(ResearchIdea.id == idea_id).first()
        if idea:
            db.delete(idea)

    db.commit()
    return {"deleted": True, "analysis_id": analysis_id}
