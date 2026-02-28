# Complete Setup Guide

Follow these steps **exactly** to get your Kindle highlights syncing to your phone.

---

## Prerequisites

- GitHub account (free)
- Python 3.10+ installed on your Mac
- Amazon Kindle account with some highlights
- iPhone with Scriptable app (optional, for home screen widget)

---

## Step 1: Create a Secret GitHub Gist

1. Go to https://gist.github.com
2. Make sure you're logged in
3. **Filename:** `latest.json`
4. **Content:**
   ```json
   {"updated_at":"","items":[]}
   ```
5. Click the dropdown on "Create secret gist" and select **"Create secret gist"** (NOT public)
6. After creating, look at the URL in your browser:
   ```
   https://gist.github.com/YOUR_USERNAME/abc123def456...
   ```
7. **Copy the Gist ID** (the long string after your username): `abc123def456...`

8. **Get the Raw URL:**
   - Click on `latest.json` filename in the gist
   - Click the **"Raw"** button
   - You'll see a URL like:
     ```
     https://gist.githubusercontent.com/YOUR_USERNAME/GIST_ID/raw/COMMIT_HASH/latest.json
     ```
   - **Remove the commit hash** to get the "always latest" URL:
     ```
     https://gist.githubusercontent.com/YOUR_USERNAME/GIST_ID/raw/latest.json
     ```
   - Save this URL for later

---

