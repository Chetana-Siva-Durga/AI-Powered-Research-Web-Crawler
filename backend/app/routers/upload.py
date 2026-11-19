import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import UserDataset, Paper
from app.schemas.analysis_schemas import UploadResponse
from app.processing.document_parser import DocumentParser
from app.processing.cleaner import TextCleaner

logger = logging.getLogger("research_scope.routers.upload")
router = APIRouter(prefix="", tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_research_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse research datasets (CSV, XLSX, JSON) or research papers (PDF, TXT).
    Extracted papers are ingested and made immediately available for research analysis.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    ext = file.filename.split(".")[-1].lower()
    papers = DocumentParser.parse_file(file.filename, content)

    if not papers:
        raise HTTPException(
            status_code=422,
            detail=f"Could not parse valid research records from '{file.filename}'. Supported formats: CSV, XLSX, JSON, PDF, TXT."
        )

    # Persist dataset record
    dataset_entry = UserDataset(
        filename=file.filename,
        file_type=ext,
        records_count=len(papers),
    )
    db.add(dataset_entry)
    db.commit()

    # Ingest parsed papers into Paper table
    ingested_count = 0
    for p in papers:
        norm_t = TextCleaner.normalize_title(p.title)
        existing = db.query(Paper).filter(Paper.normalized_title == norm_t).first()
        if not existing:
            new_p = Paper(
                doi=p.doi,
                title=p.title,
                normalized_title=norm_t,
                abstract=p.abstract,
                authors=p.authors,
                publication_year=p.year,
                venue=p.venue,
                citations=p.citations,
                source=f"upload:{file.filename}",
                url=p.url,
                keywords=p.keywords,
            )
            db.add(new_p)
            ingested_count += 1

    db.commit()
    logger.info("Uploaded '%s': parsed %d papers (%d new inserted into database)", 
                file.filename, len(papers), ingested_count)

    sample_titles = [p.title for p in papers[:5]]

    return UploadResponse(
        success=True,
        filename=file.filename,
        file_type=ext,
        records_extracted=len(papers),
        sample_titles=sample_titles,
        message=f"Successfully extracted {len(papers)} research records from '{file.filename}'.",
    )
