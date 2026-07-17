from intent_alignment.models import Evidence, ScoreComponent
from intent_alignment.utils import (
    compute_confidence,
    determine_status,
    generate_recommendation,
    generate_risk_assessment,
    generate_summary,
)


class TestUtils:
    """Unit tests for utility functions."""

    def test_compute_confidence_empty(self):
        assert compute_confidence([]) == 0.0

    def test_compute_confidence_consistent(self):
        evidence = [
            Evidence(source="p1", value=0.9, confidence=0.9, details="A"),
            Evidence(source="p2", value=0.85, confidence=0.9, details="B"),
        ]
        confidence = compute_confidence(evidence)
        assert 0 <= confidence <= 100
        # High consistency should give high confidence
        assert confidence > 70

    def test_compute_confidence_conflicting(self):
        evidence = [
            Evidence(source="p1", value=0.9, confidence=0.9, details="A"),
            Evidence(source="p2", value=0.1, confidence=0.9, details="B"),
        ]
        confidence = compute_confidence(evidence)
        # Conflicting evidence should reduce confidence
        assert confidence < 80

    def test_determine_status(self):
        assert determine_status(95) == "Fully_Aligned"
        assert determine_status(80) == "Minor_Drift"
        assert determine_status(60) == "Moderate_Drift"
        assert determine_status(30) == "Major_Drift"
        assert determine_status(10) == "Critical_Drift"

    def test_generate_summary(self):
        components = {
            "goal_provider": ScoreComponent(name="goal_provider", weight=0.3, score=85.0),
            "scope_provider": ScoreComponent(name="scope_provider", weight=0.2, score=50.0),
        }
        summary = generate_summary(components, 70.0)
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_generate_risk_assessment(self):
        components = {
            "goal_provider": ScoreComponent(name="goal_provider", weight=0.3, score=85.0),
            "scope_provider": ScoreComponent(name="scope_provider", weight=0.2, score=45.0),
        }
        risk = generate_risk_assessment([], components)
        assert isinstance(risk, str)
        assert "scope" in risk.lower() or "risk" in risk.lower()

    def test_generate_recommendation(self):
        components = {
            "goal_provider": ScoreComponent(name="goal_provider", weight=0.3, score=85.0),
        }
        rec = generate_recommendation(components, 85.0)
        assert "monitor" in rec.lower()

        rec_low = generate_recommendation(components, 20.0)
        assert "immediate" in rec_low.lower() or "reassessment" in rec_low.lower()
