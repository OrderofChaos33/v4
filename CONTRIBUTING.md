# Contributing to 280E MVP

We welcome contributions to improve the 280E Expense Reclassification MVP!

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone repository
git clone https://github.com/OrderofChaos33/v4.git
cd v4

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install black pylint mypy

# Run tests
pytest tests/ -v
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Write tests for new features

## Testing

All new features should include tests:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_classifier.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Areas for Contribution

### High Priority
- [ ] Real LLM integration (OpenAI/Anthropic)
- [ ] Database persistence layer
- [ ] User authentication
- [ ] Enhanced classification rules
- [ ] State-specific guidance

### Medium Priority
- [ ] Batch processing improvements
- [ ] QuickBooks/NetSuite API integration
- [ ] Manual override UI
- [ ] Email notifications
- [ ] Historical analysis

### Documentation
- [ ] More example use cases
- [ ] Video tutorials
- [ ] Tax professional guide
- [ ] API client libraries (Python, JavaScript)

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Sample data (if applicable, anonymized)

## Security

If you discover a security vulnerability, please email the maintainers directly rather than opening a public issue.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE.txt).

## Questions?

Open an issue for questions or discussions about the project.

Thank you for contributing!
