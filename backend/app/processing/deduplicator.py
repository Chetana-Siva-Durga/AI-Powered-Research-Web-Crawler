import difflib
import logging
from typing import List, Dict, Tuple
from app.collectors.base import RawPaper
from app.processing.cleaner import TextCleaner

logger = logging.getLogger("research_scope.processing.deduplicator")


class Deduplicator:
    """
    Multi-tiered deduplication pipeline:
    1. Canonical DOI resolution
    2. Exact normalized title matching
    3. Fuzzy token similarity matching for title variants
    Also merges citations, abstracts, and multi-source attribution into a single canonical paper record.
    """

    @staticmethod
    def _similarity_ratio(str1: str, str2: str) -> float:
        """Computes SequenceMatcher ratio between two normalized strings."""
        if not str1 or not str2:
            return 0.0
        return difflib.SequenceMatcher(None, str1, str2).ratio()

    @classmethod
    def _merge_papers(cls, canonical: RawPaper, duplicate: RawPaper) -> RawPaper:
        """Merges metadata between two matching records, preserving the richest data."""
        # 1. Choose richest abstract
        abstract = canonical.abstract
        if not abstract and duplicate.abstract:
            abstract = duplicate.abstract
        elif duplicate.abstract and len(duplicate.abstract) > len(abstract or ""):
            abstract = duplicate.abstract

        # 2. Maximum citations
        citations = max(canonical.citations, duplicate.citations)

        # 3. DOI preference
        doi = canonical.doi or duplicate.doi

        # 4. URL preference
        url = canonical.url or duplicate.url

        # 5. Combined sources
        sources = set(canonical.source.split(", "))
        for s in duplicate.source.split(", "):
            if s:
                sources.add(s)
        merged_source = ", ".join(sorted(sources))

        # 6. Combined unique authors
        authors = list(canonical.authors)
        for a in duplicate.authors:
            if a not in authors:
                authors.append(a)

        # 7. Year preference (take non-null)
        year = canonical.year or duplicate.year

        # 8. Venue preference
        venue = canonical.venue or duplicate.venue

        # 9. Combined keywords
        keywords = list(set(canonical.keywords + duplicate.keywords))

        return RawPaper(
            title=canonical.title,
            abstract=abstract,
            authors=authors,
            year=year,
            venue=venue,
            citations=citations,
            source=merged_source,
            url=url,
            doi=doi,
            keywords=keywords[:8],
        )

    @classmethod
    def deduplicate(cls, raw_papers: List[RawPaper]) -> Tuple[List[RawPaper], int]:
        """
        Deduplicates a list of RawPaper objects.
        Returns (deduplicated_papers, duplicates_removed_count).
        """
        if not raw_papers:
            return [], 0

        # Step 1: Clean every paper first
        cleaned_list = [TextCleaner.clean_paper(p) for p in raw_papers]

        unique_papers: List[RawPaper] = []
        doi_map: Dict[str, int] = {}             # doi -> index in unique_papers
        norm_title_map: Dict[str, int] = {}      # norm_title -> index in unique_papers

        duplicates_count = 0

        for paper in cleaned_list:
            norm_title = TextCleaner.normalize_title(paper.title)
            matched_index = None

            # Check 1: DOI match
            if paper.doi and paper.doi in doi_map:
                matched_index = doi_map[paper.doi]

            # Check 2: Exact normalized title match
            elif norm_title and norm_title in norm_title_map:
                matched_index = norm_title_map[norm_title]

            # Check 3: Fuzzy title match (for near-identical titles with punctuation/subtitles)
            elif norm_title and len(norm_title) > 15:
                for existing_norm, idx in norm_title_map.items():
                    if abs(len(existing_norm) - len(norm_title)) < 15:
                        if cls._similarity_ratio(norm_title, existing_norm) >= 0.90:
                            matched_index = idx
                            break

            if matched_index is not None:
                # Merge into canonical record
                canonical = unique_papers[matched_index]
                merged = cls._merge_papers(canonical, paper)
                unique_papers[matched_index] = merged
                duplicates_count += 1
            else:
                # Add as new unique paper
                new_idx = len(unique_papers)
                unique_papers.append(paper)
                if paper.doi:
                    doi_map[paper.doi] = new_idx
                if norm_title:
                    norm_title_map[norm_title] = new_idx

        logger.info(
            "Deduplication finished: %d raw papers -> %d unique papers (%d duplicates removed)",
            len(raw_papers), len(unique_papers), duplicates_count
        )
        return unique_papers, duplicates_count
