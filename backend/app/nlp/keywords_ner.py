import re
from collections import Counter
from typing import List, Dict, Set


# Common academic and generic English stop words
ACADEMIC_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it",
    "its", "itself", "let's", "me", "more", "most", "my", "myself", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "she", "should", "so", "some", "such",
    "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there",
    "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "were", "weren't", "what", "when", "where", "which",
    "while", "who", "whom", "why", "with", "won't", "would", "you", "your", "yours",
    "yourself", "yourselves",
    # Academic noise terms
    "paper", "study", "approach", "method", "results", "based", "using", "proposed",
    "analysis", "show", "shows", "present", "presents", "demonstrate", "evaluation",
    "performance", "significant", "provide", "existing", "experimental", "new",
}

# Technical concepts & domain entities mapping
TECH_ENTITIES: Dict[str, str] = {
    # Architectures & Models
    "transformer": "Deep Learning Architecture",
    "vision transformer": "Computer Vision Architecture",
    "vit": "Computer Vision Architecture",
    "cnn": "Convolutional Architecture",
    "resnet": "Deep Learning Architecture",
    "diffusion model": "Generative AI Architecture",
    "llm": "Large Language Model",
    "bert": "Language Model",
    "gnn": "Graph Neural Network",
    "reinforcement learning": "AI Paradigm",
    "federated learning": "Distributed AI",
    # Modalities & Data
    "mri": "Medical Imaging Modality",
    "ct scan": "Medical Imaging Modality",
    "eeg": "Biomedical Signal",
    "x-ray": "Radiological Modality",
    "clinical data": "Healthcare Data",
    "electronic health records": "Healthcare Data",
    "ehr": "Healthcare Data",
    # Problems & Tasks
    "brain tumor": "Medical Condition / Pathology",
    "cancer detection": "Clinical Diagnosis",
    "early detection": "Clinical Screening",
    "segmentation": "Computer Vision Task",
    "object detection": "Computer Vision Task",
    "classification": "Machine Learning Task",
    "anomaly detection": "Security & Diagnostics Task",
    "zero trust": "Cybersecurity Architecture",
    "intrusion detection": "Cybersecurity Task",
    "edge computing": "Distributed Systems",
    "quantum computing": "Quantum Technology",
    "quantum machine learning": "Quantum AI",
    "qml": "Quantum AI",
}


class KeywordsAndNER:
    """
    Extracts keyphrases, technical keywords, and scientific entities from research text.
    """

    @classmethod
    def extract_keywords(cls, text: str, top_k: int = 8) -> List[str]:
        """Extracts dominant keywords using n-gram frequency and length-weighting."""
        if not text:
            return []

        clean_text = text.lower()
        # Find explicit multi-word technical entities first
        found_entities = []
        for term in TECH_ENTITIES.keys():
            if re.search(r"\b" + re.escape(term) + r"\b", clean_text):
                found_entities.append(term.title())

        # Extract 1-3 word phrases
        tokens = re.findall(r"\b[a-zA-Z]{3,}\b", clean_text)
        filtered_tokens = [t for t in tokens if t not in ACADEMIC_STOPWORDS]

        # Count bi-grams
        bigrams = []
        for i in range(len(filtered_tokens) - 1):
            bigrams.append(f"{filtered_tokens[i]} {filtered_tokens[i+1]}")

        counts = Counter(filtered_tokens + bigrams)
        common_phrases = [phrase.title() for phrase, _ in counts.most_common(top_k * 2)]

        # Combine found entities and phrases, preserving order and uniqueness
        seen = set()
        result = []
        for item in found_entities + common_phrases:
            norm = item.lower()
            if norm not in seen and norm not in ACADEMIC_STOPWORDS:
                seen.add(norm)
                result.append(item)
            if len(result) >= top_k:
                break

        return result

    @classmethod
    def extract_entities(cls, text: str) -> List[Dict[str, str]]:
        """Identifies domain entities with their respective category types."""
        if not text:
            return []

        lower_text = text.lower()
        entities = []
        for term, category in TECH_ENTITIES.items():
            if re.search(r"\b" + re.escape(term) + r"\b", lower_text):
                entities.append({
                    "entity": term.title(),
                    "category": category,
                })
        return entities

    @classmethod
    def extract_corpus_top_keywords(cls, texts: List[str], top_k: int = 15) -> List[str]:
        """Extracts top corpus-wide keywords using TF-IDF across all collected papers."""
        valid_texts = [t for t in texts if t and len(t.strip()) > 20]
        if not valid_texts:
            return []

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=1000,
                min_df=1,
            )
            tfidf_matrix = vectorizer.fit_transform(valid_texts)
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.sum(axis=0).A1

            top_indices = scores.argsort()[::-1]
            keywords = []
            seen = set()
            for idx in top_indices:
                word = feature_names[idx]
                if any(sw in word for sw in ("paper", "results", "method", "using", "proposed", "study")):
                    continue
                if word not in seen:
                    seen.add(word)
                    keywords.append(word.title())
                if len(keywords) >= top_k:
                    break
            return keywords
        except Exception:
            # Fallback simple count
            all_text = " ".join(valid_texts)
            return cls.extract_keywords(all_text, top_k=top_k)
