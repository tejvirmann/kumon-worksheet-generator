# Quick Start Guide

## Running Locally (3 Steps!)

### Step 1: Install Dependencies
```bash
make install
# OR manually: pip install -r requirements.txt
```

### Step 2: Set Up Environment
```bash
make setup
# This creates .env file - you'll need to edit it
```

### Step 3: Add Your OpenAI API Key
Edit the `.env` file and add:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### Step 4: Run!
```bash
make run
# OR for auto-reload: make dev
```

Visit: **http://localhost:5000**

## That's It! 🎉

The app is now running locally. You can:
- Select a Kumon level (B, H, K, etc.)
- Choose a topic
- Generate worksheets with AI-powered problems

## AI Model Used

- **Default Model:** GPT-4
- **Location:** Same model used locally and in deployment (configured via environment variable)

To change the model, add to `.env`:
```
OPENAI_MODEL=gpt-3.5-turbo
```

Available models:
- `gpt-4` - Best quality, most expensive
- `gpt-3.5-turbo` - Faster, cheaper, good quality
- `gpt-4-turbo` - Fast gpt-4 variant

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full deployment instructions to:
- Render (Recommended)
- Railway
- Fly.io
- Vercel
- Heroku

## Common Commands

```bash
make help     # See all commands
make run      # Run the app
make dev      # Run with auto-reload
make clean    # Clean generated files
make install  # Install dependencies
```

## Troubleshooting

**Error: OPENAI_API_KEY not set**
- Make sure you edited `.env` file with your actual API key

**Error: Module not found**
- Run `make install` to install dependencies

**Port already in use**
- Change port in `app.py` or set `PORT` environment variable

