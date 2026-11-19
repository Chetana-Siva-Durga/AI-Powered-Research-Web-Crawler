import html
import re
from typing import Optional, List
from app.collectors.base import RawPaper


class TextCleaner:
    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        """Strips HTML, unescapes entities, normalizes whitespace and encoding."""
        if not text:
            return None

        # Unescape HTML entities (&amp;, &lt;, etc.)
        cleaned = html.unescape(text)

        # Remove HTML tags (e.g. <jats:p>, <b>, <span>)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)

        # Remove strange control characters and multiple newlines/tabs
        cleaned = re.sub(r"[\r\n\t]+", " ", cleaned)
        cleaned = re.sub(r"\s{2,}", " ", cleaned)

        return cleaned.strip()

    @staticmethod
    def normalize_title(title: str) -> str:
        """
        Creates a normalized representation of a title for deduplication:
        lowercase, stripped of punctuation, prefixes, and excess whitespace.
        """
        if not title:
            return ""

        # Remove common prefixes
        t = re.sub(r"^(title:\s*|arxiv:\s*|pmid:\s*)", "", title, flags=re.IGNORECASE)
        t = t.lower()
        # Remove punctuation
        t = re.sub(r"[^\w\s]", "", t)
        # Collapse spaces
        t = re.sub(r"\s+", " ", t).strip()
        return t

    @classmethod
    def clean_paper(cls, paper: RawPaper) -> RawPaper:
        """Cleans all text fields within a RawPaper object."""
        cleaned_title = cls.clean_text(paper.title) or "Untitled Research Paper"
        cleaned_abstract = cls.clean_text(paper.abstract)

        cleaned_authors = []
        for author in paper.authors:
            cleaned_auth = cls.clean_text(author)
            if cleaned_auth and len(cleaned_auth) > 1:
                cleaned_authors.append(cleaned_auth)

        cleaned_doi = None
        if paper.doi:
            cleaned_doi = paper.doi.strip().lower()
            cleaned_doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", cleaned_doi)

        return RawPaper(
            title=cleaned_title,
            abstract=cleaned_abstract,
            authors=cleaned_authors,
            year=paper.year,
            venue=cls.clean_text(paper.venue),
            citations=max(0, paper.citations),
            source=paper.source,
            url=paper.url,
            doi=cleaned_doi,
            keywords=[cls.clean_text(k) for k in paper.keywords if k],
        )
