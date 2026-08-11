"""Unit tests verifying explicit __all__ exports for all public modules."""

import importlib


def test_models_all_exports():
    module = importlib.import_module("intent_alignment.models")
    assert hasattr(module, "__all__")
    expected = ["AlignmentContext", "AlignmentReport", "Evidence", "ScoreComponent"]
    assert sorted(module.__all__) == sorted(expected)
    for name in expected:
        assert hasattr(module, name)


def test_utils_all_exports():
    module = importlib.import_module("intent_alignment.utils")
    assert hasattr(module, "__all__")
    expected = [
        "compute_confidence",
        "determine_status",
        "generate_summary",
        "generate_risk_assessment",
        "generate_recommendation",
    ]
    assert sorted(module.__all__) == sorted(expected)
    for name in expected:
        assert hasattr(module, name)


def test_scoring_all_exports():
    module = importlib.import_module("intent_alignment.scoring")
    assert hasattr(module, "__all__")
    expected = ["compute_weighted_score", "aggregate_scores"]
    assert sorted(module.__all__) == sorted(expected)
    for name in expected:
        assert hasattr(module, name)


def test_report_all_exports():
    module = importlib.import_module("intent_alignment.report")
    assert hasattr(module, "__all__")
    expected = ["render_report"]
    assert sorted(module.__all__) == sorted(expected)
    for name in expected:
        assert hasattr(module, name)


def test_evidence_base_all_exports():
    module = importlib.import_module("intent_alignment.evidence.base")
    assert hasattr(module, "__all__")
    expected = ["EvidenceProvider"]
    assert sorted(module.__all__) == sorted(expected)
    for name in expected:
        assert hasattr(module, name)


def test_evidence_analysis_all_exports():
    module = importlib.import_module("intent_alignment.evidence.analysis")
    assert hasattr(module, "__all__")
    expected = [
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
    assert sorted(module.__all__) == sorted(expected)
    for name in expected:
        assert hasattr(module, name)


def test_engine_all_exports():
    module = importlib.import_module("intent_alignment.engine")
    assert hasattr(module, "__all__")
    expected = ["IntentAlignmentEngine"]
    assert sorted(module.__all__) == sorted(expected)
    for name in expected:
        assert hasattr(module, name)
