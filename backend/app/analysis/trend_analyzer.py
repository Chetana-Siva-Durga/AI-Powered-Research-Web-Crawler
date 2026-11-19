import logging
from collections import defaultdict
from typing import List, Dict, Any
from app.collectors.base import RawPaper
from app.schemas.analysis_schemas import TrendDataSchema, YearlyTrendSchema, KeywordTrajectorySchema
from app.nlp.keywords_ner import KeywordsAndNER

logger = logging.getLogger("research_scope.analysis.trend_analyzer")


class TrendAnalyzer:
    """
    Analyzes temporal trends, publication growth velocities,
    keyword trajectories, and emerging vs mature technologies.
    """

    @classmethod
    def analyze(cls, papers: List[RawPaper], query_keywords: List[str] = None) -> TrendDataSchema:
        if not papers:
            return TrendDataSchema()

        # 1. Yearly distribution
        year_counts: Dict[int, int] = defaultdict(int)
        current_year = 2026
        valid_years = []

        for p in papers:
            if p.year and 2000 <= p.year <= current_year:
                year_counts[p.year] += 1
                valid_years.append(p.year)

        # Fallback/smooth distribution if years are scarce
        if not valid_years:
            # Default spread over last 5 years
            for y in range(current_year - 4, current_year + 1):
                year_counts[y] = 1
            valid_years = list(year_counts.keys())

        min_year = max(2018, min(valid_years))
        max_year = max(valid_years)
        
        # Ensure contiguous yearly representation
        yearly_distribution: List[YearlyTrendSchema] = []
        for y in range(min_year, max_year + 1):
            yearly_distribution.append(YearlyTrendSchema(year=y, count=year_counts.get(y, 0)))

        # 2. Calculate CAGR / Growth Velocity
        start_count = year_counts.get(min_year, 1) or 1
        end_count = year_counts.get(max_year, 1) or 1
        num_years = max(1, max_year - min_year)
        try:
            cagr = ((end_count / start_count) ** (1.0 / num_years) - 1.0) * 100
            cagr = round(max(-50.0, min(150.0, cagr)), 1)
        except Exception:
            cagr = 15.0

        # 3. Top Keywords and Trajectories over time
        all_abstracts = [(p.title + " " + (p.abstract or "")) for p in papers]
        top_corpus_keywords = KeywordsAndNER.extract_corpus_top_keywords(all_abstracts, top_k=8)
        if query_keywords:
            for qk in query_keywords:
                if qk.title() not in top_corpus_keywords:
                    top_corpus_keywords.insert(0, qk.title())
        top_corpus_keywords = top_corpus_keywords[:6]

        keyword_year_matrix: Dict[str, Dict[int, int]] = {k: defaultdict(int) for k in top_corpus_keywords}
        for p in papers:
            p_year = p.year if (p.year and min_year <= p.year <= max_year) else max_year
            text = (p.title + " " + (p.abstract or "")).lower()
            for kw in top_corpus_keywords:
                if kw.lower() in text:
                    keyword_year_matrix[kw][p_year] += 1

        keyword_trajectories: List[KeywordTrajectorySchema] = []
        emerging_topics: List[str] = []
        mature_topics: List[str] = []

        for kw, years_dict in keyword_year_matrix.items():
            total_k_count = sum(years_dict.values())
            # Recent count (last 2 years) vs earlier count
            recent_count = sum(years_dict.get(y, 0) for y in (max_year, max_year - 1))
            earlier_count = sum(years_dict.get(y, 0) for y in range(min_year, max_year - 1))

            is_emerging = recent_count >= earlier_count or total_k_count >= 3
            if is_emerging:
                emerging_topics.append(kw)
            else:
                mature_topics.append(kw)

            keyword_trajectories.append(KeywordTrajectorySchema(
                keyword=kw,
                trajectory={y: years_dict.get(y, 0) for y in range(min_year, max_year + 1)},
                total_count=total_k_count,
                is_emerging=is_emerging,
            ))

        if not emerging_topics and top_corpus_keywords:
            emerging_topics = top_corpus_keywords[:2]

        return TrendDataSchema(
            yearly_distribution=yearly_distribution,
            keyword_trajectories=keyword_trajectories,
            top_keywords=top_corpus_keywords,
            emerging_topics=emerging_topics,
            mature_topics=mature_topics,
            cagr_growth_rate=cagr,
        )
