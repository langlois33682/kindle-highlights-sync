# Kindle Highlights Sync

Automatically sync your latest Kindle highlights to your phone using GitHub Actions, GitHub Gist, and GitHub Pages — completely free!

> **📖 First time setup?** See **[SETUP.md](SETUP.md)** for complete step-by-step instructions.

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Amazon Kindle  │────▶│  GitHub Actions  │────▶│  GitHub Gist    │
│    Notebook     │     │   (scheduled)    │     │  (latest.json)  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                        ┌─────────────────────────────────┼─────────────────────────────────┐
                        │                                 │                                 │
                        ▼                                 ▼                                 ▼
               ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
               │  GitHub Pages   │              │    Scriptable   │              │   Any Device    │
               │     Viewer      │              │  iPhone Widget  │              │   (JSON API)    │
               └─────────────────┘              └─────────────────┘              └─────────────────┘
```

1. **GitHub Actions** runs every 15 minutes (or on-demand)
2. **Playwright scraper** logs into Amazon Kindle Notebook with your saved session
3. **Extracts highlights** and deduplicates them (one per book)
4. **Uploads to a secret Gist** as `latest.json`
5. **GitHub Pages** hosts a mobile-friendly viewer
6. **Scriptable widget** displays the latest highlight on your iPhone home screen

## Quick Start

### Prerequisites

- GitHub account (free)
- Amazon Kindle account with highlights
- iPhone with [Scriptable app](https://apps.apple.com/app/scriptable/id1405459188) (optional, for widget)

### Step 1: Fork or Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/kindle-highlights-sync.git
cd kindle-highlights-sync
```

### Step 2: Create a Secret GitHub Gist

1. Go to https://gist.github.com
2. Create a **Secret** gist (not public)
3. Filename: `latest.json`
4. Content: `{}`
5. Click "Create secret gist"
6. Copy the **Gist ID** from the URL: `https://gist.github.com/USERNAME/GIST_ID_HERE`

### Step 3: Create a GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `kindle-highlights-gist`
4. Scopes: Check only `gist`
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### Step 4: Generate Amazon Auth State (Local)

```bash
cd scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run interactive login
python -m app.main --login --region com
# For UK: python -m app.main --login --region co.uk
```

A browser window will open. Log into Amazon, complete any 2FA, and wait until you see your Kindle Notebook. Then press Enter in the terminal.

### Step 5: Base64 Encode Auth State

```bash
# macOS/Linux
base64 -i data/auth.json | tr -d '\n' | pbcopy
# The encoded string is now in your clipboard

# Linux (without pbcopy)
base64 -w 0 data/auth.json
# Copy the output manually
```

### Step 6: Add GitHub Secrets

Go to your repo → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `AMAZON_AUTH_JSON_B64` | The base64 string from Step 5 |
| `GIST_ID` | The Gist ID from Step 2 |
| `GIST_PAT` | The GitHub token from Step 3 |

Add this variable (Settings → Secrets and variables → Actions → Variables):

| Variable Name | Value |
|---------------|-------|
| `AMAZON_REGION` | `com` or `co.uk` |

### Step 7: Enable GitHub Pages

1. Go to repo → Settings → Pages
2. Source: "Deploy from a branch"
3. Branch: `main` (or `master`)
4. Folder: `/viewer`
5. Click Save

Your viewer will be at: `https://YOUR_USERNAME.github.io/REPO_NAME/`

### Step 8: Configure the Viewer

Edit `viewer/app.js` and update:

```javascript
const GIST_RAW_URL = 'https://gist.githubusercontent.com/YOUR_USERNAME/GIST_ID/raw/latest.json';
```

Get your Gist raw URL:
1. Open your Gist
2. Click "Raw" on the `latest.json` file
3. Copy the URL (remove the commit hash for latest version):
   - Before: `https://gist.githubusercontent.com/.../abc123/latest.json`
   - After: `https://gist.githubusercontent.com/USERNAME/GIST_ID/raw/latest.json`

### Step 9: Run the Workflow

1. Go to repo → Actions → "Sync Kindle Highlights"
2. Click "Run workflow" → "Run workflow"
3. Wait for it to complete (check logs for any errors)

### Step 10: Set Up iPhone Widget (Optional)

1. Install [Scriptable](https://apps.apple.com/app/scriptable/id1405459188)
2. Copy the contents of `widget/scriptable_widget.js`
3. Open Scriptable → + → Paste the code
4. Update the configuration at the top:
   ```javascript
   const GIST_RAW_URL = 'https://gist.githubusercontent.com/...';
   const VIEWER_URL = 'https://YOUR_USERNAME.github.io/REPO_NAME/';
   ```
5. Save the script (name it "Kindle Highlights")
6. Add a Scriptable widget to your home screen
7. Long-press → Edit Widget → Script: "Kindle Highlights"

## Troubleshooting

### Auth Session Expired

Amazon sessions expire after some time. When you see authentication errors:

1. Run `--login` locally again
2. Re-encode the auth.json
3. Update the `AMAZON_AUTH_JSON_B64` secret

### No Highlights Found

- Make sure you have highlights in your Kindle account
- Check the debug screenshot artifact in Actions for clues
- Try a different `AMAZON_REGION` value

### Workflow Fails

Check the Actions logs for specific errors:
- "Auth state file not found" → Check `AMAZON_AUTH_JSON_B64` secret
- "Auth session expired" → Regenerate auth.json locally
- "Failed to upload to Gist" → Check `GIST_ID` and `GIST_PAT` secrets

### Widget Shows Error

- Verify the `GIST_RAW_URL` is correct and accessible
- Test the URL in Safari to confirm it returns JSON
- Make sure the Gist is not empty

## Project Structure

```
├── .github/
│   └── workflows/
│       └── sync.yml          # GitHub Actions workflow
├── scraper/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # CLI entrypoint
│   │   ├── scraper.py        # Playwright scraper
│   │   ├── build.py          # Data processing
│   │   ├── gist.py           # Gist upload
│   │   └── utils.py          # Utilities
│   ├── data/                  # Local data (gitignored)
│   ├── requirements.txt
│   └── README.md
├── viewer/
│   ├── index.html            # Mobile-friendly viewer
│   ├── styles.css
│   └── app.js
├── widget/
│   └── scriptable_widget.js  # iPhone widget
├── .gitignore
└── README.md
```

## Output Format

`latest.json`:

```json
{
  "updated_at": "2026-02-28T12:34:56Z",
  "items": [
    {
      "book_title": "Atomic Habits",
      "highlight_text": "You do not rise to the level of your goals. You fall to the level of your systems.",
      "highlight_time": "2026-02-28T10:15:00Z",
      "fetched_at": "2026-02-28T12:34:56Z"
    }
  ]
}
```

## Costs

**$0/month** - Everything uses free tiers:
- GitHub Actions: 2,000 minutes/month free (this uses ~1 min per run)
- GitHub Gist: Free
- GitHub Pages: Free for public repos
- Scriptable: Free app

## Security Notes

- Use a **secret** Gist, not public
- The `GIST_PAT` token only needs `gist` scope
- Auth sessions are stored encrypted in GitHub Secrets
- Never commit `auth.json` to the repo

## License

MIT
