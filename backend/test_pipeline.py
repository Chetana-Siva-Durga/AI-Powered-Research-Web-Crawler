import asyncio
from app.core.database import init_db, SessionLocal
from app.collectors.manager import CollectorManager
from app.processing.deduplicator import Deduplicator
from app.nlp.domain_detector import DomainDetector
from app.nlp.keywords_ner import KeywordsAndNER
from app.nlp.similarity import SimilarityAnalyzer
from app.analysis.trend_analyzer import TrendAnalyzer
from app.analysis.gap_analyzer import GapAnalyzer
from app.analysis.relevance_evaluator import RelevanceEvaluator
from app.analysis.explainer import Explainer

async def main():
    print("=== 1. Initializing Database ===")
    init_db()

    query = "Using Transformer models for early detection of brain tumors from MRI images"
    print(f"\n=== 2. Testing Query: '{query}' ===")

    # Domain & Keywords
    domain, conf, subdomains = DomainDetector.detect(query)
    keywords = KeywordsAndNER.extract_keywords(query)
    print(f"Detected Domain: {domain} (Confidence: {conf}%)")
    print(f"Extracted Keywords: {keywords}")

    # Collectors
    print("\n=== 3. Testing Multi-Source Data Collection (APIs + Crawler) ===")
    mgr = CollectorManager()
    collection = await mgr.collect_all(query=query, keywords=keywords, limit_per_source=5)
    raw_papers = collection["papers"]
    breakdown = collection["breakdown"]
    print(f"Raw Papers Collected: {len(raw_papers)}")
    print(f"Sources Breakdown: {breakdown}")

    # Deduplication
    print("\n=== 4. Testing Deduplication ===")
    unique_papers, dupes = Deduplicator.deduplicate(raw_papers)
    print(f"Unique Papers: {len(unique_papers)} ({dupes} duplicates removed)")

    # Similarity
    print("\n=== 5. Testing Semantic Similarity ===")
    similarities = SimilarityAnalyzer.compute_similarity(query, unique_papers, keywords)
    print(f"Ranked {len(similarities)} papers by semantic proximity.")
    if similarities:
        top = similarities[0]
        print(f"Top Match: '{top['paper'].title}' -> {top['similarity_score']}% ({top['relevance_tier']})")

    # Trends
    print("\n=== 6. Testing Research Trends ===")
    trends = TrendAnalyzer.analyze(unique_papers, keywords)
    print(f"CAGR Growth Rate: +{trends.cagr_growth_rate}%")
    print(f"Emerging Topics: {trends.emerging_topics}")
    print(f"Mature Topics: {trends.mature_topics}")

    # Gaps
    print("\n=== 7. Testing Potential Research Gaps ===")
    gaps = GapAnalyzer.analyze(query, unique_papers, keywords)
    print(f"Discovered {len(gaps)} potential research gaps:")
    for g in gaps[:3]:
        print(f"  - [{g.novelty_score}% Novelty] {g.gap_title}")

    # Relevance Evaluation
    print("\n=== 8. Testing Multi-Dimensional Evaluation ===")
    evaluation = RelevanceEvaluator.evaluate(query, unique_papers, similarities, trends, gaps, domain)
    print(f"Academic Score:       {evaluation.academic.score}/100 ({evaluation.academic.level})")
    print(f"Industry Score:       {evaluation.industry.score}/100 ({evaluation.industry.level})")
    print(f"Societal Score:       {evaluation.societal.score}/100 ({evaluation.societal.level})")
    print(f"Future Potential:     {evaluation.future_potential.score}/100 ({evaluation.future_potential.level})")
    print(f"Composite Viability:  {evaluation.composite_score}/100")

    # Explainer
    print("\n=== 9. Testing Explainable Results Generator ===")
    explanation = Explainer.generate_explanation(query, domain, unique_papers, similarities, trends, gaps, evaluation)
    print("Executive Summary:")
    print(f"  {explanation.executive_summary[:200]}...")
    print(f"Actionable Recommendations: {len(explanation.actionable_recommendations)}")

    print("\n>>> ALL PIPELINE STAGES PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    asyncio.run(main())
