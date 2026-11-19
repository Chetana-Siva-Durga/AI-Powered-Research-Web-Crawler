import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import (
    ResearchIdea,
    Paper,
    AnalysisResult,
    PaperSimilarity,
    ResearchGap,
    TopicTrend,
)
from app.schemas.analysis_schemas import (
    AnalysisRequest,
    AnalysisResponse,
    SimilarPaperSchema,
)
from app.collectors.manager import CollectorManager
from app.processing.deduplicator import Deduplicator
from app.processing.cleaner import TextCleaner
from app.nlp.domain_detector import DomainDetector
from app.nlp.keywords_ner import KeywordsAndNER
from app.nlp.similarity import SimilarityAnalyzer
from app.analysis.trend_analyzer import TrendAnalyzer
from app.analysis.gap_analyzer import GapAnalyzer
from app.analysis.relevance_evaluator import RelevanceEvaluator
from app.analysis.explainer import Explainer

logger = logging.getLogger("research_scope.routers.analyze")
router = APIRouter(prefix="", tags=["Analysis"])

collector_manager = CollectorManager()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_research_idea(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Core Research Scope Pipeline:
    1. Validates idea and extracts domain & keywords
    2. Collects research papers concurrently from scholarly APIs + Web Crawler
    3. Cleans, normalizes, and deduplicates papers
    4. Persists records in MySQL / SQLite database
    5. Runs NLP Semantic Similarity analysis
    6. Conducts Trend Analysis and Gap Discovery
    7. Evaluates Multi-Dimensional Relevance (Academic, Industry, Society, Future)
    8. Synthesizes human-readable explanations and returns comprehensive dashboard data
    """
    if not request.idea or len(request.idea.strip()) < 5:
        raise HTTPException(status_code=400, detail="Please provide a valid research idea (minimum 5 characters).")

    idea_text = request.idea.strip()
    logger.info("Initiating research analysis for: '%s'", idea_text[:60])

    # 1. Domain Detection and Keyword Extraction
    detected_domain, domain_conf, subdomains = DomainDetector.detect(idea_text, user_hint=request.domain)

    extracted_keywords = KeywordsAndNER.extract_keywords(idea_text, top_k=6)
    
    # Merge user keywords with extracted keywords
    all_keywords = list(request.keywords or [])
    for kw in extracted_keywords:
        if kw not in all_keywords:
            all_keywords.append(kw)

    # 2. Scholarly Data Collection (APIs + Web Crawler)
    collection_result = await collector_manager.collect_all(
        query=idea_text,
        keywords=all_keywords,
        sources=request.sources,
        limit_per_source=max(8, request.max_papers // len(request.sources or [1])),
    )
    raw_papers = collection_result["papers"]
    source_breakdown = collection_result["breakdown"]

    # 3. Data Processing: Cleaning + Deduplication
    unique_papers, duplicates_removed = Deduplicator.deduplicate(raw_papers)
    logger.info("Corpus ready: %d unique papers (%d duplicates purged)", len(unique_papers), duplicates_removed)

    # 4. Database Persistence (ResearchIdea)
    idea_record = ResearchIdea(
        idea_text=idea_text,
        domain=detected_domain,
        keywords=all_keywords,
        created_at=datetime.utcnow(),
    )
    db.add(idea_record)
    db.commit()
    db.refresh(idea_record)

    # Persist or retrieve existing papers in database
    db_paper_map = {}
    for p in unique_papers:
        norm_t = TextCleaner.normalize_title(p.title)
        existing_p = db.query(Paper).filter(Paper.normalized_title == norm_t).first()
        if not existing_p:
            new_p = Paper(
                doi=p.doi,
                title=p.title,
                normalized_title=norm_t,
                abstract=p.abstract,
                authors=p.authors,
                publication_year=p.year,
                venue=p.venue,
                citations=p.citations,
                source=p.source,
                url=p.url,
                keywords=p.keywords,
            )
            db.add(new_p)
            db.commit()
            db.refresh(new_p)
            db_paper_map[norm_t] = new_p
        else:
            db_paper_map[norm_t] = existing_p

    # 5. AI/NLP Engine: Semantic Similarity
    similarities = SimilarityAnalyzer.compute_similarity(
        idea_text=idea_text,
        papers=unique_papers,
        idea_keywords=all_keywords,
    )

    # 6. Trend Analysis
    trends = TrendAnalyzer.analyze(papers=unique_papers, query_keywords=all_keywords)

    # 7. Research Gap Analysis
    gaps = GapAnalyzer.analyze(
        idea_text=idea_text,
        papers=unique_papers,
        idea_keywords=all_keywords,
    )

    # 8. Multi-Dimensional Relevance Evaluation
    evaluation = RelevanceEvaluator.evaluate(
        idea_text=idea_text,
        papers=unique_papers,
        similarities=similarities,
        trends=trends,
        gaps=gaps,
        detected_domain=detected_domain,
    )

    # 9. Explainability & Insights
    explanation = Explainer.generate_explanation(
        idea_text=idea_text,
        detected_domain=detected_domain,
        papers=unique_papers,
        similarities=similarities,
        trends=trends,
        gaps=gaps,
        evaluation=evaluation,
    )

    # 10. Persist Analysis Results in Database
    analysis_record = AnalysisResult(
        idea_id=idea_record.id,
        total_papers_analyzed=len(raw_papers),
        deduplicated_papers_count=len(unique_papers),
        academic_score=evaluation.academic.score,
        industry_score=evaluation.industry.score,
        societal_score=evaluation.societal.score,
        future_score=evaluation.future_potential.score,
        evidence_academic=evaluation.academic.evidence,
        evidence_industry=evaluation.industry.evidence,
        evidence_societal=evaluation.societal.evidence,
        evidence_future=evaluation.future_potential.evidence,
        explanation_narrative=explanation.executive_summary,
        created_at=datetime.utcnow(),
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    # Save Top Similar Papers associations in DB
    similar_paper_schemas: list[SimilarPaperSchema] = []
    for sim_item in similarities[:25]:
        p = sim_item["paper"]
        norm_t = TextCleaner.normalize_title(p.title)
        db_p = db_paper_map.get(norm_t)
        if db_p:
            sim_db = PaperSimilarity(
                analysis_id=analysis_record.id,
                paper_id=db_p.id,
                similarity_score=sim_item["similarity_score"],
                rank=sim_item["rank"],
                relevance_tier=sim_item["relevance_tier"],
                matching_concepts=sim_item["matching_concepts"],
            )
            db.add(sim_db)

            similar_paper_schemas.append(SimilarPaperSchema(
                id=db_p.id,
                title=p.title,
                abstract=p.abstract,
                authors=p.authors,
                publication_year=p.year,
                venue=p.venue,
                citations=p.citations,
                source=p.source,
                url=p.url,
                doi=p.doi,
                similarity_score=sim_item["similarity_score"],
                rank=sim_item["rank"],
                relevance_tier=sim_item["relevance_tier"],
                matching_concepts=sim_item["matching_concepts"],
            ))

    # Save Gaps in DB
    for g in gaps:
        db_gap = ResearchGap(
            analysis_id=analysis_record.id,
            gap_title=g.gap_title,
            concept_a=g.concept_a,
            concept_b=g.concept_b,
            co_occurrence_count=g.co_occurrence_count,
            novelty_score=g.novelty_score,
            description=g.description,
            suggested_direction=g.suggested_direction,
        )
        db.add(db_gap)

    # Save Trends in DB
    for y_trend in trends.yearly_distribution:
        db_trend = TopicTrend(
            analysis_id=analysis_record.id,
            topic_or_keyword=detected_domain,
            year=y_trend.year,
            paper_count=y_trend.count,
            growth_rate=trends.cagr_growth_rate,
            is_emerging=y_trend.year >= 2024,
        )
        db.add(db_trend)

    db.commit()

    return AnalysisResponse(
        analysis_id=analysis_record.id,
        idea_id=idea_record.id,
        idea=idea_text,
        detected_domain=detected_domain,
        keywords=all_keywords,
        total_papers_collected=len(raw_papers),
        deduplicated_papers_count=len(unique_papers),
        sources_breakdown=source_breakdown,
        similar_papers=similar_paper_schemas,
        trends=trends,
        gaps=gaps,
        evaluation=evaluation,
        explanation=explanation,
        created_at=datetime.utcnow().isoformat(),
    )
