import io
import json
import logging
import re
from typing import List
import pandas as pd
from pypdf import PdfReader
from app.collectors.base import RawPaper
from app.processing.cleaner import TextCleaner

logger = logging.getLogger("research_scope.processing.document_parser")


class DocumentParser:
    """
    Extracts scholarly research paper records from user-uploaded files:
    CSV, Excel (.xlsx, .xls), JSON, PDF, and plain text.
    """

    @classmethod
    def parse_file(cls, filename: str, content: bytes) -> List[RawPaper]:
        ext = filename.lower().split(".")[-1]
        papers: List[RawPaper] = []

        try:
            if ext == "csv":
                papers = cls._parse_tabular(pd.read_csv(io.BytesIO(content)), filename)
            elif ext in ("xlsx", "xls"):
                papers = cls._parse_tabular(pd.read_excel(io.BytesIO(content)), filename)
            elif ext == "json":
                papers = cls._parse_json(content, filename)
            elif ext == "pdf":
                papers = cls._parse_pdf(content, filename)
            elif ext in ("txt", "md"):
                papers = cls._parse_text(content.decode("utf-8", errors="ignore"), filename)
            else:
                logger.warning("Unsupported file extension: %s", ext)
        except Exception as e:
            logger.error("Error parsing uploaded file %s: %s", filename, e)

        return papers

    @classmethod
    def _parse_tabular(cls, df: pd.DataFrame, filename: str) -> List[RawPaper]:
        papers: List[RawPaper] = []
        # Find column mappings flexibly (case-insensitive)
        cols = {str(c).lower().strip(): c for c in df.columns}

        title_col = next((cols[c] for c in cols if any(k in c for k in ("title", "paper", "name", "article"))), None)
        abstract_col = next((cols[c] for c in cols if any(k in c for k in ("abstract", "summary", "description", "content"))), None)
        authors_col = next((cols[c] for c in cols if any(k in c for k in ("author", "creator", "writer"))), None)
        year_col = next((cols[c] for c in cols if any(k in c for k in ("year", "date", "published"))), None)
        venue_col = next((cols[c] for c in cols if any(k in c for k in ("venue", "journal", "conference", "publisher"))), None)
        doi_col = next((cols[c] for c in cols if "doi" in c), None)
        url_col = next((cols[c] for c in cols if any(k in c for k in ("url", "link"))), None)

        for _, row in df.iterrows():
            title = str(row[title_col]) if title_col and pd.notna(row[title_col]) else None
            if not title or len(title.strip()) < 5:
                continue

            abstract = str(row[abstract_col]) if abstract_col and pd.notna(row[abstract_col]) else None
            
            # Author list
            authors = []
            if authors_col and pd.notna(row[authors_col]):
                raw_auth = str(row[authors_col])
                authors = [a.strip() for a in re.split(r"[,;|]", raw_auth) if a.strip()]

            # Year
            year = None
            if year_col and pd.notna(row[year_col]):
                match = re.search(r"\b(19\d\d|20\d\d)\b", str(row[year_col]))
                if match:
                    year = int(match.group(1))

            venue = str(row[venue_col]) if venue_col and pd.notna(row[venue_col]) else None
            doi = str(row[doi_col]) if doi_col and pd.notna(row[doi_col]) else None
            url = str(row[url_col]) if url_col and pd.notna(row[url_col]) else None

            paper = RawPaper(
                title=title.strip(),
                abstract=abstract,
                authors=authors,
                year=year,
                venue=venue,
                citations=0,
                source=f"upload:{filename}",
                url=url,
                doi=doi,
                keywords=[],
            )
            papers.append(TextCleaner.clean_paper(paper))

        return papers

    @classmethod
    def _parse_json(cls, content: bytes, filename: str) -> List[RawPaper]:
        data = json.loads(content.decode("utf-8", errors="ignore"))
        items = data if isinstance(data, list) else data.get("papers", [data])
        df = pd.DataFrame(items)
        return cls._parse_tabular(df, filename)

    @classmethod
    def _parse_pdf(cls, content: bytes, filename: str) -> List[RawPaper]:
        """Extracts text from PDF and identifies title and abstract."""
        reader = PdfReader(io.BytesIO(content))
        full_text = ""
        for i, page in enumerate(reader.pages[:5]):  # inspect first 5 pages
            text = page.extract_text()
            if text:
                full_text += "\n" + text

        lines = [l.strip() for l in full_text.splitlines() if l.strip()]
        title = lines[0] if lines else filename.replace(".pdf", "")
        
        abstract = None
        match_abs = re.search(r"(?:Abstract|ABSTRACT)[\s:—]+(.*?)(?=(?:1\.?\s+Introduction|Keywords|Index Terms|Categories))", full_text, re.DOTALL | re.IGNORECASE)
        if match_abs:
            abstract = match_abs.group(1).strip()
        elif len(lines) > 2:
            abstract = " ".join(lines[1:10])

        paper = RawPaper(
            title=title,
            abstract=abstract,
            authors=[],
            year=None,
            venue="User Uploaded PDF",
            citations=0,
            source=f"upload:{filename}",
            url=None,
            doi=None,
            keywords=[],
        )
        return [TextCleaner.clean_paper(paper)]

    @classmethod
    def _parse_text(cls, text: str, filename: str) -> List[RawPaper]:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        title = lines[0] if lines else filename
        abstract = " ".join(lines[1:15]) if len(lines) > 1 else text
        paper = RawPaper(
            title=title,
            abstract=abstract,
            authors=[],
            year=None,
            venue="User Uploaded Text Document",
            citations=0,
            source=f"upload:{filename}",
            url=None,
            doi=None,
            keywords=[],
        )
        return [TextCleaner.clean_paper(paper)]
