# 🚀 Research Scope — AI-Powered Scholarly Research Analysis Platform

> **"Research Scope is an AI-based research analysis platform that collects scholarly literature from multiple sources using APIs and web crawlers, analyzes it using NLP and deep-learning techniques, and helps researchers identify similar work, potential research gaps, trends, and the academic, industry, societal, and future relevance of their research idea."**

---

## 📌 1. The Problem Statement

When a student, researcher, or faculty member develops a new research idea, they typically face hours of tedious, manual literature reviews across scattered databases attempting to answer:
- **Has someone already researched this exact topic?**
- **What existing papers are most closely related?**
- **Is this research area growing or becoming obsolete?**
- **Where are the unexplored research gaps and novel concept combinations?**
- **What is the academic, industrial, societal, and future potential of the idea?**

**Research Scope** automates this end-to-end literature harvesting and intelligence pipeline.

---

## 🏛️ 2. Architectural Blueprint (7 Layers)

```
┌─────────────────────────────────────────────────────────────┐
│                       1. USER INPUT                         │
│       Research Idea / Keywords / Domain / Custom Dataset     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     2. REACT FRONTEND                       │
│    Vite + Tailwind CSS + Lucide Icons + Recharts Dashboard  │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API (JSON / Axios)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    3. FASTAPI BACKEND                       │
│        Uvicorn + Asynchronous Pipeline Coordinator          │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌───────────────────────┐             ┌───────────────────────┐
│  4A. SCHOLARLY APIS   │             │   4B. WEB CRAWLER     │
│  • OpenAlex           │             │  • Scrapy Framework   │
│  • Semantic Scholar   │             │  • BeautifulSoup      │
│  • Crossref (DOIs)    │             │  • Requests           │
│  • arXiv Preprints    │             │  • Open Repositories  │
│  • PubMed E-utilities │             │  • Rate-limiting      │
└───────────┬───────────┘             └───────────┬───────────┘
            └──────────────────┬──────────────────┘
                               │ Raw Paper Records
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    5. DATA PROCESSING                       │
│  • Unicode & HTML sanitization (TextCleaner)                │
│  • Title normalization & author resolution                  │
│  • Multi-Tier Deduplication (DOI + Levenshtein / Sequence)  │
│  • User Dataset / PDF Ingestion Parser (PyPDF, Pandas)      │
└──────────────────────────────┬──────────────────────────────┘
                               │ Cleaned & Deduplicated Corpus
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    6. PERSISTENT STORAGE                    │
│   • MySQL (Primary) with Automatic Resilient SQLite Fallback │
│   • Relational Schema: Ideas, Papers, Citations, Gaps,      │
│     Trends, Multi-Dimensional Scores                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   7. AI / NLP & EVALUATION                  │
│  • Domain Detection (CS, AI/ML, Healthcare, Cyber, etc.)    │
│  • Dense Semantic Embeddings (Sentence-Transformers / LSA)  │
│  • Cosine Similarity Proximity & Literature Ranking         │
│  • Trend Dynamics (Publication Velocity & % CAGR)           │
│  • Research Gap Discovery (Concept Co-occurrence Matrix)    │
│  • Multi-Dimensional Evaluation (Academic, Industry,        │
│    Societal, Future Potential)                              │
│  • Explainable Findings & Evidence Generator                │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 8. INTERACTIVE DASHBOARD                    │
│  • Scorecards • Similar Papers • Recharts Trend Lines        │
│  • Gap Cards • Radar Chart • Pipeline Inspector • Export MD │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 3. Technology Stack

| Technology | Role & Purpose in Research Scope |
| :--- | :--- |
| **React 18 + Vite** | High-performance, reactive user interface and dashboard |
| **Tailwind CSS** | Elegant, modern dark academia/tech visual styling |
| **Recharts** | Interactive SVG visualizations (Radar charts, Line plots, Bar velocity) |
| **FastAPI + Uvicorn** | Asynchronous Python REST API orchestration framework |
| **Scrapy** | Mandatory focused scholarly web crawler for open repositories |
| **BeautifulSoup / Requests** | HTML parsing and Dublin Core / Highwire Press metadata extraction |
| **Sentence-Transformers** | Dense vector representations for semantic understanding |
| **scikit-learn** | Latent Semantic Analysis (LSA), TF-IDF, and Cosine Similarity |
| **SQLAlchemy** | Object-Relational Mapping (ORM) and resilient DB connection management |
| **MySQL** | Persistent storage for papers, author graphs, trends, and evaluations |
| **Pandas / PyPDF** | Ingestion engine for uploaded CSV, Excel, and PDF research datasets |

---

## 🔬 4. Core Algorithmic & Analytical Components

### 4.1 Multi-Source Data Collection (APIs + Mandatory Web Crawler)
Rather than relying on a single source, Research Scope queries **5 scholarly APIs** in parallel with a **dedicated focused Web Crawler**:
1. **OpenAlex**: Global research metadata and citations.
2. **Semantic Scholar**: Graph citations and academic venues.
3. **Crossref**: Canonical peer-reviewed DOIs and metadata.
4. **arXiv**: Recent computer science, machine learning, and quantum preprints.
5. **PubMed**: Clinical and healthcare AI biomedical literature.
6. **Web Crawler (Scrapy / BS4)**: Crawls permitted public preprint indices and open-access research repositories extracting structured metadata directly from HTML DOM and meta tags.

### 4.2 Multi-Tier Deduplication
Raw papers from different sources are consolidated into a single canonical record:
- **Tier 1**: Exact DOI matching (`10.xxxx/...`).
- **Tier 2**: Normalized title hash matching (lowercase, stripped punctuation).
- **Tier 3**: High-similarity fuzzy Levenshtein / Sequence matching ($\ge 0.90$).
- **Metadata Merging**: Combines the richest abstract, aggregates multi-source citations, and preserves open-access URLs.

### 4.3 Semantic Similarity Analysis
- Embeds user idea and collected papers into dense vector space $\mathbf{u}, \mathbf{v} \in \mathbb{R}^d$.
- Calculates Cosine Proximity:
  $$\text{Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} \times 100\%$$
- Ranks papers into High ($\ge 70\%$), Medium ($50\% - 69\%$), and Low ($< 50\%$) tiers.

### 4.4 Research Trend Analysis & Publication Velocity
- Groups publication counts across chronological years.
- Computes Compound Annual Growth Rate (CAGR):
  $$\text{CAGR} = \left(\frac{V_{\text{final}}}{V_{\text{initial}}}\right)^{\frac{1}{n}} - 1$$
- Tracks individual keyword trajectories over time and classifies topics into **Emerging Directions** (accelerating velocity) vs **Established Methodologies**.

### 4.5 Potential Research Gap Discovery
Research Scope does not make unsubstantiated claims ("nobody has ever done this"). Instead, it analyzes:
1. **Concept Co-Occurrence Matrix**: Measures single-concept frequency $C(A)$ and $C(B)$ versus joint occurrence $C(A \cap B)$. Concepts that are individually prominent but rarely combined indicate high-novelty unexplored niches.
2. **Novelty Score Calculation**:
   $$\text{Novelty} = \min\left(95, 50 + 40 \times \left(1 - \frac{C(A \cap B)}{\sqrt{C(A) \cdot C(B)} + 1}\right)\right)$$
3. **Literature Limitations Mining**: Natural-language pattern extractors scan paper abstracts for explicit author-cited limitations ("remains an open challenge", "limited by", "future work is needed").
4. **Actionable Hypotheses**: Formulates concrete experimental directions for the researcher.

### 4.6 Multi-Dimensional Relevance Evaluation
Calculates 4 quantifiable scores (0 to 100) supported by explicit empirical evidence:
- **Academic Relevance**: Peer-reviewed volume, top-paper similarity, recent 2023-2026 publication velocity.
- **Industry Relevance**: Industrial indicators (real-time, latency, deployment, clinical translation, hardware feasibility).
- **Societal Relevance**: Public health, safety, privacy, accessibility, and humanitarian benefit.
- **Future Potential**: Growth trajectory (% CAGR), high-novelty gaps, emerging technology alignment.

### 4.7 Explainable Results Generator
Synthesizes findings into natural-language narratives:
- **Executive Summary**
- **Literature Alignment Insights**
- **Trend & Velocity Insights**
- **Strategic Gap Opportunity**
- **Actionable Next Steps**

---

## 🚀 5. Quickstart Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ and npm
- (Optional) MySQL Server (if MySQL is not active, the system automatically uses SQLite with zero configuration required).

### Option A: Launching with Windows Scripts

1. **Start Backend**:
   Double click or run:
   ```cmd
   run_backend.bat
   ```
   *FastAPI server will start on `http://127.0.0.1:8000` (Swagger docs at `/docs`).*

