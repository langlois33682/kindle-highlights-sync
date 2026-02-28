"""Utility functions for the Kindle scraper."""

import os
import json
import base64
from datetime import datetime, timezone
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory (scraper folder)."""
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """Get the data directory path."""
    data_dir = get_project_root() / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def get_auth_path() -> Path:
    """Get the auth.json path."""
    return get_data_dir() / "auth.json"


def get_latest_path() -> Path:
    """Get the latest.json output path."""
    return get_data_dir() / "latest.json"


def utc_now() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def decode_base64_to_file(b64_string: str, output_path: Path) -> None:
    """Decode a base64 string and write to file."""
    decoded = base64.b64decode(b64_string)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(decoded)
    print(f"Decoded auth state to {output_path}")


def load_json(path: Path) -> dict:
    """Load JSON from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, path: Path) -> None:
    """Save data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON to {path}")


def get_amazon_region() -> str:
    """Get Amazon region from environment variable."""
    region = os.environ.get("AMAZON_REGION", "com")
    if region not in ("com", "co.uk"):
        print(f"Warning: Unknown region '{region}', defaulting to 'com'")
        return "com"
    return region


def get_kindle_notebook_url(region: str) -> str:
    """Get the Kindle Notebook URL for the given region."""
    return f"https://read.amazon.{region}/notebook"
