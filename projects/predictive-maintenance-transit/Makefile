.PHONY: install test run clean lint format fetch docker-build docker-run

PYTHON := python3
PIP := pip3

install:
	$(PIP) install -e ".[dev]"

fetch:
	$(PYTHON) -m src.data.loader --download

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

run:
	$(PYTHON) -m src.pipeline.orchestrator

dashboard:
	streamlit run src/visualization/dashboard.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache/ .coverage/ htmlcov/ build/ dist/ *.egg-info/

lint:
	ruff check src/ tests/
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/
	ruff check --fix src/ tests/

docker-build:
	docker build -t predictive-maintenance .

docker-run:
	docker run -p 8501:8501 -v $(PWD)/data:/app/data predictive-maintenance
