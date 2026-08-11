"""Shared, dependency-free analysis helpers used by evidence providers.

These helpers implement the lightweight, explainable heuristics that let each
provider reason about a context without pulling in external NLP libraries. They
are deliberately simple and transparent: every score a provider produces can be
traced back to the tokens, keywords, or counts these functions return.

The matching is intentionally *fuzzy-but-transparent*: tokens are normalized
(stopword removal, lowercasing, light suffix stripping) and compared via both
exact and alias (synonym) matching, so "reduce memory usage" and "memory
optimization" are recognized as related even though they share no identical word
beyond "memory".
"""

from typing import Any

__all__ = [
    "tokenize",
    "keyword_overlap",
    "term_frequency",
    "salient_tokens",
    "topic_alignment",
    "get_text",
    "get_list",
    "is_empty",
    "parse_git_diff",
]

# Words that carry no semantic weight for alignment comparison.
_STOPWORDS: set[str] = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "of",
    "to",
    "in",
    "on",
    "for",
    "with",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "this",
    "that",
    "these",
    "those",
    "it",
    "its",
    "we",
    "our",
    "you",
    "your",
    "i",
    "my",
    "me",
    "by",
    "from",
    "at",
    "into",
    "than",
    "then",
    "so",
    "if",
    "else",
    "when",
    "while",
    "which",
    "who",
    "whom",
    "what",
    "how",
    "why",
    "all",
    "any",
    "some",
    "no",
    "not",
    "do",
    "does",
    "did",
    "has",
    "have",
    "had",
    "can",
    "could",
    "should",
    "would",
    "will",
    "shall",
    "may",
    "might",
    "must",
    "using",
    "use",
    "make",
    "making",
    "add",
    "added",
    "new",
    "current",
    "currently",
    "implement",
    "implementation",
    "support",
}

# Alias groups: any two tokens in the same group are treated as a match.
# This is the transparent "semantic" layer -- small, curated, and explainable.
_ALIASES: list[set[str]] = [
    {"memory", "ram", "heap"},
    {"optimize", "optimization", "optimise", "tune", "tuning"},
    {"speed", "performance", "fast", "fastest", "latency"},
    {"startup", "boot", "initialization", "init", "launch"},
    {"refactor", "restructure", "rewrite", "reorganize"},
    {"security", "secure", "auth", "authentication", "authorization"},
    {"bug", "defect", "error", "issue", "fix"},
    {"test", "tests", "testing", "coverage"},
    {"database", "db", "storage", "persistence"},
    {"api", "endpoint", "interface", "service"},
]


def _alias_index() -> dict[str, int]:
    """Map each alias token to its group id."""
    index: dict[str, int] = {}
    for gid, group in enumerate(_ALIASES):
        for token in group:
            index[token] = gid
    return index


_ALIAS_INDEX = _alias_index()


def _normalize(text: Any) -> str:
    """Coerce arbitrary context values into a single lowercase string."""
    if text is None:
        return ""
    if isinstance(text, (list, tuple, set)):
        return " ".join(_normalize(item) for item in text)
    if isinstance(text, dict):
        return " ".join(_normalize(v) for v in text.values())
    return str(text).lower()


