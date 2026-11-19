import itertools
import logging
import re
from typing import List, Dict, Tuple
from app.collectors.base import RawPaper
from app.schemas.analysis_schemas import ResearchGapSchema
from app.nlp.keywords_ner import KeywordsAndNER

logger = logging.getLogger("research_scope.analysis.gap_analyzer")

# Predefined concept pairs to explore for AI/CS research when concepts exist
COMPLEMENTARY_CONCEPTS = [
    ("Transformer", "Clinical Data"),
    ("Multimodal", "Longitudinal EHR"),
    ("Deep Learning", "Explainability & Interpretability"),
    ("Vision Transformer", "Low-Resource Imaging"),
    ("Federated Learning", "Cross-Hospital MRI"),
    ("Diffusion Models", "Tumor Synthesizing & Augmentation"),
    ("Real-Time Inference", "Edge Deployment"),
    ("Zero Trust Architecture", "Resource-Constrained IoT"),
    ("Quantum Neural Network", "Noisy Intermediate-Scale Quantum"),
]

LIMITATION_PATTERNS = [
    re.compile(r"(?:a major limitation of|limitation is|remains an open challenge|remains challenging|rarely investigated|insufficiently explored|lack of|little attention has been paid to|further research is needed to)\s+([^.!?]{15,120}[.!?])", re.I),
    re.compile(r"(?:future work will focus on|future work should explore|open problem is|bottleneck lies in)\s+([^.!?]{15,120}[.!?])", re.I),
]


class GapAnalyzer:
    """
    Identifies potential underexplored research gaps by analyzing:
    1. Concept co-occurrence matrix (concepts prevalent individually but absent together)
    2. Explicit limitations and future work mined from scholarly abstracts
    3. Structural underrepresentation in current literature clusters
    """

    @classmethod
    def _extract_abstract_limitations(cls, papers: List[RawPaper]) -> List[str]:
        """Extracts direct limitation statements mentioned by existing authors."""
        limitations = []
        for p in papers:
            if not p.abstract:
                continue
            for pattern in LIMITATION_PATTERNS:
                match = pattern.search(p.abstract)
                if match:
                    limitation_phrase = match.group(0).strip()
                    # Clean up
                    limitation_phrase = re.sub(r"\s+", " ", limitation_phrase)
                    if len(limitation_phrase) > 20:
                        limitations.append(limitation_phrase)
                        break
        return limitations[:5]

    @classmethod
    def analyze(
        cls,
        idea_text: str,
        papers: List[RawPaper],
        idea_keywords: List[str] = None
    ) -> List[ResearchGapSchema]:
        gaps: List[ResearchGapSchema] = []
        if not papers:
            return gaps

        # 1. Extract concepts from idea + top corpus keywords
        idea_kws = KeywordsAndNER.extract_keywords(idea_text, top_k=6)
        if idea_keywords:
            for ik in idea_keywords:
                if ik.title() not in idea_kws:
                    idea_kws.append(ik.title())

        # Collect corpus paper texts
        corpus_texts = [(p.title + " " + (p.abstract or "")).lower() for p in papers]
        mined_limitations = cls._extract_abstract_limitations(papers)

        # 2. Build frequency map for individual concepts
        concept_freq: Dict[str, int] = {}
        for c in idea_kws:
            c_lower = c.lower()
            concept_freq[c] = sum(1 for text in corpus_texts if c_lower in text)

        # 3. Analyze co-occurrence of concept pairs
        candidate_pairs: List[Tuple[str, str, int, int, int]] = []
        pairs = list(itertools.combinations(idea_kws[:6], 2))

        # Also consider complementary concepts if mentioned in idea
        idea_lower = idea_text.lower()
        for ca, cb in COMPLEMENTARY_CONCEPTS:
            if ca.lower() in idea_lower or cb.lower() in idea_lower:
                pairs.append((ca, cb))

        for ca, cb in pairs:
            ca_lower = ca.lower()
            cb_lower = cb.lower()

            count_a = sum(1 for t in corpus_texts if ca_lower in t)
            count_b = sum(1 for t in corpus_texts if cb_lower in t)
            co_count = sum(1 for t in corpus_texts if ca_lower in t and cb_lower in t)

            # High individual presence but rare co-occurrence signifies a potential research gap
            candidate_pairs.append((ca, cb, count_a, count_b, co_count))

        # Sort pairs by novelty potential: high (count_a + count_b) and low co_count
        candidate_pairs.sort(key=lambda x: (x[2] + x[3]) / (x[4] + 1), reverse=True)

        seen_gap_titles = set()
        gap_id = 1

        for ca, cb, count_a, count_b, co_count in candidate_pairs:
            if len(gaps) >= 4:
                break

            title = f"Underexplored Interplay: {ca} and {cb}"
            if title in seen_gap_titles:
                continue
            seen_gap_titles.add(title)

            # Compute novelty score between 65.0 and 96.0
            if co_count == 0:
                novelty = round(min(95.0, 78.0 + (count_a + count_b) * 1.2), 1)
                rarity_text = "zero co-occurring studies"
            elif co_count <= 2:
                novelty = round(min(90.0, 72.0 + (count_a + count_b) * 0.8), 1)
                rarity_text = f"only {co_count} co-occurring studies"
            else:
                novelty = round(max(60.0, 75.0 - co_count * 2.0), 1)
                rarity_text = f"{co_count} co-occurring publications"

            desc = (
                f"While '{ca}' appears in {count_a} analyzed works and '{cb}' appears in {count_b} works, "
                f"the corpus reveals {rarity_text} that explicitly integrate both dimensions simultaneously."
            )

            suggested = (
                f"Investigate a hybrid framework that leverages {ca} methodologies to directly address "
                f"the operational constraints of {cb}, validating performance against baseline benchmarks."
            )

            gaps.append(ResearchGapSchema(
                id=gap_id,
                gap_title=title,
                concept_a=ca,
                concept_b=cb,
                co_occurrence_count=co_count,
                novelty_score=novelty,
                description=desc,
                suggested_direction=suggested,
                feasibility="High" if novelty < 90 else "Medium",
            ))
            gap_id += 1

        # 4. Integrate paper-mined limitation gap if available
        if mined_limitations and len(gaps) < 4:
            limitation_text = mined_limitations[0]
            gaps.append(ResearchGapSchema(
                id=gap_id,
                gap_title="Empirical Literature Bottleneck: Reported Limitation",
                concept_a="Reported Author Limitation",
                concept_b="Generalization Barrier",
                co_occurrence_count=1,
                novelty_score=87.5,
                description=f"Existing studies explicitly highlight this research barrier: '{limitation_text}'",
                suggested_direction="Design ablation benchmarks specifically targeting this cited limitation to establish empirical superiority over current baselines.",
                feasibility="High",
            ))

        logger.info("Identified %d potential research gaps", len(gaps))
        return gaps
