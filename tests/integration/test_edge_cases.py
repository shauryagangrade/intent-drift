import pytest

from intent_alignment.engine import IntentAlignmentEngine
from intent_alignment.models import AlignmentContext, Evidence


class TestEdgeCases:
    """Edge case tests for the engine."""

    @pytest.fixture
    def engine(self):
        return IntentAlignmentEngine()

    def test_empty_context(self, engine):
        """Test engine with completely empty context."""
        ctx = AlignmentContext(original_goal={}, current_plan={}, execution_context={})
        # Should not raise, should return a valid report
        report = engine.evaluate(ctx)
        assert report is not None
        assert hasattr(report, "overall_alignment")

    def test_minimal_context(self, engine):
        """Test with minimal valid context."""
        ctx = AlignmentContext(
            original_goal={"text": "Do X"},
            current_plan={"summary": "Doing X"},
            execution_context={"edited_files": ["x.py"]},
        )
        report = engine.evaluate(ctx)
        assert report is not None
        assert report.overall_alignment >= 0

    def test_conflicting_evidence(self, engine):
        """Test with strongly conflicting evidence."""
        # Create a context that triggers conflicting signals
        ctx = AlignmentContext(
            original_goal={"text": "Keep it simple"},
            current_plan={"summary": "Adding 50 features"},
            execution_context={
                "edited_files": ["feature1.py", "feature2.py", "feature3.py"],
                "git_diff": "+ def feature1():\n+ def feature2():\n+ def feature3():\n",
                "recent_messages": ["Adding more functionality"],
                "reasoning_summary": "Expanding scope significantly",
            },
        )
        report = engine.evaluate(ctx)
        # Should detect drift due to scope expansion
        assert report.status in ("Major_Drift", "Critical_Drift", "Moderate_Drift")

    def test_high_similarity_context(self, engine):
        """Test with nearly identical goal and plan."""
        ctx = AlignmentContext(
            original_goal={"text": "Fix the login bug"},
            current_plan={"summary": "Fixing the login authentication bug"},
            execution_context={
                "edited_files": ["auth.py", "login.py"],
                "git_diff": "+ def fix_login_auth():\n+     # Fix authentication\n",
                "recent_messages": ["Fixing login authentication"],
                "reasoning_summary": "Fixing the login authentication bug",
            },
        )
        report = engine.evaluate(ctx)
        assert report.overall_alignment > 70

    def test_custom_provider_low_evidence(self, engine):
        """Test with a custom provider that returns low-value evidence."""

        class LowEvidenceProvider:
            name = "low_provider"
            weight = 0.5

            def collect(self, context):
                return [
                    Evidence(
                        source="low_provider",
                        value=0.1,
                        confidence=0.95,
                        details="Low alignment detected",
                    )
                ]

        engine.add_provider(LowEvidenceProvider())
        ctx = AlignmentContext(
            original_goal={"text": "Original"},
            current_plan={"summary": "Different"},
            execution_context={"edited_files": ["x.py"]},
        )
        report = engine.evaluate(ctx)
        assert report is not None
        # Low evidence should reduce overall alignment
        assert report.overall_alignment < 80
