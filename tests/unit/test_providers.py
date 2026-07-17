import pytest

from intent_alignment.evidence.providers import (
    ArchitectureProvider,
    ConstraintProvider,
    DependencyProvider,
    ExecutionProvider,
    FileGraphProvider,
    GoalProvider,
    ProblematicFindingsProvider,
    RequirementCoverageProvider,
    ScopeProvider,
)
from intent_alignment.models import Evidence


class TestProviders:
    """Unit tests for all evidence providers."""

    @pytest.fixture
    def sample_context(self):
        return {
            "original_goal": {
                "text": "Reduce the application's memory usage.",
                "constraints": ["Stay under 100MB RAM", "Maintain API compatibility"],
                "success_criteria": ["Peak memory < 50MB", "Startup time < 2s"],
            },
            "current_plan": {
                "summary": "Optimizing startup initialization for faster application load.",
                "steps": ["Profile initialization bottlenecks", "Optimize startup sequence"],
            },
            "execution_context": {
                "edited_files": ["main.py", "startup.py"],
                "git_diff": "+ def optimize_startup():\n",
                "recent_commands": ["pip install numpy"],
                "recent_messages": ["Focusing on startup performance"],
                "reasoning_summary": "Optimizing startup sequence",
            },
        }

    @pytest.mark.parametrize(
        "provider_cls",
        [
            GoalProvider,
            ConstraintProvider,
            ScopeProvider,
            ArchitectureProvider,
            ExecutionProvider,
            FileGraphProvider,
            DependencyProvider,
            RequirementCoverageProvider,
            ProblematicFindingsProvider,
        ],
    )
    def test_provider_interface(self, provider_cls, sample_context):
        """Test that all providers implement the required interface."""
        provider = provider_cls()
        evidence = provider.collect(sample_context)

        assert isinstance(provider.name, str)
        assert isinstance(provider.weight, float)
        assert provider.weight > 0
        assert isinstance(evidence, list)
        assert all(isinstance(e, Evidence) for e in evidence)

        for e in evidence:
            assert 0.0 <= e.value <= 1.0
            assert 0.0 <= e.confidence <= 1.0
            assert isinstance(e.details, str)
            assert e.source == provider.name

    def test_goal_provider(self, sample_context):
        provider = GoalProvider()
        evidence = provider.collect(sample_context)
        assert len(evidence) >= 1
        assert evidence[0].source == "goal_provider"

    def test_constraint_provider(self, sample_context):
        provider = ConstraintProvider()
        evidence = provider.collect(sample_context)
        assert evidence[0].source == "constraint_provider"

    def test_empty_context(self):
        empty_context = {"original_goal": {}, "current_plan": {}, "execution_context": {}}
        provider = GoalProvider()
        evidence = provider.collect(empty_context)
        # Should not raise, may return empty or low-confidence evidence
        assert isinstance(evidence, list)
