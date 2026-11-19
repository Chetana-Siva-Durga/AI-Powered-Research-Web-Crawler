import re
from typing import Dict, Tuple, List


DOMAIN_SIGNATURES: Dict[str, List[str]] = {
    "Healthcare AI & Medical Imaging": [
        "mri", "tumor", "cancer", "medical", "clinical", "ct scan", "radiology",
        "healthcare", "lesion", "biomedical", "diagnosis", "pathology", "patient",
        "brain tumor", "alzheimer", "eeg", "cardiac", "genomic", "drug discovery"
    ],
    "Computer Vision": [
        "image", "vision", "segmentation", "object detection", "yolo", "vit",
        "convolutional", "cnn", "optical", "video", "pose", "pixel", "visual"
    ],
    "Natural Language Processing": [
        "nlp", "text", "language model", "llm", "transformer", "bert", "gpt",
        "sentiment", "summarization", "translation", "token", "semantic", "dialogue"
    ],
    "Cybersecurity & Privacy": [
        "security", "cyber", "attack", "vulnerability", "malware", "zero trust",
        "intrusion", "encryption", "privacy", "cryptography", "threat", "firewall", "phishing"
    ],
    "IoT & Edge Computing": [
        "iot", "sensor", "edge", "smart city", "embedded", "wireless", "rfid",
        "fog computing", "lora", "actuator", "wearable", "edge ai"
    ],
    "Cloud & Distributed Systems": [
        "cloud", "distributed", "kubernetes", "microservices", "serverless",
        "consensus", "blockchain", "load balancing", "fault tolerance"
    ],
    "Quantum Computing": [
        "quantum", "qubit", "qml", "quantum circuit", "superconducting",
        "entanglement", "quantum machine learning"
    ],
    "Deep Learning & Machine Learning": [
        "neural network", "deep learning", "machine learning", "reinforcement learning",
        "gradient", "backpropagation", "supervised", "unsupervised", "clustering"
    ],
}


class DomainDetector:
    """
    Detects the relevant computer science / scientific domains from
    a research idea string, user keywords, and related literature.
    """

    @classmethod
    def detect(cls, text: str, user_hint: str = "Auto-detect") -> Tuple[str, float, List[str]]:
        """
        Returns:
            (primary_domain, confidence_score_0_to_100, relevant_subdomains)
        """
        if user_hint and user_hint != "Auto-detect" and user_hint != "":
            return user_hint, 95.0, [user_hint]

        lower_text = text.lower()
        domain_scores: Dict[str, int] = {}

        for domain, keywords in DOMAIN_SIGNATURES.items():
            score = 0
            for kw in keywords:
                # Give bonus points for whole word / phrase matches
                matches = len(re.findall(r"\b" + re.escape(kw) + r"\b", lower_text))
                score += matches * 2
            domain_scores[domain] = score

        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        top_domain, top_score = sorted_domains[0]

        if top_score == 0:
            return "General Computer Science", 50.0, ["Machine Learning", "Software Systems"]

        total_score = sum(domain_scores.values()) or 1
        confidence = min(98.0, round((top_score / total_score) * 100 + 20, 1))

        # Identify secondary subdomains with significant scores
        subdomains = [d for d, s in sorted_domains if s > 0][:3]

        return top_domain, confidence, subdomains
