# OpenRouter.io Setup

This project now supports **OpenRouter.io**, which provides access to multiple AI models through a unified API.

## Your OpenRouter API Key

Your API key has been configured! The `.env` file should contain:

```
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=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
OPENAI_MODEL=openai/gpt-4
```

## Quick Setup

If the `.env` file doesn't exist yet, create it:

```bash
# Copy the template
cp env.template .env

# Edit .env and set:
# AI_PROVIDER=openrouter
# OPENROUTER_API_KEY=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
# OPENAI_MODEL=openai/gpt-4
```

Or use the setup script:
```bash
chmod +x setup_openrouter.sh
./setup_openrouter.sh
```

## Available Models on OpenRouter

You can use any model available on OpenRouter by changing `OPENAI_MODEL` in your `.env`:

### OpenAI Models
- `openai/gpt-4` - Best quality (default)
- `openai/gpt-4-turbo` - Faster GPT-4
- `openai/gpt-3.5-turbo` - Faster, cheaper

### Anthropic Models
- `anthropic/claude-3-opus` - Most capable
- `anthropic/claude-3-sonnet` - Balanced
- `anthropic/claude-3-haiku` - Fastest

### Other Models
- `google/gemini-pro` - Google's model
- `meta-llama/llama-3-70b-instruct` - Meta's Llama

See all available models: https://openrouter.ai/models

## Switching Between Providers

### Use OpenRouter (Current)
```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your-key-here
OPENAI_MODEL=openai/gpt-4
```

### Use OpenAI Direct
```env
AI_PROVIDER=openai
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4
```

## Cost Comparison

OpenRouter often has better pricing than direct OpenAI:

- **GPT-4 via OpenRouter:** Usually cheaper
- **GPT-3.5-turbo:** Very affordable
- **Claude models:** Available through OpenRouter

Check current pricing: https://openrouter.ai/models

## Advantages of OpenRouter

1. **Multiple Models:** Access to OpenAI, Anthropic, Google, Meta, and more
2. **Better Pricing:** Often cheaper than direct APIs
3. **Fallback Options:** If one model is down, try another
4. **Unified API:** Same code works with all models

## Testing Your Setup

```bash
# Install dependencies
make install

# Run the app
make run

# Visit http://localhost:5000
# Try generating a worksheet - it should work!
```

## Troubleshooting

**"API key not set" error:**
- Check your `.env` file exists
- Verify `OPENROUTER_API_KEY` is set correctly
- Make sure the key starts with `sk-or-v1-`

**Model not found:**
- Check the model name format: `provider/model-name`
- Visit https://openrouter.ai/models to see available models
- Try `openai/gpt-3.5-turbo` as a test

**Rate limits:**
- OpenRouter has rate limits based on your account tier
- Free tier has generous limits for testing
- Upgrade if you need more requests

## Security Note

⚠️ **Important:** The `.env` file is in `.gitignore` and won't be committed to git. This protects your API key. Never commit API keys to version control!

## Need Help?

- OpenRouter Docs: https://openrouter.ai/docs
- OpenRouter Dashboard: https://openrouter.ai/keys (check usage)
- See [QUICKSTART.md](QUICKSTART.md) for general setup

