from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class ResearchIdea(Base):
    __tablename__ = "research_ideas"

    id = Column(Integer, primary_key=True, index=True)
    idea_text = Column(Text, nullable=False)
    domain = Column(String(100), default="General Computer Science", index=True)
    keywords = Column(JSON, default=list)  # list of strings
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    analyses = relationship("AnalysisResult", back_populates="idea", cascade="all, delete-orphan")


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    doi = Column(String(255), index=True, nullable=True)
    title = Column(Text, nullable=False)
    normalized_title = Column(String(500), index=True, nullable=False)
    abstract = Column(Text, nullable=True)
    authors = Column(JSON, default=list)  # list of author names
    publication_year = Column(Integer, index=True, nullable=True)
    venue = Column(String(255), nullable=True)
    citations = Column(Integer, default=0)
    source = Column(String(100), default="unknown", index=True)  # openalex, arxiv, pubmed, crawler, etc.
    url = Column(String(1000), nullable=True)
    keywords = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    similarities = relationship("PaperSimilarity", back_populates="paper")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("research_ideas.id"), nullable=False)
    total_papers_analyzed = Column(Integer, default=0)
    deduplicated_papers_count = Column(Integer, default=0)

    # Multi-dimensional scores (0 to 100)
    academic_score = Column(Float, default=0.0)
    industry_score = Column(Float, default=0.0)
    societal_score = Column(Float, default=0.0)
    future_score = Column(Float, default=0.0)

    # Evidence lists (JSON arrays of rationale strings)
    evidence_academic = Column(JSON, default=list)
    evidence_industry = Column(JSON, default=list)
    evidence_societal = Column(JSON, default=list)
    evidence_future = Column(JSON, default=list)

    # Explainable narrative
    explanation_narrative = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    idea = relationship("ResearchIdea", back_populates="analyses")
    similar_papers = relationship("PaperSimilarity", back_populates="analysis", cascade="all, delete-orphan")
    gaps = relationship("ResearchGap", back_populates="analysis", cascade="all, delete-orphan")
    trends = relationship("TopicTrend", back_populates="analysis", cascade="all, delete-orphan")


class PaperSimilarity(Base):
    __tablename__ = "paper_similarities"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)  # 0.0 - 100.0%
    rank = Column(Integer, default=1)
    relevance_tier = Column(String(50), default="Medium")  # High, Medium, Low
    matching_concepts = Column(JSON, default=list)

    # Relationships
    analysis = relationship("AnalysisResult", back_populates="similar_papers")
    paper = relationship("Paper", back_populates="similarities")


class ResearchGap(Base):
    __tablename__ = "research_gaps"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False)
    gap_title = Column(String(255), nullable=False)
    concept_a = Column(String(100), nullable=True)
    concept_b = Column(String(100), nullable=True)
    co_occurrence_count = Column(Integer, default=0)
    individual_a_count = Column(Integer, default=0)
    individual_b_count = Column(Integer, default=0)
    novelty_score = Column(Float, default=0.0)
    description = Column(Text, nullable=False)
    suggested_direction = Column(Text, nullable=True)

    # Relationships
    analysis = relationship("AnalysisResult", back_populates="gaps")


class TopicTrend(Base):
    __tablename__ = "topic_trends"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False)
    topic_or_keyword = Column(String(150), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    paper_count = Column(Integer, default=0)
    growth_rate = Column(Float, default=0.0)
    is_emerging = Column(Boolean, default=False)

    # Relationships
    analysis = relationship("AnalysisResult", back_populates="trends")


class UserDataset(Base):
    __tablename__ = "user_datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    records_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
