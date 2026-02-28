"""Main entrypoint for the Kindle highlights scraper."""

import os
import sys
import argparse

from .utils import (
    get_amazon_region,
    get_auth_path,
    decode_base64_to_file,
)
from .scraper import scrape_highlights, login_and_save_auth
from .build import merge_with_existing, save_output
from .gist import upload_to_gist


def setup_auth_from_env() -> bool:
    """Set up auth.json from base64 environment variable.
    
    Returns:
        True if auth was set up from env, False otherwise
    """
    b64_auth = os.environ.get("AMAZON_AUTH_JSON_B64")
    
    if b64_auth:
        auth_path = get_auth_path()
        decode_base64_to_file(b64_auth, auth_path)
        return True
    
    return False


def run_scraper(region: str, upload: bool = True) -> None:
    """Run the full scraper pipeline.
    
    Args:
        region: Amazon region ('com' or 'co.uk')
        upload: Whether to upload to Gist
    """
    print(f"Starting Kindle highlights scraper for amazon.{region}")
    print("-" * 50)
    
    setup_auth_from_env()
    
    auth_path = get_auth_path()
    if not auth_path.exists():
        print(f"Error: Auth file not found at {auth_path}")
        print("Run with --login flag to generate auth.json locally")
        sys.exit(1)
    
    print("Scraping highlights...")
    highlights = scrape_highlights(region, headless=True)
    
    if not highlights:
        print("Warning: No highlights scraped")
    
    print(f"Scraped {len(highlights)} highlights")
    
    merged = merge_with_existing(highlights)
    print(f"Total after merge/dedupe: {len(merged)} highlights")
    
    output = save_output(merged)
    print(f"Saved {len(output['items'])} items to latest.json")
    
    if upload:
        gist_id = os.environ.get("GIST_ID")
        github_token = os.environ.get("GITHUB_TOKEN")
        
        if gist_id and github_token:
            print("Uploading to Gist...")
            try:
                raw_url = upload_to_gist()
                print(f"Upload complete: {raw_url}")
            except Exception as e:
                print(f"Error uploading to Gist: {e}")
                sys.exit(1)
        else:
            print("Skipping Gist upload (GIST_ID or GITHUB_TOKEN not set)")
    
    print("-" * 50)
    print("Done!")


def run_login(region: str) -> None:
    """Run interactive login to generate auth.json.
    
    Args:
        region: Amazon region ('com' or 'co.uk')
    """
    print(f"Starting interactive login for amazon.{region}")
    print("-" * 50)
    login_and_save_auth(region)


def main() -> None:
    """Main entrypoint."""
    parser = argparse.ArgumentParser(
        description="Kindle Highlights Scraper"
    )
    
    parser.add_argument(
        "--login",
        action="store_true",
        help="Run interactive login to generate auth.json"
    )
    
    parser.add_argument(
        "--region",
        type=str,
        default=None,
        help="Amazon region (com or co.uk). Defaults to AMAZON_REGION env var or 'com'"
    )
    
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip uploading to Gist"
    )
    
    args = parser.parse_args()
    
    region = args.region or get_amazon_region()
    
    if args.login:
        run_login(region)
    else:
        run_scraper(region, upload=not args.no_upload)


if __name__ == "__main__":
    main()
