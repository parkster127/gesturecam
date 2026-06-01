# Contributing to GestureCam

Thank you for your interest in contributing to GestureCam! We welcome contributions from everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code.

**Be respectful, inclusive, and collaborative.**

## Getting Started

### Fork the Repository

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/your-username/gesturecam.git
cd gesturecam
```

3. Add the upstream repository:

```bash
git remote add upstream https://github.com/original-owner/gesturecam.git
```

## Development Setup

### Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Pre-commit Setup

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit manually
pre-commit run --all-files
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=gesturecam tests/

# Run specific test file
pytest tests/test_gestures.py
```

## Submitting Changes

### Workflow

1. Create a new branch for your feature/fix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-123
```

2. Make your changes and test them

3. Commit your changes with a clear message:

```bash
git commit -m "feat: add new gesture for volume control"
```

4. Push to your fork:

```bash
git push origin feature/your-feature-name
```

5. Create a Pull Request on GitHub

### Commit Message Format

We use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add pinch gesture for smooth zoom
fix: resolve camera initialization issue on macOS
docs: update API reference for gesture module
```

### Pull Request Guidelines

- Describe your changes in the PR description
- Link to related issues
- Ensure all tests pass
- Update documentation if needed
- Keep PRs focused on a single change

## Coding Standards

### Python Code Style

We follow PEP 8 guidelines:

```bash
# Linting
ruff check gesturecam/

# Formatting
black gesturecam/
```

### Code Quality

- Write clear, descriptive variable names
- Add docstrings to functions and classes
- Keep functions focused and under 50 lines
- Add type hints where appropriate
- Write tests for new features

### Example Code

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class GestureResult:
    """Result of gesture detection.

    Attributes:
        gesture: The detected gesture type
        confidence: Detection confidence (0.0 - 1.0)
        landmarks: Detected hand landmarks
    """
    gesture: str
    confidence: float
    landmarks: Optional[list] = None

def detect_gesture(landmarks: list) -> GestureResult:
    """Detect a gesture from hand landmarks.

    Args:
        landmarks: List of hand landmark coordinates

    Returns:
        GestureResult with detected gesture and confidence
    """
    # Implementation here
    pass
```

## Reporting Bugs

### Before Reporting

1. Check existing [issues](https://github.com/parkster127/gesturecam/issues)
2. Try the latest version
3. Check [troubleshooting guide](./docs/TROUBLESHOOTING.md)

### Bug Report Template

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. macOS 14.0, Windows 11, Ubuntu 22.04]
 - Python version: [e.g. 3.11]
 - Camera: [e.g. Logitech C920]
 - GestureCam version: [e.g. 0.1.0]

**Additional context**
Add any other context about the problem here.
```

## Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## Questions?

- Check our [documentation](./README.md)
- Search [existing discussions](https://github.com/parkster127/gesturecam/discussions)
- Ask in [GitHub Discussions](https://github.com/parkster127/gesturecam/discussions/new)

---

**Thank you for contributing to GestureCam!**