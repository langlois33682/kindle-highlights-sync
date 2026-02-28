# Kindle Highlights Scraper

Python Playwright-based scraper for Amazon Kindle Notebook highlights.

## Local Setup

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
cd scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Generate Auth State (Required First Time)

You must run this locally with a visible browser to log into Amazon:

```bash
# For amazon.com
python -m app.main --login --region com

# For amazon.co.uk
python -m app.main --login --region co.uk
```

This will:
1. Open a browser window
2. Navigate to Kindle Notebook
3. Wait for you to log in manually
4. Save the session to `data/auth.json`

**Important**: Complete any 2FA/CAPTCHA prompts in the browser window.

### Test Locally

After generating auth.json:

```bash
# Test scraping (no upload)
python -m app.main --no-upload --region com

# Check output
cat data/latest.json
```

### Base64 Encode for GitHub Secrets

```bash
# macOS/Linux
base64 -i data/auth.json | tr -d '\n'

# Copy the output and add it as a GitHub secret named AMAZON_AUTH_JSON_B64
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AMAZON_AUTH_JSON_B64` | Base64-encoded auth.json content | For CI |
| `AMAZON_REGION` | Amazon region: `com` or `co.uk` | No (default: com) |
| `GIST_ID` | GitHub Gist ID for uploading results | For upload |
| `GITHUB_TOKEN` | GitHub token with gist scope | For upload |

## Troubleshooting

### Auth Expired

If you see "Auth session expired" errors:
1. Delete `data/auth.json`
2. Run `--login` again locally
3. Re-encode and update the GitHub secret

### Selectors Not Working

Amazon's Kindle Notebook HTML structure may vary by region. The scraper tries multiple selectors, but if it fails:

**For amazon.com:**
- Book list: `.kp-notebook-library-each-book`
- Title: `h2`, `.kp-notebook-searchable`
- Highlights: `#highlight`, `.kp-notebook-highlight`

**For amazon.co.uk:**
- May use slightly different class names
- Check the debug screenshot saved on failure

### No Highlights Found

1. Ensure you have highlights in your Kindle account
2. Check that auth.json is valid (not expired)
3. Try running with `--login` to refresh authentication

## Output Format

`data/latest.json`:

```json
{
  "updated_at": "2026-02-28T12:34:56Z",
  "items": [
    {
      "book_title": "Book Title",
      "highlight_text": "The highlighted sentence...",
      "highlight_time": "2026-02-28T12:20:00Z",
      "fetched_at": "2026-02-28T12:34:56Z"
    }
  ]
}
```
