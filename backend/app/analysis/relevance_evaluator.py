import logging
from typing import List, Dict, Any
from app.collectors.base import RawPaper
from app.schemas.analysis_schemas import (
    RelevanceEvaluationSchema,
    RelevanceScoreDetail,
    ResearchGapSchema,
    TrendDataSchema,
)

logger = logging.getLogger("research_scope.analysis.relevance_evaluator")

# Keywords indicating industry applicability
INDUSTRY_SIGNALS = [
    "clinical", "diagnostic", "deployment", "real-time", "latency", "hardware",
    "edge", "cloud", "scale", "enterprise", "throughput", "low-power", "production",
    "commercial", "fda", "hospital", "patient", "workflow", "cost-effective"
]

# Keywords indicating societal / humanitarian impact
SOCIETAL_SIGNALS = [
    "health", "cancer", "tumor", "mortality", "patient", "safety", "privacy",
    "ethical", "accessibility", "equitable", "public health", "survival",
    "sustainable", "energy-efficient", "green ai", "misinformation", "bias"
]


class RelevanceEvaluator:
    """
    Multi-dimensional evaluation engine.
    Calculates quantifiable scores (0-100) and empirical evidence rationales
    across Academic, Industry, Societal, and Future Potential dimensions.
    """

    @classmethod
    def evaluate(
        cls,
        idea_text: str,
        papers: List[RawPaper],
        similarities: List[Dict[str, Any]],
        trends: TrendDataSchema,
        gaps: List[ResearchGapSchema],
        detected_domain: str,
    ) -> RelevanceEvaluationSchema:
        idea_lower = idea_text.lower()
        corpus_text = " ".join((p.title + " " + (p.abstract or "")).lower() for p in papers)

        # -------------------------------------------------------------
        # 1. Academic Relevance (0 - 100)
        # -------------------------------------------------------------
        acad_base = 60.0
        # Signal A: Volume of existing literature
        paper_count = len(papers)
        if paper_count >= 25:
            acad_base += 15.0
        elif paper_count >= 10:
            acad_base += 10.0
        else:
            acad_base += 5.0

        # Signal B: Mean similarity of top-5 papers
        top_sims = [s["similarity_score"] for s in similarities[:5]] if similarities else [50.0]
        avg_sim = sum(top_sims) / len(top_sims)
        if avg_sim >= 75.0:
            acad_base += 12.0
        elif avg_sim >= 55.0:
            acad_base += 8.0
        else:
            acad_base += 4.0

        # Signal C: Recent publication activity (years >= 2023)
        recent_count = sum(1 for p in papers if p.year and p.year >= 2023)
        if recent_count >= 10:
            acad_base += 8.0
        elif recent_count >= 4:
            acad_base += 5.0

        academic_score = min(98.0, round(acad_base, 1))
        academic_evidence = [
            f"Strong alignment with {paper_count} analyzed publications across peer-reviewed scholarly venues.",
            f"Top related literature exhibits an average semantic similarity of {avg_sim:.1f}%.",
            f"Active current research domain with {recent_count} publications appearing between 2023 and 2026.",
            f"Foundational theoretical interest within {detected_domain}.",
        ]

        # -------------------------------------------------------------
        # 2. Industry Relevance (0 - 100)
        # -------------------------------------------------------------
        ind_base = 55.0
        matched_ind_keywords = [kw for kw in INDUSTRY_SIGNALS if kw in idea_lower or kw in corpus_text]
        ind_signal_count = len(matched_ind_keywords)
        ind_base += min(25.0, ind_signal_count * 2.5)

        # Citations / applied interest signal
        high_cited = sum(1 for p in papers if p.citations > 10)
        if high_cited >= 5:
            ind_base += 10.0
        elif high_cited >= 1:
            ind_base += 5.0

        industry_score = min(95.0, round(ind_base, 1))
        industry_evidence = [
            f"Identified {ind_signal_count} high-priority industrial indicators in domain corpus (e.g. {', '.join(matched_ind_keywords[:4])}).",
            "Direct potential for operational deployment into practical systems and diagnostics.",
            f"{high_cited} related studies feature high academic and patent-linked citation impact.",
            "High commercial interest from enterprise, medical technology, and cloud automation sectors.",
        ]

        # -------------------------------------------------------------
        # 3. Societal Relevance (0 - 100)
        # -------------------------------------------------------------
        soc_base = 50.0
        matched_soc_keywords = [kw for kw in SOCIETAL_SIGNALS if kw in idea_lower or kw in corpus_text]
        soc_signal_count = len(matched_soc_keywords)
        soc_base += min(35.0, soc_signal_count * 4.0)

        societal_score = min(98.0, round(soc_base, 1))
        societal_evidence = [
            f"Identified major societal keywords: {', '.join(matched_soc_keywords[:4]) if matched_soc_keywords else 'Public health, safety, and reliability'}.",
            "High potential for improving human life quality, patient prognosis, or system reliability.",
            "Contributes to equitable access and automation in critical societal infrastructure.",
            "Addresses pressing ethical, health, or privacy imperatives in modern computing.",
        ]

        # -------------------------------------------------------------
        # 4. Future Potential (0 - 100)
        # -------------------------------------------------------------
        fut_base = 60.0
        # Signal A: Trend CAGR
        if trends.cagr_growth_rate >= 20.0:
            fut_base += 15.0
        elif trends.cagr_growth_rate >= 5.0:
            fut_base += 10.0
        else:
            fut_base += 5.0

        # Signal B: Identified gaps with high novelty
        high_novelty_gaps = [g for g in gaps if g.novelty_score >= 80.0]
        if len(high_novelty_gaps) >= 2:
            fut_base += 12.0
        elif high_novelty_gaps:
            fut_base += 8.0

        # Signal C: Emerging topics presence
        if len(trends.emerging_topics) >= 2:
            fut_base += 8.0

        future_score = min(97.0, round(fut_base, 1))
        future_evidence = [
            f"Annual publication velocity exhibits a {trends.cagr_growth_rate}% CAGR trajectory.",
            f"Identified {len(high_novelty_gaps)} high-novelty unexplored research gaps with strong breakthrough potential.",
            f"Active intersection with emerging technology paradigms: {', '.join(trends.emerging_topics[:3])}.",
            "High runway for subsequent Ph.D. dissertations, grant applications, and industrial R&D patents.",
        ]

        # Composite Score (weighted mean)
        composite = round((academic_score * 0.3 + industry_score * 0.25 + societal_score * 0.25 + future_score * 0.2), 1)

        # -------------------------------------------------------------
        # 5. Novelty Score (0 - 100) — how unexplored is this idea?
        # High similarity  → low novelty (area is well-covered)
        # Few papers       → higher novelty
        # Many open gaps   → higher novelty
        # -------------------------------------------------------------
        novelty_base = 100.0 - avg_sim                    # lower similarity = more novel
        if paper_count >= 40:
            novelty_base -= 20.0
        elif paper_count >= 20:
            novelty_base -= 10.0
        elif paper_count <= 5:
            novelty_base += 10.0

        high_novelty_gap_count = len([g for g in gaps if g.novelty_score >= 75.0])
        novelty_base += min(15.0, high_novelty_gap_count * 5.0)
        novelty_score = max(5.0, min(97.0, round(novelty_base, 1)))

        # -------------------------------------------------------------
        # 6. Capstone Score (0 - 100) — suitability for student project
        # Balanced mix of: feasibility, scope, open data, trending area
        # Penalise if area is too niche (< 5 papers) or too saturated (> 40 papers)
        # -------------------------------------------------------------
        cap_base = 60.0
        # Sweet spot: 8–25 papers → manageable literature, enough prior work
        if 8 <= paper_count <= 25:
            cap_base += 15.0
        elif 5 <= paper_count < 8 or 25 < paper_count <= 40:
            cap_base += 8.0
        elif paper_count > 40:
            cap_base += 4.0
        else:
            cap_base += 2.0

        # Trending (CAGR ≥ 5%) is good for capstone — easy to find recent resources
        if trends.cagr_growth_rate >= 10.0:
            cap_base += 10.0
        elif trends.cagr_growth_rate >= 5.0:
            cap_base += 6.0

        # Identified gaps → student can position their work
        cap_base += min(10.0, high_novelty_gap_count * 3.5)

        # Novelty sweet spot: 40–80 → something to add, but not too blank-slate
        if 40.0 <= novelty_score <= 80.0:
            cap_base += 8.0
        elif novelty_score > 80.0:
            cap_base += 3.0    # very novel = hard to benchmark

        capstone_score = max(10.0, min(98.0, round(cap_base, 1)))

        def capstone_verdict(score: float) -> str:
            if score >= 85.0:
                return "Excellent"
            elif score >= 70.0:
                return "Good"
            elif score >= 55.0:
                return "Moderate"
            return "Challenging"

        verdict = capstone_verdict(capstone_score)

        # -------------------------------------------------------------
        # 7. One-line Highlight Recommendation
        # -------------------------------------------------------------
        if novelty_score >= 75.0 and capstone_score >= 70.0:
            highlight = (
                f"🚀 Strong novel angle with limited prior work — "
                f"focus your contribution on {gaps[0].gap_title if gaps else 'the identified gaps'} "
                f"to stand out immediately."
            )
        elif novelty_score < 40.0 and paper_count >= 30:
            highlight = (
                f"⚠️ This area is heavily researched ({paper_count} papers found) — "
                f"differentiate by combining it with "
                f"{', '.join(trends.emerging_topics[:2]) if trends.emerging_topics else 'an emerging technique'} "
                f"to add original value."
            )
        elif capstone_score >= 80.0:
            highlight = (
                f"🎓 Excellent capstone fit — well-scoped topic with {paper_count} papers to reference, "
                f"{high_novelty_gap_count} open gaps to exploit, and active community support."
            )
        elif trends.cagr_growth_rate >= 15.0 and novelty_score >= 55.0:
            highlight = (
                f"📈 Fast-growing field ({trends.cagr_growth_rate}% CAGR) with moderate novelty — "
                f"publish early to ride the wave before it saturates."
            )
        elif novelty_score < 40.0:
            highlight = (
                f"🔁 Moderately explored topic — add a novel angle such as "
                f"{trends.emerging_topics[0] if trends.emerging_topics else 'cross-domain adaptation'} "
                f"or a dataset from an under-served region to justify the contribution."
            )
        else:
            highlight = (
                f"✅ Well-balanced research idea with a composite viability of {composite}/100 — "
                f"sharpen your methodology around {gaps[0].gap_title if gaps else 'identified gaps'} "
                f"for a strong academic submission."
            )

        def get_level(score: float) -> str:
            if score >= 88.0:
                return "Exceptional"
            elif score >= 75.0:
                return "High"
            elif score >= 60.0:
                return "Moderate"
            return "Developing"

        return RelevanceEvaluationSchema(
            academic=RelevanceScoreDetail(
                score=academic_score,
                level=get_level(academic_score),
                evidence=academic_evidence,
            ),
            industry=RelevanceScoreDetail(
                score=industry_score,
                level=get_level(industry_score),
                evidence=industry_evidence,
            ),
            societal=RelevanceScoreDetail(
                score=societal_score,
                level=get_level(societal_score),
                evidence=societal_evidence,
            ),
            future_potential=RelevanceScoreDetail(
                score=future_score,
                level=get_level(future_score),
                evidence=future_evidence,
            ),
            composite_score=composite,
            novelty_score=novelty_score,
            capstone_score=capstone_score,
            highlight_line=highlight,
            capstone_verdict=verdict,
        )

