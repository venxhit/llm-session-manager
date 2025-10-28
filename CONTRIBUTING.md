# Contributing to LLM Session Manager

Thank you for your interest in contributing to LLM Session Manager! We welcome contributions from the community.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- Git
- Node.js 18+ (for frontend development)

### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/llm-session-manager.git
cd llm-session-manager

# Install dependencies
poetry install

# Run tests to verify setup
python tests/test_cli_automated.py
```

Expected output: **14/14 tests passing** ✅

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clear, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation if needed

### 3. Add Tests

**Important:** All new features must include tests.

```bash
# Add your tests to tests/test_cli_automated.py
# or create a new test file

# Run tests
python tests/test_cli_automated.py

# Ensure all tests pass (14/14 or more)
```

### 4. Test Manually

```bash
# Test CLI changes
poetry run python -m llm_session_manager.cli <your-command>

# Test backend changes
cd backend
uvicorn app.main:app --reload

# Test frontend changes
cd frontend
npm run dev
```

### 5. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: Add support for Windsurf AI sessions"
# or
git commit -m "fix: Resolve token counting issue for long sessions"
# or
git commit -m "docs: Update installation guide"
```

**Commit message format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Link to any related issues
- Screenshots/GIFs if UI changes
- Test results

## Code Style

### Python
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Keep functions focused and small
- Add docstrings for public functions

### JavaScript/React
- Use functional components
- Follow existing naming conventions
- Keep components small and reusable

## Testing Guidelines

### Automated Tests

All code must pass existing tests:

```bash
# Run CLI tests
python tests/test_cli_automated.py

# Run backend tests
python tests/test_backend_automated.py
```

### Test Coverage

We maintain **100% test coverage** for core functionality:
- CLI commands
- Session discovery
- Health monitoring
- Export functionality
- Memory operations
- Tagging system

When adding features, add corresponding tests.

## Areas We'd Love Help With

### High Priority
- 🔍 **AI Tool Support** - Integration with Windsurf, Aider, Cody, etc.
- 🧠 **Pattern Recognition** - Improved AI-powered insights
- 🎨 **UI/UX** - Better visualizations and user experience
- 📱 **Mobile Support** - Responsive design improvements

### Medium Priority
- 📚 **Documentation** - Tutorials, guides, examples
- 🌐 **Internationalization** - Multi-language support
- ⚡ **Performance** - Optimization and caching
- 🔌 **Integrations** - Slack, Discord, webhooks

### Good First Issues

Look for issues tagged with `good-first-issue` on GitHub. These are perfect for new contributors!

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Join our community (if applicable)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

### Not Acceptable

- Harassment or discrimination
- Trolling or inflammatory comments
- Spam or off-topic discussions
- Publishing others' private information

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md (Contributors section)
- Release notes
- Project documentation

Thank you for contributing! 🎉