2. **Start Frontend**:
   Double click or run:
   ```cmd
   run_frontend.bat
   ```
   *React Vite application will open on `http://localhost:5173`.*

---

### Option B: Manual Terminal Launch

#### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🗄️ 6. Database Configuration

The application is configured to connect to MySQL by default via `backend/.env`:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DB=research_scope
USE_SQLITE_FORCE=False
```

> **Resilient Auto-Fallback**: If MySQL is stopped or credentials are not yet configured, the system automatically falls back to a local SQLite database (`research_scope.db`). Once your MySQL server is running, simply set your credentials in `.env` and it will automatically persist to MySQL!

---

## 🎓 7. Interview Defense & Frequently Asked Questions

### Q1: "What does your project do in one sentence?"
> *"Research Scope is an AI-based research analysis platform that collects scholarly literature from multiple sources using APIs and web crawlers, analyzes it using NLP and deep-learning techniques, and helps researchers identify similar work, potential research gaps, trends, and the academic, industry, societal, and future relevance of their research idea."*

### Q2: "Why do you use both APIs and a Web Crawler?"
> *"APIs provide structured metadata from indexed repositories with rate limits and specific schemas. However, many preprint archives, university institutional repositories, and open conference proceedings do not have open API endpoints. Our Python + Scrapy/BeautifulSoup web crawler complements APIs by directly parsing HTML pages, extracting Dublin Core and Highwire Press citation meta tags, and indexing open papers directly from the web."*

### Q3: "How does the system calculate an Academic Relevance score of 88?"
> *"We do not rely on an arbitrary LLM hallucination. The relevance engine calculates a metric-backed score combining: (1) total volume of peer-reviewed literature in the domain, (2) mean semantic cosine similarity of top-matching papers, (3) publication velocity in recent years (2023–2026), and (4) citation impact across matched foundational studies. Each score is presented with itemized evidence."*

### Q4: "How does Gap Analysis work?"
> *"We construct a concept co-occurrence matrix from the analyzed corpus. If Concept A (e.g., Vision Transformers) and Concept B (e.g., Low-Resource Clinical MRI) frequently appear individually in literature but exhibit low or zero co-occurrence together, the system detects an underexplored combination and calculates a novelty score. Furthermore, we extract author-stated limitations from paper abstracts to identify unsolved barriers."*
