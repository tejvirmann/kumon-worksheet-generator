.PHONY: help install run dev clean test setup deploy

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

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
	python app.py

dev: ## Run the Flask app in development mode with auto-reload
	FLASK_ENV=development FLASK_DEBUG=1 python app.py

clean: ## Clean generated files and cache
	rm -rf output/*.pdf
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true

test: ## Run tests (placeholder for future tests)
	@echo "No tests defined yet"

check: ## Check code with linters
	@echo "Checking code..."
	@python -m py_compile app.py problem_generator.py worksheet_generator.py 2>/dev/null || echo "Syntax errors found"

deploy: ## Show deployment instructions
	@echo "Deployment options:"
	@echo "  1. Render: See DEPLOYMENT.md for instructions"
	@echo "  2. Railway: See DEPLOYMENT.md for instructions"
	@echo "  3. Fly.io: See DEPLOYMENT.md for instructions"

requirements: ## Update requirements.txt from current environment
	pip freeze > requirements.txt

