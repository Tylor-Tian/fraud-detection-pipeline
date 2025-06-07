# Contributing to Fraud Detection Pipeline

First off, thank you for considering contributing to Fraud Detection Pipeline! It's people like you that make this project such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include logs and error messages**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and explain which behavior you expected to see instead**
* **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/Tylor-Tian/fraud-detection-pipeline.git
   cd fraud-detection-pipeline
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Run tests to ensure everything is working**
   ```bash
   pytest
   ```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run tests and linting**
   ```bash
   make test
   make lint
   ```

4. **Format your code**
   ```bash
   make format
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template
   - Submit!

## Style Guide

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these additional guidelines:

* Line length: 100 characters
* Use type hints where possible
* Write docstrings for all public functions and classes
* Use meaningful variable names

### Code Formatting

We use `black` for code formatting and `isort` for import sorting:

```bash
black fraud_detection/
isort fraud_detection/
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
Add fraud detection rule for velocity checks

- Implement velocity checking across time windows
- Add configuration for velocity thresholds
- Include tests for edge cases

Fixes #123
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fraud_detection

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest -v
```

### Writing Tests

* Write tests for all new functionality
* Maintain test coverage above 80%
* Use descriptive test names
* Include both positive and negative test cases
* Mock external dependencies

Example test:
```python
def test_process_transaction_with_high_amount():
    """Test that high amount transactions are flagged correctly."""
    detector = FraudDetectionSystem()
    transaction = Transaction(
        transaction_id="TEST001",
        amount=15000,  # High amount
        # ... other fields
    )
    
    result = detector.process_transaction(transaction)
    
    assert result.is_fraud is True
    assert "HIGH_AMOUNT" in result.flags
```

## Documentation

* Update the README.md if needed
* Add docstrings to all public APIs
* Update the docs/ folder for significant changes
* Include examples in documentation

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create a tag: `git tag -a v1.0.0 -m "Release version 1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will handle the rest

## Questions?

Feel free to open an issue with your question or contact the maintainers directly.

Thank you for contributing! 🎉
