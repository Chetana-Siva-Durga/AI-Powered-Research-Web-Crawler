from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.models import Paper

router = APIRouter(prefix="/papers", tags=["Papers"])


@router.get("", response_model=List[dict])
def list_papers(
    q: Optional[str] = Query(None, description="Search query string"),
    source: Optional[str] = Query(None, description="Filter by source"),
    year: Optional[int] = Query(None, description="Filter by year"),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Paper)
    if q:
        query = query.filter(
            or_(
                Paper.title.ilike(f"%{q}%"),
                Paper.abstract.ilike(f"%{q}%"),
            )
        )
    if source:
        query = query.filter(Paper.source.ilike(f"%{source}%"))
    if year:
        query = query.filter(Paper.publication_year == year)

    papers = query.order_by(Paper.publication_year.desc().nullslast()).offset(offset).limit(limit).all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "abstract": p.abstract,
            "authors": p.authors,
            "publication_year": p.publication_year,
            "venue": p.venue,
            "citations": p.citations,
            "source": p.source,
            "url": p.url,
            "doi": p.doi,
        }
        for p in papers
    ]


@router.get("/{paper_id}", response_model=dict)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return {
        "id": paper.id,
        "title": paper.title,
        "abstract": paper.abstract,
        "authors": paper.authors,
        "publication_year": paper.publication_year,
        "venue": paper.venue,
        "citations": paper.citations,
        "source": paper.source,
        "url": paper.url,
        "doi": paper.doi,
        "keywords": paper.keywords,
    }
