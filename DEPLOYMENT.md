# Deployment Guide

## AI Model Configuration

**Currently using:** GPT-4 (configured in `problem_generator.py`)

- **Local Development:** Uses GPT-4 (or whatever is set in `.env` as `OPENAI_MODEL`)
- **Production/Deployment:** Uses GPT-4 (same model, controlled by environment variable)

To change the model, set the `OPENAI_MODEL` environment variable:
- `gpt-4` (default, more accurate, more expensive)
- `gpt-3.5-turbo` (faster, cheaper)
- `gpt-4-turbo` (faster than gpt-4, similar quality)

## Running Locally

### Quick Start

```bash
# 1. Install dependencies
make install

# 2. Set up environment
make setup

# 3. Edit .env file and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here

# 4. Run the app
make run
# OR for development mode with auto-reload
make dev
```

The app will be available at `http://localhost:5000`

### Manual Steps

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key-here"
python app.py
```

## Deployment Options

This Flask app can be deployed to several platforms. **Note:** PyPI is for publishing Python packages, not for deploying web applications. For web deployment, use one of these platforms:

### Option 1: Render (Recommended - Easy Setup)

1. **Create account** at [render.com](https://render.com)

2. **Create a new Web Service:**
   - Connect your GitHub repository
   - Select "Web Service"
   - Choose the repository

3. **Configure settings:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
   - **Python Version:** 3.11

4. **Add Environment Variables:**
   - `OPENAI_API_KEY` = your OpenAI API key
   - `OPENAI_MODEL` = `gpt-4` (optional, defaults to gpt-4)
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = (generate a random secret key)

5. **Deploy!** Render will automatically deploy on every push to main.

**Free tier available** (with limitations on sleep time)

---

### Option 2: Railway (Recommended - Simple)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Add environment variables in Railway dashboard:**
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL` (optional)
   - `PORT` (Railway sets this automatically)

4. **Your app will be live!** Railway provides a URL automatically.

**Free tier with $5/month credit**

---

### Option 3: Fly.io (Good for Global Distribution)

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create fly.toml** (see fly.toml.example in repo)

3. **Deploy:**
   ```bash
   fly launch
   fly secrets set OPENAI_API_KEY=your-key-here
   fly secrets set OPENAI_MODEL=gpt-4
   fly deploy
   ```

**Free tier with shared-cpu-1x VMs**

---

### Option 4: Vercel (Serverless - Requires Adaptation)

Vercel is primarily for serverless functions. To deploy Flask on Vercel, you need to adapt it:

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Create `vercel.json`** (see vercel.json.example in repo)

3. **Deploy:**
   ```bash
   vercel
   ```

**Note:** Vercel has timeout limits (10s on free tier), which might be problematic for PDF generation. Consider using Render or Railway instead.

---

### Option 5: Heroku (Classic Platform)

1. **Install Heroku CLI:**
   ```bash
   brew install heroku/brew/heroku  # macOS
   ```

2. **Login and create app:**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set OPENAI_API_KEY=your-key-here
   heroku config:set OPENAI_MODEL=gpt-4
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

**Free tier discontinued, starts at $7/month**

---

## Environment Variables

Required for all deployments:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | (required) |
| `OPENAI_MODEL` | Model to use (`gpt-4`, `gpt-3.5-turbo`, etc.) | `gpt-4` |
| `FLASK_ENV` | Environment (`development` or `production`) | `development` |
| `SECRET_KEY` | Flask secret key for sessions | (auto-generated) |
| `PORT` | Port to run on | `5000` |

## Makefile Commands

```bash
make help       # Show all available commands
make install    # Install dependencies
make setup      # Create directories and .env file
make run        # Run in production mode
make dev        # Run in development mode
make clean      # Clean generated files
make check      # Check code syntax
make deploy     # Show deployment instructions
```

## Troubleshooting

### OpenAI API Key Not Working
- Make sure `OPENAI_API_KEY` is set correctly in your environment
- Check that you have credits in your OpenAI account
- Verify the API key has the right permissions

### PDF Generation Fails
- Ensure `output/` directory exists and is writable
- Check file permissions on the server
- Verify ReportLab is installed correctly

### Model Errors
- If you get "model not found" errors, check your OpenAI account has access to the model
- Try `gpt-3.5-turbo` as a fallback (cheaper and more available)

## Cost Considerations

- **GPT-4:** ~$0.03 per worksheet (depending on problem count)
- **GPT-3.5-turbo:** ~$0.002 per worksheet (much cheaper)
- **Hosting:** Most platforms have free tiers for small projects

Consider using `gpt-3.5-turbo` for production to reduce costs while maintaining good quality.

