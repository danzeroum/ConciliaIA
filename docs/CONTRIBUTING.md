# 🤝 Contributing to BuildToValue v7

Thank you for your interest in contributing to BuildToValue! This document provides guidelines and instructions for contributing.

## 📑 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Documentation](#documentation)
8. [Community](#community)

---

## Code of Conduct

BuildToValue is committed to providing a welcoming and inclusive environment. Please read and follow our [Code of Conduct](./CODE_OF_CONDUCT.md).

**Quick Summary:**
- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards others

---

## How to Contribute

There are many ways to contribute to BuildToValue:

### 🐛 Report Bugs

Found a bug? Help us fix it!

1. **Check existing issues** - Search [GitHub Issues](https://github.com/buildtovalue/v7/issues) first
2. **Create detailed bug report** - Use the bug report template
3. **Provide reproduction steps** - Clear steps to reproduce the issue
4. **Include environment details** - OS, version, configuration

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- BuildToValue Version: [e.g., 7.0.0]
- Foundation Level: [e.g., standard]
- Docker Version: [e.g., 24.0.0]

**Additional context**
Any other relevant information.
```

### ✨ Suggest Features

Have an idea for improvement?

1. **Check existing feature requests** - Avoid duplicates
2. **Create feature request** - Use the feature request template
3. **Explain the use case** - Why is this needed?
4. **Consider alternatives** - What other solutions exist?

**Feature Request Template:**
```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Use case**
How would this feature be used?

**Additional context**
Mockups, examples, or other details.
```

### 📝 Improve Documentation

Documentation is crucial! You can help by:

- Fixing typos or clarifying confusing sections
- Adding examples or use cases
- Translating documentation
- Writing tutorials or guides

### 💻 Submit Code

Ready to contribute code? Great!

1. **Find an issue** - Look for `good-first-issue` or `help-wanted` labels
2. **Comment on the issue** - Let others know you're working on it
3. **Fork and create branch** - Follow our branching strategy
4. **Write code** - Follow our coding standards
5. **Add tests** - Ensure good coverage
6. **Submit PR** - Use the pull request template

---

## Development Setup

### Prerequisites

- **Git:** 2.30+
- **Docker:** 20.10+
- **Docker Compose:** 2.0+
- **Python:** 3.11+ (for Python scripts)
- **Node.js:** 18+ (optional, for frontend tools)

### Fork and Clone
```bash
# Fork repository on GitHub
# Then clone your fork

git clone https://github.com/YOUR_USERNAME/buildtovalue-v7.git
cd buildtovalue-v7

# Add upstream remote
git remote add upstream https://github.com/buildtovalue/v7.git
```

### Set Up Development Environment
```bash
# Copy environment file
cp .env.example .env.dev

# Edit .env.dev with your configuration
nano .env.dev

# Set your API keys (for testing)
OPENAI_API_KEY=sk-your-test-key-here

# Initialize project
./scripts/init-v7.sh --foundation=standard

# Start development environment
docker-compose up -d

# Verify setup
./scripts/troubleshooting/health-check.sh
```

### Install Development Dependencies
```bash
# Python dependencies
pip install -r requirements-dev.txt

# Pre-commit hooks (recommended)
pre-commit install

# Verify installation
pre-commit run --all-files
```

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_orchestrator.py

# Run with verbose output
pytest -v

# Run only fast tests (skip slow integration tests)
pytest -m "not slow"
```

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:
```python
# Good: Clear, descriptive names
def route_problem_to_squad(problem: str, context: dict) -> RoutingResult:
    """Route problem to appropriate IA squad."""
    pass

# Bad: Unclear names
def rp(p, c):
    pass

# Good: Type hints
def calculate_confidence(
    similarity_score: float,
    historical_success: int,
    total_attempts: int
) -> float:
    pass

# Good: Docstrings (Google style)
def validate_input(data: dict) -> bool:
    """
    Validate input data against schema.
    
    Args:
        data: Dictionary containing input data
    
    Returns:
        True if valid, False otherwise
    
    Raises:
        ValidationError: If data structure is invalid
    
    Example:
        >>> validate_input({'problem': 'test'})
        True
    """
    pass
```

### Code Formatting

We use automated formatters:
```bash
# Black - Code formatter
black src/ tests/

# isort - Import sorter
isort src/ tests/

# flake8 - Linter
flake8 src/ tests/

# mypy - Type checker
mypy src/

# Run all formatters
make format
```

### Git Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

**Examples:**
```bash
# Good
feat(orchestrator): add ML-based routing algorithm

Implements machine learning routing using sentence transformers
for improved accuracy. Includes caching for performance.

Closes #123

# Good
fix(squad): prevent persona config corruption

Adds validation when loading persona YAML files to prevent
corruption from malformed configuration.

Fixes #456

# Bad (too vague)
fix: bug fix

# Bad (no scope)
updated code
```

### Branch Naming
```bash
# Feature branches
git checkout -b feat/ml-routing-algorithm

# Bug fix branches
git checkout -b fix/persona-loading-error

# Documentation branches
git checkout -b docs/api-reference-update

# Refactoring branches
git checkout -b refactor/database-queries
```

---

## Testing Guidelines

### Test Structure
```python
# tests/test_orchestrator.py

import pytest
from src.orchestrator import route_problem

class TestRouting:
    """Test suite for routing functionality"""
    
    @pytest.fixture
    def mock_personas(self):
        """Fixture providing mock persona data"""
        return [
            {"id": "ia-developer", "autonomy": 3},
            {"id": "ia-arquiteto", "autonomy": 4}
        ]
    
    def test_route_simple_problem(self, mock_personas):
        """Test routing of simple problem"""
        result = route_problem("Implement authentication")
        
        assert result.primary_ia == "ia-developer"
        assert result.confidence > 0.75
    
    def test_route_with_context(self):
        """Test routing with additional context"""
        result = route_problem(
            "Design architecture",
            context={"complexity": "high"}
        )
        
        assert result.primary_ia == "ia-arquiteto"
    
    @pytest.mark.parametrize("problem,expected_ia", [
        ("Fix bug", "ia-developer"),
        ("Design database", "ia-data-architect"),
        ("Security review", "ia-auditor")
    ])
    def test_routing_multiple_cases(self, problem, expected_ia):
        """Test routing for multiple problem types"""
        result = route_problem(problem)
        assert result.primary_ia == expected_ia
    
    @pytest.mark.slow
    def test_routing_performance(self):
        """Test routing performance under load"""
        import time
        
        start = time.time()
        for _ in range(100):
            route_problem("Test problem")
        duration = time.time() - start
        
        assert duration < 10.0  # Should complete in under 10s
```

### Test Coverage Requirements

- **Minimum coverage:** 80% overall
- **Critical paths:** 95%+ coverage
- **New features:** 90%+ coverage
```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html

# Check coverage requirements
pytest --cov=src --cov-fail-under=80
```

### Integration Tests
```python
# tests/integration/test_full_workflow.py

@pytest.mark.integration
async def test_complete_decision_workflow():
    """Test complete decision workflow end-to-end"""
    # 1. Route problem
    routing = await route_problem("Implement user registration")
    
    assert routing.status == "success"
    assert routing.primary_ia is not None
    
    # 2. Activate IA
    activation = await activate_ia(
        routing.primary_ia,
        routing.problem
    )
    
    assert activation.status == "activated"
    
    # 3. Execute decision
    execution = await execute_decision(activation.decision_id)
    
    assert execution.status == "completed"
    
    # 4. Verify in ledger
    decision = await get_decision(execution.decision_id)
    
    assert decision is not None
    assert decision.success is True
```

---

## Pull Request Process

### Before Submitting

**Checklist:**
- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] Added tests for new features
- [ ] Updated documentation
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main
- [ ] No merge conflicts
```bash
# Update your branch
git fetch upstream
git rebase upstream/main

# Run tests
pytest

# Run linters
make lint

# Verify everything works
./scripts/troubleshooting/health-check.sh
```

### Submit Pull Request

1. **Push your branch**
```bash
git push origin feat/your-feature-name
```

2. **Create PR on GitHub**
   - Use the PR template
   - Link related issues
   - Add clear description
   - Request reviews

3. **PR Template**
```markdown
## Description
Clear description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to break)
- [ ] Documentation update

## Related Issues
Closes #123
Related to #456

## How Has This Been Tested?
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

**Test Configuration:**
- Foundation Level: Standard
- Environment: Development
- Docker Version: 24.0.0

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where needed
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests proving my fix/feature works
- [ ] New and existing tests pass locally
- [ ] Any dependent changes have been merged

## Screenshots (if applicable)
Add screenshots showing the changes.

## Additional Notes
Any additional information for reviewers.
```

### Review Process

Your PR will be reviewed by maintainers:

1. **Automated Checks** - CI/CD runs tests and linters
2. **Code Review** - Maintainers review code quality
3. **Discussion** - Address feedback and questions
4. **Approval** - Get required approvals (usually 2)
5. **Merge** - Maintainer merges your PR

**Tips for getting merged faster:**
- Keep PRs focused and small
- Write clear descriptions
- Respond promptly to feedback
- Be open to suggestions
- Test thoroughly

### After Merge
```bash
# Update your local repository
git checkout main
git pull upstream main

# Delete your feature branch
git branch -d feat/your-feature-name
git push origin --delete feat/your-feature-name

# Celebrate! 🎉
```

---

## Documentation

### Documentation Standards

- **Clear and concise** - Easy to understand
- **Examples included** - Show how to use features
- **Up to date** - Keep in sync with code
- **Well organized** - Logical structure

### Documentation Types

**README.md** - Project overview
**Guides** - How-to tutorials
**Reference** - API documentation
**Examples** - Real-world use cases

### Writing Documentation
```markdown
# Good: Clear title and description

## Feature: ML-Based Routing

BuildToValue v7 uses machine learning to route problems to the most appropriate IA.

### How It Works

1. Problem is analyzed
2. Embedding generated
3. Similarity search performed
4. Best IA selected

### Example

```python
result = route_problem("Implement authentication")
print(f"Route to: {result.primary_ia}")
# Output: Route to: ia-developer
```

### Configuration

See [Configuration Guide](./CONFIGURATION-GUIDE.md#routing) for options.
```

### Updating Documentation

When you change code that affects documentation:

1. Update relevant documentation files
2. Run spell checker: `make spellcheck`
3. Test examples work
4. Update version numbers if needed

---

## Community

### Get Help

- **Discord:** Join our [Discord server](https://discord.gg/buildtovalue)
- **GitHub Discussions:** Ask questions in [Discussions](https://github.com/buildtovalue/v7/discussions)
- **Stack Overflow:** Tag questions with `buildtovalue`

### Stay Updated

- **GitHub:** Watch the repository
- **Repositório:** https://github.com/danzeroum/ConciliaIA
- **Twitter:** Follow [@buildtovalue](https://twitter.com/buildtovalue)
- **Newsletter:** Subscribe to updates

### Recognition

Contributors are recognized in:
- **CHANGELOG.md** - Credited in release notes
- **README.md** - Listed in contributors section
- **Hall of Fame** - Top contributors featured

### Maintainers

Current maintainers:
- **@maintainer1** - Core development
- **@maintainer2** - Documentation
- **@maintainer3** - Community management

Want to become a maintainer? Show consistent, high-quality contributions!

---

## Development Tips

### Useful Commands
```bash
# Development
make dev              # Start development environment
make test             # Run tests
make lint             # Run linters
make format           # Format code

# Documentation
make docs             # Build documentation
make docs-serve       # Serve documentation locally

# Release
make release          # Create release (maintainers only)
```

### Debugging
```python
# Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()

# Or use breakpoint (Python 3.7+)
breakpoint()
```

### Performance Profiling
```bash
# Profile a script
python -m cProfile -o profile.stats script.py

# View results
python -m pstats profile.stats

# Generate flame graph
./scripts/troubleshooting/generate-flamegraph.sh
```

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

- **Technical questions:** [GitHub Discussions](https://github.com/buildtovalue/v7/discussions)
- **Security issues:** https://github.com/danzeroum/ConciliaIA/security (private)
- **Other inquiries:** danniellau@gmail.com

---

Thank you for contributing to BuildToValue! 🚀

**Document Version:** 7.0.0  
**Last Updated:** 2025-01-20

© 2025 BuildToValue | [Main Documentation](./README.md) | [Code of Conduct](./CODE_OF_CONDUCT.md)
