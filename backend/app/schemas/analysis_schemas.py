from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    idea: str = Field(..., description="The user's research idea or question")
    domain: Optional[str] = Field(default="Auto-detect", description="Optional selected domain")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Optional user keywords")
    sources: Optional[List[str]] = Field(
        default=["openalex", "semanticscholar", "crossref", "arxiv", "pubmed", "crawler"],
        description="Sources to query"
    )
    max_papers: Optional[int] = Field(default=50, description="Max papers to collect across sources")


class SimilarPaperSchema(BaseModel):
    id: int
    title: str
    abstract: Optional[str] = None
    authors: List[str] = []
    publication_year: Optional[int] = None
    venue: Optional[str] = None
    citations: int = 0
    source: str = "unknown"
    url: Optional[str] = None
    doi: Optional[str] = None
    similarity_score: float = 0.0  # percentage (0 - 100)
    rank: int = 1
    relevance_tier: str = "Medium"  # High, Medium, Low
    matching_concepts: List[str] = []


class YearlyTrendSchema(BaseModel):
    year: int
    count: int


class KeywordTrajectorySchema(BaseModel):
    keyword: str
    trajectory: Dict[int, int]  # year -> count
    total_count: int
    is_emerging: bool


class TrendDataSchema(BaseModel):
    yearly_distribution: List[YearlyTrendSchema] = []
    keyword_trajectories: List[KeywordTrajectorySchema] = []
    top_keywords: List[str] = []
    emerging_topics: List[str] = []
    mature_topics: List[str] = []
    cagr_growth_rate: float = 0.0


class ResearchGapSchema(BaseModel):
    id: Optional[int] = None
    gap_title: str
    concept_a: Optional[str] = None
    concept_b: Optional[str] = None
    co_occurrence_count: int = 0
    novelty_score: float = 0.0  # 0 to 100
    description: str
    suggested_direction: Optional[str] = None
    feasibility: Optional[str] = "High"


class RelevanceScoreDetail(BaseModel):
    score: float
    level: str  # High, Medium, Moderate, etc.
    evidence: List[str] = []


class RelevanceEvaluationSchema(BaseModel):
    academic: RelevanceScoreDetail
    industry: RelevanceScoreDetail
    societal: RelevanceScoreDetail
    future_potential: RelevanceScoreDetail
    composite_score: float
    novelty_score: float = 0.0          # 0-100: how unexplored is this idea
    capstone_score: float = 0.0         # 0-100: suitability for a student capstone project
    highlight_line: str = ""            # one-line punchy recommendation
    capstone_verdict: str = ""          # "Excellent" | "Good" | "Moderate" | "Challenging"


class ExplanationSchema(BaseModel):
    executive_summary: str
    similarity_insights: str
    trend_insights: str
    gap_insights: str
    relevance_justification: str
    actionable_recommendations: List[str] = []


class AnalysisResponse(BaseModel):
    analysis_id: int
    idea_id: int
    idea: str
    detected_domain: str
    keywords: List[str]
    total_papers_collected: int
    deduplicated_papers_count: int
    sources_breakdown: Dict[str, int]
    similar_papers: List[SimilarPaperSchema]
    trends: TrendDataSchema
    gaps: List[ResearchGapSchema]
    evaluation: RelevanceEvaluationSchema
    explanation: ExplanationSchema
    created_at: str



class UploadResponse(BaseModel):
    success: bool
    filename: str
    file_type: str
    records_extracted: int
    sample_titles: List[str] = []
    message: str
