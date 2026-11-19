import logging
from typing import List, Dict, Any
from app.collectors.base import RawPaper
from app.nlp.embeddings import embedding_engine
from app.nlp.keywords_ner import KeywordsAndNER

logger = logging.getLogger("research_scope.nlp.similarity")


class SimilarityAnalyzer:
    """
    Computes semantic cosine similarity between the user's research idea
    and collected paper corpus, ranking them and identifying concept intersections.
    """

    @classmethod
    def compute_similarity(
        cls,
        idea_text: str,
        papers: List[RawPaper],
        idea_keywords: List[str] = None
    ) -> List[Dict[str, Any]]:
        import numpy as np

        if not papers:
            return []

        # 1. Prepare texts
        idea_query = idea_text
        if idea_keywords and len(idea_keywords) > 0:
            idea_query += " " + " ".join(idea_keywords)

        paper_texts = []
        for p in papers:
            text = p.title
            if p.abstract:
                text += ". " + p.abstract[:500]
            if p.keywords:
                text += " " + " ".join(p.keywords)
            paper_texts.append(text)

        # 2. Compute embeddings
        all_texts = [idea_query] + paper_texts
        embeddings = embedding_engine.get_embeddings(all_texts)

        idea_vec = embeddings[0]
        paper_vecs = embeddings[1:]

        # 3. Cosine similarity
        dot_products = np.dot(paper_vecs, idea_vec)
        
        # Ensure values fall into realistic percentages [0.0, 98.0]
        idea_entities = set(k.lower() for k in KeywordsAndNER.extract_keywords(idea_text))

        ranked_results = []
        for idx, (p, raw_score) in enumerate(zip(papers, dot_products)):
            # Normalize score into clean 0 - 100 percentage
            # Cosine similarity in positive space typically ranges 0.2 - 0.95
            score_clamped = max(0.0, min(1.0, float(raw_score)))
            score_pct = round(score_clamped * 100, 1)

            # Match overlapping concepts
            paper_text = (p.title + " " + (p.abstract or "")).lower()
            matching = [ent.title() for ent in idea_entities if ent in paper_text]

            # Determine relevance tier
            if score_pct >= 70.0:
                tier = "High"
            elif score_pct >= 50.0:
                tier = "Medium"
            else:
                tier = "Low"

            ranked_results.append({
                "paper": p,
                "similarity_score": score_pct,
                "relevance_tier": tier,
                "matching_concepts": matching[:6],
            })

        # 4. Sort descending by similarity score
        ranked_results.sort(key=lambda x: x["similarity_score"], reverse=True)

        # Assign ordinal rank
        for i, item in enumerate(ranked_results):
            item["rank"] = i + 1

        logger.info("Computed similarity for %d papers. Top score: %.1f%%", 
                    len(ranked_results), ranked_results[0]["similarity_score"] if ranked_results else 0.0)
        return ranked_results
