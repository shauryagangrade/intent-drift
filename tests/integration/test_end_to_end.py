import pytest

from intent_alignment.engine import IntentAlignmentEngine
from intent_alignment.models import AlignmentContext
from intent_alignment.report import render_report


class TestEndToEnd:
    """Integration tests for the full engine pipeline."""

    @pytest.fixture
    def engine(self):
        return IntentAlignmentEngine()

    @pytest.fixture
    def aligned_context(self):
        """Context where current work aligns with original goal."""
        return AlignmentContext(
            original_goal={
                "text": "Reduce the application's memory usage.",
                "constraints": ["Stay under 100MB RAM"],
                "success_criteria": ["Peak memory < 50MB"],
            },
            current_plan={
                "summary": "Refactoring memory allocation in core modules.",
                "steps": ["Profile memory usage", "Optimize allocation"],
            },
            execution_context={
                "edited_files": ["memory_manager.py", "allocator.py"],
                "git_diff": "+ def optimize_allocation():\n+     # Reduce memory footprint\n",
                "recent_commands": ["python -m memory_profiler"],
                "recent_messages": ["Working on memory optimization"],
                "reasoning_summary": "Focusing on reducing memory consumption",
            },
        )

    @pytest.fixture
    def drifted_context(self):
        """Context where current work has drifted from original goal."""
        return AlignmentContext(
            original_goal={
                "text": "Reduce the application's memory usage.",
                "constraints": ["Stay under 100MB RAM"],
                "success_criteria": ["Peak memory < 50MB"],
            },
            current_plan={
                "summary": "Optimizing startup initialization for faster application load.",
                "steps": ["Profile startup bottlenecks", "Optimize initialization"],
            },
            execution_context={
                "edited_files": ["main.py", "startup.py", "initialization.py"],
                "git_diff": "- def reduce_memory():\n+ def optimize_startup():\n+     # Startup optimizations\n",
                "recent_commands": ["pip install numpy", "python -m cProfile"],
                "recent_messages": ["We're making progress on startup optimization"],
                "reasoning_summary": "Focusing on startup performance rather than memory optimization",
            },
        )

    def test_full_pipeline_aligned(self, engine, aligned_context):
        """Test full pipeline with aligned context."""
        report = engine.evaluate(aligned_context)
        assert report.status in ("Fully_Aligned", "Minor_Drift")
        assert report.overall_alignment > 70
        assert len(report.evidence) > 0

        # Test report rendering
        rendered = render_report(report)
        assert "Overall Alignment" in rendered
        assert "Confidence" in rendered
        assert "Evidence" in rendered

    def test_full_pipeline_drifted(self, engine, drifted_context):
        """Test full pipeline with drifted context."""
        report = engine.evaluate(drifted_context)
        # Drift should be detected - either moderate or worse
        assert report.status in ("Moderate_Drift", "Major_Drift", "Critical_Drift")
        assert report.overall_alignment < 75
        # Should recommend reassessment
        assert "reassess" in report.recommendation.lower()

    def test_report_contains_required_sections(self, engine, aligned_context):
        """Test that rendered report contains all required sections."""
        report = engine.evaluate(aligned_context)
        rendered = render_report(report)

        required_sections = [
            "Intent Alignment Report",
            "Overall Alignment",
            "Status",
            "Confidence",
            "Summary",
            "Evidence",
            "Risk",
            "Recommendation",
            "Breakdown",
        ]
        for section in required_sections:
            assert section in rendered

    def test_multiple_evaluations_consistency(self, engine, aligned_context):
        """Test that repeated evaluations give consistent results."""
        report1 = engine.evaluate(aligned_context)
        report2 = engine.evaluate(aligned_context)
        assert report1.overall_alignment == report2.overall_alignment
        assert report1.status == report2.status
