"""GitHub Gist upload functionality."""

import os
import json
import urllib.request
import urllib.error
from typing import Optional

from .utils import get_latest_path, load_json


def upload_to_gist(
    gist_id: Optional[str] = None,
    github_token: Optional[str] = None,
    data: Optional[dict] = None,
    filename: str = "latest.json"
) -> str:
    """Upload data to a GitHub Gist.
    
    Args:
        gist_id: The Gist ID (from env GIST_ID if not provided)
        github_token: GitHub personal access token (from env GITHUB_TOKEN if not provided)
        data: Data to upload (loads from latest.json if not provided)
        filename: Filename in the gist
        
    Returns:
        The raw URL of the uploaded file
        
    Raises:
        ValueError: If required parameters are missing
        RuntimeError: If upload fails
    """
    gist_id = gist_id or os.environ.get("GIST_ID")
    github_token = github_token or os.environ.get("GITHUB_TOKEN")
    
    if not gist_id:
        raise ValueError(
            "Gist ID is required. Set GIST_ID environment variable or pass gist_id parameter."
        )
    
    if not github_token:
        raise ValueError(
            "GitHub token is required. Set GITHUB_TOKEN environment variable or pass github_token parameter."
        )
    
    if data is None:
        latest_path = get_latest_path()
        if not latest_path.exists():
            raise FileNotFoundError(f"No data file found at {latest_path}")
        data = load_json(latest_path)
    
    content = json.dumps(data, indent=2, ensure_ascii=False)
    
    payload = {
        "files": {
            filename: {
                "content": content
            }
        }
    }
    
    url = f"https://api.github.com/gists/{gist_id}"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    
    request_data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=request_data,
        headers=headers,
        method="PATCH"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            
            files = response_data.get("files", {})
            file_info = files.get(filename, {})
            raw_url = file_info.get("raw_url", "")
            
            print(f"Successfully uploaded to Gist: {gist_id}")
            print(f"Raw URL: {raw_url}")
            
            return raw_url
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(
            f"Failed to upload to Gist: {e.code} {e.reason}\n{error_body}"
        )
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error uploading to Gist: {e.reason}")


def get_gist_raw_url(gist_id: str, filename: str = "latest.json") -> str:
    """Get the raw URL for a file in a Gist.
    
    Note: This returns the base URL format. The actual URL with cache-busting
    hash is returned by the upload function.
    
    Args:
        gist_id: The Gist ID
        filename: The filename in the gist
        
    Returns:
        The raw URL pattern
    """
    return f"https://gist.githubusercontent.com/raw/{gist_id}/{filename}"
