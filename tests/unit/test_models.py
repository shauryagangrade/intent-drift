from intent_alignment.models import (
    AlignmentContext,
    AlignmentReport,
    Evidence,
    ScoreComponent,
)


class TestModels:
    """Unit tests for data models."""

    def test_alignment_context_creation(self):
        ctx = AlignmentContext(
            original_goal={"text": "Test goal"},
            current_plan={"summary": "Test plan"},
            execution_context={"edited_files": ["a.py"]},
        )
        assert ctx.original_goal["text"] == "Test goal"
        assert ctx.current_plan["summary"] == "Test plan"
        assert "a.py" in ctx.execution_context["edited_files"]

    def test_evidence_creation(self):
        ev = Evidence(source="test", value=0.85, confidence=0.9, details="Test evidence")
        assert ev.source == "test"
        assert 0 <= ev.value <= 1
        assert 0 <= ev.confidence <= 1

    def test_score_component_creation(self):
        comp = ScoreComponent(name="test", weight=0.3, score=85.0)
        assert comp.name == "test"
        assert comp.weight == 0.3
        assert comp.score == 85.0

    def test_alignment_report_creation(self):
        report = AlignmentReport(
            overall_alignment=82.0,
            confidence=91.0,
            status="Minor_Drift",
            breakdown={"goal_provider": {"score": 88.0, "weight": 0.3}},
            summary="Test summary",
            evidence=[],
            risk="Test risk",
            recommendation="Test recommendation",
            timeline=[],
        )
        assert report.overall_alignment == 82.0
        assert report.confidence == 91.0
        assert report.status == "Minor_Drift"
        assert len(report.evidence) == 0
