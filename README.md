# intent-drift

[![PyPI version](https://img.shields.io/pypi/v/intent-drift.svg)](https://pypi.org/project/intent-drift/)
[![Python versions](https://img.shields.io/pypi/pyversions/intent-drift.svg)](https://pypi.org/project/intent-drift/)
[![License](https://img.shields.io/pypi/l/intent-drift.svg)](https://github.com/shauryagangrade/intent-drift/blob/main/LICENSE)

Dependency-free Python library that detects **intent drift** in AI-assisted development: it compares the original goal against the current plan and execution activity, and returns an explainable alignment report.

## Install

```bash
pip install intent-drift   # Python >= 3.10
```

## Quick Start

```python
from intent_alignment import IntentAlignmentEngine

engine = IntentAlignmentEngine()

context = {
    "original_goal": {
        "text": "Reduce the application's memory usage.",
        "constraints": ["Stay under 100MB RAM"],
        "success_criteria": ["Peak memory < 50MB"],
    },
    "current_plan": {
        "summary": "Optimizing startup initialization for faster load.",
        "steps": ["Profile initialization", "Optimize startup sequence"],
    },
    "execution_context": {
        "edited_files": ["startup.py"],
        "git_diff": "+ def optimize_startup(): ...",
        "recent_messages": ["Working on startup optimization"],
        "reasoning_summary": "Focusing on startup performance",
    },
}

report = engine.evaluate(context)
print(report.overall_alignment)  # 0-100
print(report.status)             # e.g. "Moderate_Drift"
print(report.confidence)         # 0-100
print(report.recommendation)
```

`evaluate()` accepts a plain dict or an `AlignmentContext` dataclass. Use `intent_alignment.report.render_report(report)` to render the full text report (evidence, risk, and per-provider breakdown).

## How It Works

The engine runs the context through pluggable **evidence providers** — goal alignment, constraints, scope, architecture, execution, file graph, dependencies, requirement coverage, and problematic findings. Each emits weighted evidence that is aggregated into an overall alignment score, confidence, status, and recommendation. No external NLP dependencies: matching is transparent token/alias-based, so every score is traceable to specific input text.

## Extending

Implement `EvidenceProvider` (`collect(context) -> list[Evidence]`) and register it with `engine.add_provider(provider)`.

## Layout

```
src/intent_alignment/
├── engine.py     # IntentAlignmentEngine, provider registration
├── models.py     # AlignmentContext, AlignmentReport, Evidence, ScoreComponent
├── scoring.py    # Weighted aggregation of provider evidence
├── report.py     # render_report() -> human-readable text
├── utils.py      # Status, confidence, summary, risk, recommendation
└── evidence/     # EvidenceProvider base + 9 providers + shared analysis helpers
tests/            # Unit and integration test suite
examples/         # example_usage.py
```

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

See [CHANGELOG.md](CHANGELOG.md) for releases. License: [MIT](LICENSE).