def _strip_suffix(token: str) -> str:
    """Light suffix stripping so 'optimization' and 'optimize' can match."""
    for suffix in ("ization", "isation", "ing", "ed", "er", "es"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 3:
            return token[: -len(suffix)]
    return token


def tokenize(text: Any) -> list[str]:
    """Split a context value into meaningful word tokens (no stopwords)."""
    raw = _normalize(text)
    tokens: list[str] = []
    current = ""
    for ch in raw:
        if ch.isalnum():
            current += ch
        else:
            if current:
                tokens.append(current)
                current = ""
    if current:
        tokens.append(current)
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def _tokenset(text: Any) -> set[str]:
    """Return the normalized token set for a value (for set operations)."""
    return set(tokenize(text))


def _token_matches(a: str, b: str) -> bool:
    """True if two tokens match via exact, suffix, substring, or alias rule."""
    if a == b:
        return True
    # Suffix-stripped equality (optimize == optimization).
    if _strip_suffix(a) == _strip_suffix(b):
        return True
    # Substring containment for compound words (mem matches memory).
    if a in b or b in a:
        return True
    # Alias/synonym groups.
    ga, gb = _ALIAS_INDEX.get(a), _ALIAS_INDEX.get(b)
    if ga is not None and ga == gb:
        return True
    return False


def _matched_fraction(set_a: set[str], set_b: set[str]) -> float:
    """Fraction of ``set_a`` tokens that have a match in ``set_b``, in [0, 1]."""
    if not set_a:
        return 0.0
    matched = 0
    for ta in set_a:
        if any(_token_matches(ta, tb) for tb in set_b):
            matched += 1
    return matched / len(set_a)


def keyword_overlap(a: Any, b: Any) -> float:
    """Return an overlap score in [0, 1] between two texts.

    Uses the *overlap coefficient* (intersection / size of the smaller set)
    rather than pure Jaccard, so a focused plan that is a subset of the goal's
    concepts scores highly. Substring/alias matching makes the comparison robust
    to wording changes.
    """
    set_a = _tokenset(a)
    set_b = _tokenset(b)
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = sum(1 for ta in set_a if any(_token_matches(ta, tb) for tb in set_b))
    smaller = min(len(set_a), len(set_b))
    return intersection / smaller


def term_frequency(text: Any, terms: list[str]) -> float:
    """Fraction of the given *phrases* present (via fuzzy match) in the text.

    Each element of ``terms`` is treated as a phrase: it counts as present when
    at least half of its tokens match the text (fuzzy/alias). Returns [0, 1].
    """
    if not terms:
        return 1.0
    target = _tokenset(text)
    if not target:
        return 0.0
    hits = 0
    for term in terms:
        term_tokens = tokenize(term)
        if not term_tokens:
            continue
        matched = sum(1 for tt in term_tokens if any(_token_matches(tt, t) for t in target))
        if matched >= max(1, len(term_tokens) // 2):
            hits += 1
    return hits / len(terms)


# Short but meaningful domain tokens that should always count as topics even
# though they are brief (e.g. "ram", "api", "db").
_SALIENT_SHORT: set[str] = {
    "ram",
    "api",
    "db",
    "gpu",
    "cpu",
    "io",
    "ui",
    "os",
    "log",
    "bug",
    "fix",
    "web",
    "cli",
    "sdk",
    "sql",
    "xml",
    "json",
    "yaml",
    "css",
    "html",
    "dom",
}


def salient_tokens(text: Any, min_len: int = 4) -> set[str]:
    """Return the 'content' tokens of a text: longer non-stopword tokens.

    Short words (verbs, articles, numbers) are excluded so the salient set
    captures the *topic* nouns rather than generic wording. A small set of brief
    but meaningful domain tokens (e.g. "ram", "api") is always retained.
    """
    tokens = tokenize(text)
    return {t for t in tokens if t in _SALIENT_SHORT or len(t) >= min_len}


def topic_alignment(goal: Any, work: Any) -> float:
    """Topical alignment between a goal and the work done toward it, in [0, 1].

    This is the core "are we still talking about the same thing?" measure. It
    computes recall of the goal's salient (topic) tokens within the work text
    using fuzzy + alias matching, then applies a floor: if *any* goal topic token
    is present in the work, alignment is at least 0.7, because sharing even one
    dominant concept (e.g. "memory") means the work is on-topic.
    """
    goal_topics = salient_tokens(goal)
    work_tokens = _tokenset(work)
    if not goal_topics:
        return 1.0
    if not work_tokens:
        return 0.0
    matched = sum(1 for gt in goal_topics if any(_token_matches(gt, wt) for wt in work_tokens))
    recall = matched / len(goal_topics)
    # Floor: on-topic work (shares at least one dominant concept) is well aligned.
    if matched >= 1:
        return max(0.7, min(1.0, 0.7 + 0.3 * recall))
    return recall


def get_text(context: dict[str, Any], key: str, default: str = "") -> str:
    """Safely fetch a string field from original_goal / current_plan / execution."""
    for section in ("original_goal", "current_plan", "execution_context"):
        section_data = context.get(section, {}) or {}
        if key in section_data and section_data[key] is not None:
            return _normalize(section_data[key])
    return default


def get_list(context: dict[str, Any], key: str) -> list[Any]:
    """Safely fetch a list field from any context section."""
    for section in ("original_goal", "current_plan", "execution_context"):
        section_data = context.get(section, {}) or {}
        value = section_data.get(key)
        if isinstance(value, list):
            return value
    return []


def is_empty(context: dict[str, Any]) -> bool:
    """True when the context carries no meaningful content in any section."""
    for section in ("original_goal", "current_plan", "execution_context"):
        if _normalize(context.get(section, {})).strip():
            return False
    return True


def parse_git_diff(diff: Any) -> dict[str, int]:
    """Count added, removed, and total lines and files from a unified diff.

    Returns a dict with ``added``, ``removed``, ``total`` line counts and a
    ``files`` count parsed from ``diff --git`` headers.
    """
    if not isinstance(diff, str) or not diff.strip():
        return {"added": 0, "removed": 0, "total": 0, "files": 0}

    added = removed = files = 0
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            files += 1
        elif line.startswith("+++") or line.startswith("---"):
            continue
        elif line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            removed += 1
    return {
        "added": added,
        "removed": removed,
        "total": added + removed,
        "files": files,
    }
