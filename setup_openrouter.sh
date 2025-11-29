#!/bin/bash
# Quick setup script for OpenRouter

echo "Setting up .env file for OpenRouter..."

cat > .env << 'EOF'
# AI Provider Configuration
AI_PROVIDER=openrouter

# OpenRouter.io API Key
OPENROUTER_API_KEY=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

# Model to use (OpenRouter format)
# Available models: openai/gpt-4, openai/gpt-3.5-turbo, anthropic/claude-3-opus, etc.
OPENAI_MODEL=openai/gpt-4

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
PORT=5000

# Output Directory
OUTPUT_DIR=output
EOF

echo "✅ .env file created with OpenRouter configuration!"
echo "You can now run: make run"

