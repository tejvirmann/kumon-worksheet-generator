# How to Run & Deploy

## Quick Answers

### How to Run Locally?
```bash
make install  # Install dependencies
make setup    # Create .env file
# Edit .env and add OPENAI_API_KEY=your-key-here
make run      # Start the app
```

Visit: **http://localhost:5000**

### What Model is Used?

- **Currently:** GPT-4 (set in `problem_generator.py`)
- **Local:** Uses model from `.env` file (defaults to `gpt-4`)
- **Deployment:** Same - uses environment variable `OPENAI_MODEL`

To change: Add `OPENAI_MODEL=gpt-3.5-turbo` to your `.env` file

### How to Deploy?

**This is a Flask web app** (Python), not a PyPI package. Deploy to:

1. **Render** - Easiest, free tier ✅ (Recommended)
2. **Railway** - Simple, $5/month credit
3. **Fly.io** - Global distribution, free tier
4. **Vercel** - Serverless (needs adaptation)
5. **Heroku** - Classic platform ($7/month)

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions for each platform.

## All Makefile Commands

```bash
make help       # Show all commands
make install    # Install Python dependencies
make setup      # Create .env file and directories
make run        # Run in production mode
make dev        # Run in development mode (auto-reload)
make clean      # Clean generated PDFs and cache
make check      # Check code syntax
make deploy     # Show deployment options
```

## Step-by-Step Local Setup

1. **Install Python 3.11+** (if not already installed)
   ```bash
   python3 --version
   ```

2. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd kumon-worksheet-generator
   ```

3. **Install dependencies**
   ```bash
   make install
   # OR: pip install -r requirements.txt
   ```

4. **Set up environment**
   ```bash
   make setup
   ```

5. **Get OpenAI API Key**
   - Go to https://platform.openai.com/api-keys
   - Create a new API key
   - Copy it

6. **Edit `.env` file**
   ```bash
   OPENAI_API_KEY=sk-your-actual-key-here
   OPENAI_MODEL=gpt-4  # Optional, defaults to gpt-4
   ```

7. **Run the app**
   ```bash
   make run
   ```

8. **Open browser**
   - Visit: http://localhost:5000
   - Select level and topic
   - Generate worksheets!

## Model Options

Available OpenAI models:

- `gpt-4` - Best quality, slower, more expensive (~$0.03/worksheet)
- `gpt-4-turbo` - Fast GPT-4 variant
- `gpt-3.5-turbo` - Faster, cheaper (~$0.002/worksheet), good quality

Change by setting in `.env`:
```
OPENAI_MODEL=gpt-3.5-turbo
```

## Deployment Platforms

### Render (Easiest - Recommended)

1. Push code to GitHub
2. Go to render.com
3. New → Web Service
4. Connect repo
5. Build: `pip install -r requirements.txt`
6. Start: `gunicorn app:app`
7. Add env var: `OPENAI_API_KEY`
8. Deploy!

**Free tier available**

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed steps.

### Railway

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

Add `OPENAI_API_KEY` in Railway dashboard.

### Fly.io

```bash
fly launch
fly secrets set OPENAI_API_KEY=your-key
fly deploy
```

See `fly.toml` for configuration.

### Vercel

**Note:** Vercel is serverless and has timeout limits. May need code changes.

```bash
npm install -g vercel
vercel
```

See `vercel.json` for configuration.

## Troubleshooting

**"Module not found" error**
- Run `make install` again

**"OPENAI_API_KEY not set"**
- Check `.env` file exists
- Make sure key is correct (starts with `sk-`)

**Port 5000 already in use**
- Set `PORT=5001` in `.env` or change in `app.py`

**PDF generation fails**
- Check `output/` directory exists and is writable

**Model errors**
- Verify your OpenAI account has access to the model
- Try `gpt-3.5-turbo` as fallback

## Production Checklist

Before deploying:

- [ ] Set `FLASK_ENV=production`
- [ ] Set a secure `SECRET_KEY`
- [ ] Set `OPENAI_API_KEY` as environment variable (not in code!)
- [ ] Test PDF generation works
- [ ] Check `output/` directory permissions
- [ ] Consider using `gpt-3.5-turbo` to reduce costs

## Need Help?

- See [QUICKSTART.md](QUICKSTART.md) for fastest setup
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guides
- Check Makefile: `make help`

