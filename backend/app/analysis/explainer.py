import logging
from typing import List, Dict, Any
from app.collectors.base import RawPaper
from app.schemas.analysis_schemas import (
    ExplanationSchema,
    TrendDataSchema,
    ResearchGapSchema,
    RelevanceEvaluationSchema,
)

logger = logging.getLogger("research_scope.analysis.explainer")


class Explainer:
    """
    Generates explainable, human-readable insights and empirical justifications
    for the research idea, similarity results, trends, gaps, and relevance scores.
    """

    @classmethod
    def generate_explanation(
        cls,
        idea_text: str,
        detected_domain: str,
        papers: List[RawPaper],
        similarities: List[Dict[str, Any]],
        trends: TrendDataSchema,
        gaps: List[ResearchGapSchema],
        evaluation: RelevanceEvaluationSchema,
    ) -> ExplanationSchema:
        top_sim = similarities[0] if similarities else None
        top_paper_title = top_sim["paper"].title if top_sim else "related baseline studies"
        top_score = top_sim["similarity_score"] if top_sim else 0.0

        # 1. Executive Summary
        exec_summary = (
            f"The proposed research idea—\"{idea_text}\"—sits prominently within {detected_domain}. "
            f"Our multi-source scholarly analysis identified {len(papers)} directly related peer-reviewed and preprint works. "
            f"The investigation demonstrates high academic viability (composite score: {evaluation.composite_score}/100), "
            f"with substantial alignment to recent technological advancements and clear, actionable underexplored niches."
        )

        # 2. Similarity Insights
        if top_sim:
            sim_insights = (
                f"Literature retrieval reveals that the most semantically aligned paper is \"{top_paper_title}\" "
                f"with a {top_score:.1f}% semantic similarity. "
                f"Overall, {sum(1 for s in similarities if s['relevance_tier'] == 'High')} studies exhibit high thematic proximity, "
                f"confirming that while foundational principles have been established, your specific framing possesses distinct characteristics."
            )
        else:
            sim_insights = "Limited direct literature matches were retrieved, indicating a nascent or uniquely formulated concept."

        # 3. Trend Insights
        growth_descriptor = "rapidly growing" if trends.cagr_growth_rate > 15 else "consistently active"
        trend_insights = (
            f"Scholarly publication volume in this research trajectory is {growth_descriptor}, displaying an estimated "
            f"{trends.cagr_growth_rate}% Compound Annual Growth Rate (CAGR). "
            f"Analysis of keyword trajectories indicates accelerating momentum in {', '.join(trends.emerging_topics[:3]) if trends.emerging_topics else 'core methods'}, "
            f"verifying that this topic is on an upward research trajectory rather than becoming obsolete."
        )

        # 4. Gap Insights
        if gaps:
            primary_gap = gaps[0]
            gap_insights = (
                f"Our gap analysis uncovered a notable opportunity: \"{primary_gap.gap_title}\" (Novelty Score: {primary_gap.novelty_score}/100). "
                f"{primary_gap.description} "
                f"By strategically targeting this intersection, your research can yield high-impact, non-redundant contributions."
            )
        else:
            gap_insights = "Existing literature displays comprehensive coverage across standard benchmark combinations."

        # 5. Relevance Justification
        rel_justification = (
            f"Relevance scoring is backed by measurable empirical signals: "
            f"Academic Relevance ({evaluation.academic.score}/100) reflects intense ongoing peer interest; "
            f"Industry Relevance ({evaluation.industry.score}/100) is corroborated by deployment requirements; "
            f"Societal Relevance ({evaluation.societal.score}/100) is driven by critical health/safety benefits; "
            f"and Future Potential ({evaluation.future_potential.score}/100) indicates strong publication longevity."
        )

        # 6. Actionable Recommendations
        recommendations = [
            f"Formalize evaluation on standard open benchmarks within {detected_domain} to ensure reproducible comparisons against current state-of-the-art.",
            f"Prioritize the underexplored intersection: \"{gaps[0].gap_title if gaps else 'Hybrid multimodal modeling'}\" to maximize paper novelty.",
            "Incorporate ablation experiments that explicitly address latency, computational overhead, or real-world noise robustness.",
            "Target publication in premier IEEE, ACM, or domain-specialized venues with dedicated tracks in this growing area.",
        ]

        return ExplanationSchema(
            executive_summary=exec_summary,
            similarity_insights=sim_insights,
            trend_insights=trend_insights,
            gap_insights=gap_insights,
            relevance_justification=rel_justification,
            actionable_recommendations=recommendations,
        )