## Step 2: Create a GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. **Note:** `kindle-highlights-gist`
4. **Expiration:** Choose your preference (90 days, 1 year, or no expiration)
5. **Scopes:** Check ONLY `gist` (nothing else needed)
6. Click **"Generate token"**
7. **COPY THE TOKEN NOW** - you won't see it again!
8. Save it somewhere temporarily (you'll add it to GitHub Secrets soon)

---

## Step 3: Push This Repo to GitHub

If you haven't already:

```bash
cd "/Users/marklanglois/Desktop/cursor projects/live kindle book updates"

# Initialize git
git init
git add .
git commit -m "Initial commit: Kindle highlights sync system"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/kindle-highlights-sync.git
git branch -M main
git push -u origin main
```

---

## Step 4: Generate auth.json Locally (One-Time)

This step logs you into Amazon and saves the session. Run this on your Mac:

```bash
cd "/Users/marklanglois/Desktop/cursor projects/live kindle book updates/scraper"

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Run interactive login (opens a browser window)
python -m app.main --login --region co.uk
```

> **For amazon.com users:** Use `--region com` instead of `--region co.uk`

**What happens:**
1. A browser window opens to Amazon Kindle Notebook
2. Log in with your Amazon credentials
3. Complete any 2FA/CAPTCHA if prompted
4. Wait until you see your Kindle library/highlights
5. Go back to the terminal and **press Enter**
6. The auth state is saved to `scraper/data/auth.json`

---

## Step 5: Base64 Encode auth.json

Still in the `scraper` directory with your virtual environment active:

```bash
# Option A: Using Python (recommended)
python3 << 'PY'
import base64, pathlib
p = pathlib.Path("data/auth.json")
b64 = base64.b64encode(p.read_bytes()).decode()
print(b64)
PY
```

Or:

```bash
# Option B: Using base64 command (macOS)
base64 -i data/auth.json | tr -d '\n'
```

**Copy the entire output** (it's one long string with no line breaks).

---

## Step 6: Add GitHub Secrets and Variables

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**

### Add these Secrets (click "New repository secret"):

| Secret Name | Value |
|-------------|-------|
| `AMAZON_AUTH_JSON_B64` | The base64 string from Step 5 |
| `GIST_ID` | The Gist ID from Step 1 (just the ID, not the full URL) |
| `GIST_PAT` | The GitHub token from Step 2 |

### Add this Variable (click "Variables" tab → "New repository variable"):

| Variable Name | Value |
|---------------|-------|
| `AMAZON_REGION` | `co.uk` or `com` (match what you used in Step 4) |

**Important:** The workflow uses `GIST_PAT` (not `GITHUB_TOKEN`) for the token.

---

## Step 7: Update the Viewer with Your Gist URL

Edit `viewer/app.js` and change line 7:

```javascript
// BEFORE:
const GIST_RAW_URL = 'YOUR_GIST_RAW_URL_HERE';

// AFTER (use your actual URL from Step 1):
const GIST_RAW_URL = 'https://gist.githubusercontent.com/YOUR_USERNAME/YOUR_GIST_ID/raw/latest.json';
```

Commit and push:

```bash
git add viewer/app.js
git commit -m "Configure Gist URL for viewer"
git push
```

---

## Step 8: Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
2. **Source:** Deploy from a branch
3. **Branch:** `main`
4. **Folder:** `/ (root)`
5. Click **Save**

Wait 1-2 minutes for deployment. Your viewer will be at:
```
https://YOUR_USERNAME.github.io/REPO_NAME/viewer/
```

(Note the `/viewer/` at the end!)

---

## Step 9: Test the GitHub Action

1. Go to your repo → **Actions**
2. Click **"Sync Kindle Highlights"** in the left sidebar
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait for it to complete (usually 1-2 minutes)
5. Check the logs for any errors

**If successful:**
- Your Gist will now have real highlight data
- Visit your GitHub Pages viewer URL to see them

---

## Step 10: Set Up iPhone Widget (Optional)

### Install Scriptable
Download from App Store: [Scriptable](https://apps.apple.com/app/scriptable/id1405459188)

### Create the Script
1. Open Scriptable
2. Tap **+** to create a new script
3. Copy the contents of `widget/scriptable_widget.js`
4. Paste into Scriptable
5. **Update the configuration at the top:**

```javascript
const GIST_RAW_URL = 'https://gist.githubusercontent.com/YOUR_USERNAME/YOUR_GIST_ID/raw/latest.json';

const VIEWER_URL = 'https://YOUR_USERNAME.github.io/REPO_NAME/viewer/';
```

6. Tap the script name at the top and rename to **"Kindle Highlights"**
7. Tap **Done**

### Add Widget to Home Screen
1. Long-press on your iPhone home screen
2. Tap **+** in the top left
3. Search for **Scriptable**
4. Choose **Medium** size (recommended)
5. Tap **Add Widget**
6. Long-press the new widget → **Edit Widget**
7. **Script:** Select "Kindle Highlights"
8. **When Interacting:** Run Script (or Open URL)
9. Tap outside to save

---

## Troubleshooting

### "Auth session expired" Error
Amazon sessions expire periodically. When this happens:
1. Run Step 4 again locally (`python -m app.main --login --region co.uk`)
2. Run Step 5 again to get new base64 string
3. Update the `AMAZON_AUTH_JSON_B64` secret in GitHub

### Workflow Fails Immediately
- Check that all 3 secrets are set correctly (no extra spaces)
- Verify `AMAZON_REGION` variable exists

### No Highlights Found
- Make sure you have highlights in your Kindle account (read.amazon.co.uk/notebook)
- Check the workflow logs for debug info
- Download the `latest-highlights` artifact from the workflow run

### Viewer Shows "Loading..." Forever
- Check browser console (F12) for errors
- Verify your `GIST_RAW_URL` in `app.js` is correct
- Test the raw URL directly in your browser - it should return JSON

### Widget Shows Configuration Error
- Double-check both URLs in the Scriptable script
- Make sure there are no typos or extra spaces

---

## How It All Works

```
Every 15 minutes:

┌─────────────────────┐
│   GitHub Actions    │
│   (runs scraper)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│  Amazon Kindle      │────▶│  GitHub Gist        │
│  Notebook (scrape)  │     │  (stores JSON)      │
└─────────────────────┘     └──────────┬──────────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  GitHub Pages       │     │  iPhone Widget      │     │  Any Browser        │
│  (mobile viewer)    │     │  (Scriptable)       │     │  (raw JSON API)     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

---

## Costs

**$0/month** - Everything uses free tiers:
- GitHub Actions: 2,000 free minutes/month (each run uses ~1 min)
- GitHub Gist: Free unlimited
- GitHub Pages: Free for public repos
- Scriptable: Free app

---

## Security Notes

- Use a **secret** Gist (not public) to keep your reading habits private
- The `GIST_PAT` token only has `gist` scope (minimal permissions)
- `auth.json` contains Amazon session cookies - never commit it to git
- The `.gitignore` already excludes sensitive files

---

## Refreshing Amazon Auth

Amazon sessions typically last weeks to months. When they expire:

```bash
cd scraper
source .venv/bin/activate
python -m app.main --login --region co.uk

# Then re-encode and update secret:
python3 << 'PY'
import base64, pathlib
p = pathlib.Path("data/auth.json")
print(base64.b64encode(p.read_bytes()).decode())
PY
```

Copy output → GitHub repo Settings → Secrets → Update `AMAZON_AUTH_JSON_B64`
