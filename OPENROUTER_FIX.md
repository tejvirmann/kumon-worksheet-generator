# OpenRouter API 401 Error Fix

## The Problem

You're getting a `401 - User not found` error from OpenRouter. This means:

1. ❌ **API key is invalid or expired**
2. ❌ **Account not verified**  
3. ❌ **No credits in account**
4. ❌ **API key format is wrong**

## Quick Fixes

### 1. Verify Your API Key

1. Go to: https://openrouter.ai/keys
2. Check if your API key is still valid
3. Copy a fresh API key if needed

### 2. Update .env File

Edit your `.env` file:
```bash
# Make sure these are set correctly:
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-YOUR-ACTUAL-KEY-HERE
OPENAI_MODEL=openai/gpt-4
```

### 3. Verify Your Account

1. Go to: https://openrouter.ai/
2. Sign in to your account
3. Check that your account is verified
4. Make sure you have credits available

### 4. Test Your API Key

You can test if your API key works:
```bash
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer sk-or-v1-YOUR-KEY-HERE"
```

If this returns model listings, your key works!

## Fallback Mode

**Good news:** The app will automatically use a fallback problem generator if OpenRouter fails, so worksheets will still generate (just without AI-generated problems).

## After Fixing

1. **Update your `.env` file** with the correct API key
2. **Restart your Flask app:**
   ```bash
   make run
   ```
3. **Try generating a worksheet again**

## Alternative: Use OpenAI Direct

If OpenRouter keeps having issues, you can switch to OpenAI:

In `.env`:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4
```

Then restart the app.

