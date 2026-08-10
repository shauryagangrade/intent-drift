# Intent Alignment Engine

A production-quality, open-source Python library that helps AI coding agents detect and prevent intent drift during development sessions.

## 🎯 Vision

AI coding agents frequently begin working toward the correct objective, but gradually shift toward solving a different problem. This engine acts as an independent "second opinion" that continuously evaluates whether the current work remains aligned with the original request.

## 🔧 Features

- **Evidence-Based Reasoning**: Evaluates multiple independent forms of evidence rather than simple similarity scoring
- **Explainable Assessments**: Every conclusion is traceable to specific evidence points
- **Pluggable Architecture**: Easy to extend with new evidence providers
- **Timeline Tracking**: Monitor alignment drift over time
- **Framework Agnostic**: Works with any AI coding agent (Claude Code, Codex, Gemini, etc.)
- **Type Safe**: Full type hints with Pydantic models and dataclasses
- **Well Tested**: Comprehensive unit and integration tests

## 📦 Installation

```bash
pip install intent-drift
```

## 🚀 Quick Start

```python
from intent_alignment import IntentAlignmentEngine
from intent_alignment.models import AlignmentContext

engine = IntentAlignmentEngine()

context = AlignmentContext(
    original_goal="Reduce the application's memory usage.",
    current_plan="Optimizing startup latency for faster initialization.",
    execution_context={
        "edited_files": ["main.py", "startup.py"],
        "git_diff": "+ def optimize_startup():\n+     # ... startup optimizations\n",
        "recent_commands": ["pip install numpy", "python -m profiler"],
        "reasoning_summary": "Focusing on startup performance improvements"
    }
)

report = engine.evaluate(context)

print(f"Overall Alignment: {report.overall_alignment}%")
print(f"Status: {report.status}")
print(f"Confidence: {report.confidence}%")
print(f"Recommendation: {report.recommendation}")
```

## 📊 Example Output

```
Intent Alignment Report

Overall Alignment
68%

Status
Moderate Drift

Confidence
89%

Original Goal
Reduce the application's memory usage.

Current Goal
Optimize startup initialization.

Summary
The current work has gradually shifted toward startup performance rather than runtime memory reduction.

Evidence
✓ Goal partially overlaps
✓ Constraints remain satisfied
⚠ Edited files primarily affect startup logic
⚠ Current implementation no longer targets memory allocation
⚠ Dependency changes favor performance over memory optimization

Risk
Additional work is unlikely to improve runtime memory usage.

Recommendation
Pause and confirm whether startup optimization was intentional before continuing.
```

## 🏗️ Architecture

```
intent-drift/
├── src/
│   └── intent_alignment/
│       ├── __init__.py
│       ├── engine.py              # Main engine class
│       ├── models.py              # Data models (Pydantic/dataclasses)
│       ├── parser.py              # Context parsing utilities
│       ├── evidence/              # Evidence provider implementations
│       │   ├── __init__.py
│       │   ├── base.py            # Abstract EvidenceProvider
│       │   ├── goal_provider.py
│       │   ├── constraint_provider.py
│       │   ├── scope_provider.py
│       │   ├── file_graph_provider.py
│       │   ├── dependency_provider.py
│       │   ├── architecture_provider.py
│       │   ├── plan_provider.py
│       │   └── execution_provider.py
│       ├── scoring.py             # Evidence scoring and aggregation
│       ├── report.py              # Report generation
│       └── api.py                 # Public API interface
├── tests/
│   ├── unit/
│   └── integration/
├── examples/
├── docs/
├── pyproject.toml
└── LICENSE
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

## 📚 Documentation

See the [docs/](docs/) directory for:
- [Architecture Overview](docs/architecture.md)
- [Evidence Providers](docs/evidence_providers.md)
- [Public API Reference](docs/api.md)
- [Extending the Engine](docs/extending.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by the challenges of intent drift in AI-assisted development and the need for transparent, explainable alignment checking mechanisms.