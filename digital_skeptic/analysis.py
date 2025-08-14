from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import re

# Lightweight heuristics to keep things robust without large model downloads.
# If spaCy is available, you can enhance claim extraction & NER.
try:
    import spacy  # type: ignore
    _NLP = spacy.load("en_core_web_sm")
except Exception:  # pragma: no cover
    _NLP = None

EMOTIONAL_LEXICON = set([
    "disastrous","catastrophic","shocking","unprecedented","collapse","crisis","outrageous",
    "corrupt","explosive","scandal","cover-up","massive","devastating","alarming","terrifying",
    "disaster","meltdown","chaos","panic"
])

@dataclass
class CoreClaim:
    sentence: str

@dataclass
class RedFlag:
    description: str

def split_sentences(text: str) -> List[str]:
    # Basic sentence segmentation (spaCy if available, else regex)
    if _NLP:
        return [s.text.strip() for s in _NLP(text).sents if s.text.strip()]
    # Fallback: naive split
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)
    return [p.strip() for p in parts if p.strip()]

def extract_core_claims(text: str, max_claims: int = 5) -> List[CoreClaim]:
    sents = split_sentences(text)
    candidates: List[str] = []
    for s in sents:
        # Heuristics: factual-looking sentences with numbers, dates, named entities-ish
        if re.search(r"\b(said|stated|claims?|according to|report(ed)?|data|figures)\b", s, re.I):
            candidates.append(s)
        elif re.search(r"\b(will|is|are|was|were|has|have|expected|projected)\b", s):
            if len(s) > 60 and len(s) < 300:
                candidates.append(s)
        elif re.search(r"\d{4}|\b\d+(\.\d+)?%|\b\d+ (million|billion|thousand)\b", s, re.I):
            candidates.append(s)
    # Deduplicate & truncate
    seen = set()
    uniq = []
    for c in candidates:
        if c.lower() not in seen:
            uniq.append(c)
            seen.add(c.lower())
        if len(uniq) >= max_claims:
            break
    return [CoreClaim(u) for u in uniq]

def analyze_tone(text: str) -> str:
    tokens = re.findall(r"[A-Za-z']+", text.lower())
    emotionally_charged = sum(1 for t in tokens if t in EMOTIONAL_LEXICON)
    ratio = emotionally_charged / max(1, len(tokens))
    if ratio > 0.01:
        return "Uses emotionally charged and persuasive language."
    # Check for opinion indicators
    if re.search(r"\b(in my view|we believe|clearly|obviously|undeniably)\b", text, re.I):
        return "Reads as an opinionated piece with persuasive framing."
    return "Appears mostly neutral and factual in tone."

def detect_red_flags(text: str) -> List[RedFlag]:
    flags: List[RedFlag] = []
    if re.search(r"\banonymous source|unnamed (official|source)\b", text, re.I):
        flags.append(RedFlag("Relies on anonymous/unnamed sources for key claims."))
    if re.search(r"\b(no|without) (evidence|citation|source|link)\b", text, re.I):
        flags.append(RedFlag("Mentions claims without providing citations or links."))
    if re.search(r"\bonly\b.*\bexperts?\b", text, re.I):
        flags.append(RedFlag("Presents only one side (experts) without dissenting views."))
    if re.search(r"\balways|never|everyone|no one\b", text, re.I):
        flags.append(RedFlag("Absolutist language that may signal overgeneralization."))
    if "?" not in text and len(text) > 2000:
        flags.append(RedFlag("Long article with few or no questions asked—possible lack of scrutiny."))
    return flags

def quick_ner_entities(text: str, max_items: int = 8) -> List[str]:
    if _NLP:
        doc = _NLP(text[:15000])  # cap for speed
        ents = [f"{ent.text} ({ent.label_})" for ent in doc.ents if ent.label_ in {"PERSON","ORG","GPE","EVENT","WORK_OF_ART","LAW"}]
        # deduplicate while preserving order
        seen = set(); out = []
        for e in ents:
            if e not in seen:
                out.append(e); seen.add(e)
        return out[:max_items]
    # fallback: naive proper-noun-ish extraction
    candidates = re.findall(r"\b([A-Z][a-zA-Z0-9&.\-]{2,}(?:\s+[A-Z][a-zA-Z0-9&.\-]{2,}){0,3})\b", text)
    seen = set(); out = []
    for c in candidates:
        if c not in seen and not re.match(r"^[A-Z][a-z]+$", c):  # skip simple sentence starts
            out.append(f"{c} (?)")
            seen.add(c)
        if len(out) >= max_items:
            break
    return out

def credibility_score(text: str, claims: List[CoreClaim], flags: List[RedFlag]) -> Tuple[int, str]:
    score = 8
    # penalize for many flags
    score -= min(4, len(flags))
    # boost if multiple specific claims detected
    if len(claims) >= 4:
        score += 1
    # penalize sensational tone
    if "emotionally charged" in analyze_tone(text).lower():
        score -= 2
    score = max(1, min(10, score))
    rationale = "Heuristic score based on tone, number of concrete claims, and detected red flags."
    return score, rationale
