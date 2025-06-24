.PHONY: test coverage clean install-dev lint format check

# Install development dependencies
install-dev:
	pip install pre-commit black isort flake8 mypy bandit coverage pytest
	pre-commit install

# Run all tests
test:
	python -m pytest

# Run tests with coverage report
coverage:
	python -m coverage run -m pytest
	python -m coverage report -m
	python -m coverage html

# Format code
format:
	black .
	isort .

# Lint code
lint:
	flake8 .
	mypy .
	bandit -r abstractions/ -f json -o bandit-report.json || true

# Run all checks (format, lint, test)
check: format lint test

# Clean coverage and cache files
clean:
	rm -rf htmlcov/
	rm -f .coverage
	rm -f bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
