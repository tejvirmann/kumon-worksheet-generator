# Vercel Deployment Guide

## Quick Deploy to Vercel

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel
   ```

3. **Set Environment Variables** in Vercel dashboard:
   - `OPENROUTER_API_KEY` = your OpenRouter API key
   - `AI_PROVIDER` = `openrouter`
   - `OPENAI_MODEL` = `openai/gpt-4`
   - `FLASK_ENV` = `production`

## How It Works

The app uses Flask with Vercel's Python adapter (`@vercel/python`). The `vercel.json` file tells Vercel to:
- Use the Python runtime
- Route all requests to `app.py`
- Handle Flask routes automatically

## PDF Handling on Vercel

Vercel serverless functions have some limitations:
- File system is read-only (except `/tmp`)
- Files in `/tmp` are ephemeral

**Solution**: PDFs are returned as base64-encoded data in the JSON response, then:
- Embedded in the browser using a data URI
- Downloadable via blob URL

## File Storage

For persistent storage, consider:
- **Vercel Blob** (recommended) - Vercel's object storage
- **AWS S3** - External storage
- **Base64 in database** - Store PDFs as base64 strings

## Current Implementation

The app currently:
1. Generates PDF to `/tmp` directory
2. Reads PDF as base64
3. Returns base64 in JSON response
4. Browser displays PDF using data URI

This works for single-use PDFs but files are lost after function execution.

## Improvements for Production

1. **Add Vercel Blob storage**:
   ```python
   from vercel_blob import put
   
   # Upload PDF to blob storage
   blob = await put(filename, pdf_data, {
       'contentType': 'application/pdf',
       'access': 'public'
   })
   ```

2. **Use blob URL for embedding**:
   ```javascript
   pdfViewer.src = blob.url; // Direct URL to stored PDF
   ```

## Environment Variables

Required in Vercel dashboard:

```
OPENROUTER_API_KEY=sk-or-v1-...
AI_PROVIDER=openrouter
OPENAI_MODEL=openai/gpt-4
FLASK_ENV=production
```

## Testing Locally with Vercel

```bash
# Run with Vercel dev server
vercel dev
```

This simulates the Vercel environment locally.

