.PHONY: help install run clean test lint

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run the bot locally"
	@echo "  make clean      - Clean temporary files"
	@echo "  make lint       - Run code linting"
	@echo "  make setup-env  - Create .env file from example"

install:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt

run:
	. venv/bin/activate && python bot.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache

lint:
	. venv/bin/activate && python -m py_compile bot.py claude_client.py config.py

setup-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your credentials."; \
	else \
		echo ".env file already exists."; \
	fi

