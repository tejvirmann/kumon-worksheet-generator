.PHONY: help install run dev clean test setup deploy

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Detect Python executable - prefer python3
PYTHON := $(shell which python3 2>/dev/null || which python 2>/dev/null || echo "python3")
PIP := $(shell which pip3 2>/dev/null || which pip 2>/dev/null || echo "pip3")
# Use venv Python if it exists, otherwise use system Python
VENV_PYTHON := $(shell if [ -f venv/bin/python3 ]; then echo "venv/bin/python3"; elif [ -f venv/bin/python ]; then echo "venv/bin/python"; else echo "$(PYTHON)"; fi)
VENV_PIP := $(shell if [ -f venv/bin/pip3 ]; then echo "venv/bin/pip3"; elif [ -f venv/bin/pip ]; then echo "venv/bin/pip"; else echo "$(PIP)"; fi)

install: ## Install Python dependencies
	@if [ ! -d venv ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv venv; \
	fi
	$(VENV_PIP) install -r requirements.txt
	@echo "✅ Dependencies installed! Use 'make run' to start the app."

setup: ## Initial setup - create directories and copy env.template
	mkdir -p output templates static
	@if [ ! -f .env ]; then \
		echo "Creating .env file from env.template..."; \
		cp env.template .env 2>/dev/null || echo "OPENAI_API_KEY=your_openai_api_key_here" > .env; \
		echo "⚠️  Please edit .env and add your OPENAI_API_KEY"; \
	else \
		echo ".env file already exists"; \
	fi

run: ## Run the Flask app (production mode)
	@if [ ! -d venv ]; then \
		echo "⚠️  Virtual environment not found. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	@echo "Starting Flask app..."
	$(VENV_PYTHON) app.py

run-direct: ## Run the Flask app directly with system Python (no venv)
	@echo "Starting Flask app with system Python..."
	python3 app.py

dev: ## Run the Flask app in development mode with auto-reload
	@if [ ! -d venv ]; then \
		echo "⚠️  Virtual environment not found. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	FLASK_ENV=development FLASK_DEBUG=1 $(VENV_PYTHON) app.py

clean: ## Clean generated files and cache
	rm -rf output/*.pdf
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true

clean-all: ## Clean everything including virtual environment
	rm -rf venv
	$(MAKE) clean

test: ## Run tests (placeholder for future tests)
	@echo "No tests defined yet"

check: ## Check code with linters
	@echo "Checking code..."
	@$(VENV_PYTHON) -m py_compile app.py problem_generator.py worksheet_generator.py 2>/dev/null || echo "Syntax errors found"

deploy: ## Show deployment instructions
	@echo "Deployment options:"
	@echo "  1. Render: See DEPLOYMENT.md for instructions"
	@echo "  2. Railway: See DEPLOYMENT.md for instructions"
	@echo "  3. Fly.io: See DEPLOYMENT.md for instructions"

requirements: ## Update requirements.txt from current environment
	@if [ ! -d venv ]; then \
		echo "⚠️  Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	$(VENV_PIP) freeze > requirements.txt

