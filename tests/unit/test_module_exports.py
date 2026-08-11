"""Unit tests verifying explicit __all__ exports for all public modules."""

import importlib

import pytest

MODULE_EXPORTS = [
    (
        "intent_alignment.models",
        ["AlignmentContext", "AlignmentReport", "Evidence", "ScoreComponent"],
    ),
    (
        "intent_alignment.utils",
        [
            "compute_confidence",
            "determine_status",
            "generate_summary",
            "generate_risk_assessment",
            "generate_recommendation",
        ],
    ),
    (
        "intent_alignment.scoring",
        ["compute_weighted_score", "aggregate_scores"],
    ),
    ("intent_alignment.report", ["render_report"]),
    ("intent_alignment.evidence.base", ["EvidenceProvider"]),
    (
        "intent_alignment.evidence.analysis",
        [
            "tokenize",
            "keyword_overlap",
            "term_frequency",
            "salient_tokens",
            "topic_alignment",
            "get_text",
            "get_list",
            "is_empty",
            "parse_git_diff",
        ],
    ),
    ("intent_alignment.engine", ["IntentAlignmentEngine"]),
]


@pytest.mark.parametrize(("module_name", "expected"), MODULE_EXPORTS)
def test_all_exports(module_name: str, expected: list[str]) -> None:
    module = importlib.import_module(module_name)
    assert set(module.__all__) == set(expected)

    namespace: dict[str, object] = {}
    exec(f"from {module_name} import *", namespace)
    namespace.pop("__builtins__", None)
    assert set(namespace) == set(expected)
