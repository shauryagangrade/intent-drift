import pytest

from intent_alignment.engine import IntentAlignmentEngine
from intent_alignment.models import AlignmentContext, Evidence


class TestEngine:
    """Unit tests for the IntentAlignmentEngine."""

    @pytest.fixture
    def engine(self):
        return IntentAlignmentEngine()

    @pytest.fixture
    def basic_context(self):
        return AlignmentContext(
            original_goal={"text": "Reduce memory usage"},
            current_plan={"summary": "Optimizing startup"},
            execution_context={"edited_files": ["main.py"]},
        )

    def test_engine_initialization(self, engine):
        """Test that engine initializes with default providers."""
        assert len(engine.providers) > 0
        assert all(hasattr(p, "name") for p in engine.providers)

    def test_evaluate_returns_report(self, engine, basic_context):
        """Test that evaluate returns a valid AlignmentReport."""
        report = engine.evaluate(basic_context)
        assert hasattr(report, "overall_alignment")
        assert hasattr(report, "confidence")
        assert hasattr(report, "status")
        assert hasattr(report, "breakdown")
        assert hasattr(report, "evidence")

    def test_add_provider(self, engine, basic_context):
        """Test adding a custom provider."""

        class CustomProvider:
            name = "custom"
            weight = 0.1

            def collect(self, context):
                return [Evidence(source="custom", value=0.9, confidence=0.8, details="Test")]

        engine.add_provider(CustomProvider())
        report = engine.evaluate(basic_context)
        assert report is not None

    def test_alignment_score_range(self, engine, basic_context):
        """Test that alignment score is within valid range."""
        report = engine.evaluate(basic_context)
        assert 0 <= report.overall_alignment <= 100
        assert 0 <= report.confidence <= 100

    def test_status_values(self, engine, basic_context):
        """Test that status value is one of expected values."""
        report = engine.evaluate(basic_context)
        valid_statuses = {
            "Fully_Aligned",
            "Minor_Drift",
            "Moderate_Drift",
            "Major_Drift",
            "Critical_Drift",
        }
        assert report.status in valid_statuses

    def test_evidence_collection(self, engine, basic_context):
        """Test that evidence is collected from multiple providers."""
        report = engine.evaluate(basic_context)
        assert len(report.evidence) >= len(engine.providers)
        sources = {e.source for e in report.evidence}
        assert len(sources) >= 1
