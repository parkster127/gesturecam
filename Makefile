.PHONY: install dev lint format test run clean

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

lint:
	ruff check gesturecam/ main.py

format:
	black gesturecam/ main.py
	ruff check --fix gesturecam/ main.py

test:
	pytest tests/test_core.py tests/test_vision.py -v

run:
	python3 main.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info