"""Playwright scraper for Amazon Kindle Notebook highlights."""

import re
from datetime import datetime
from typing import Optional
from playwright.sync_api import sync_playwright, Page, Browser

from .utils import get_auth_path, get_kindle_notebook_url, utc_now


def parse_highlight_time(time_str: str) -> Optional[str]:
    """Parse highlight time string to ISO format.
    
    Handles formats like:
    - "Monday 28 February 2026"
    - "February 28, 2026"
    - "28 Feb 2026"
    - Relative times like "Yesterday", "2 hours ago" (returns None)
    """
    if not time_str:
        return None
    
    time_str = time_str.strip()
    
    patterns = [
        (r"(\d{1,2})\s+(\w+)\s+(\d{4})", "%d %B %Y"),
        (r"(\w+)\s+(\d{1,2}),?\s+(\d{4})", "%B %d %Y"),
        (r"(\d{1,2})\s+(\w{3})\s+(\d{4})", "%d %b %Y"),
    ]
    
    for pattern, date_format in patterns:
        match = re.search(pattern, time_str)
        if match:
            try:
                date_str = " ".join(match.groups())
                dt = datetime.strptime(date_str, date_format)
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue
    
    return None


def scrape_highlights(region: str, headless: bool = True) -> list[dict]:
    """Scrape recent highlights from Kindle Notebook.
    
    Args:
        region: Amazon region ('com' or 'co.uk')
        headless: Run browser in headless mode
        
    Returns:
        List of highlight dictionaries with book_title, highlight_text, 
        highlight_time, and fetched_at.
    """
    auth_path = get_auth_path()
    notebook_url = get_kindle_notebook_url(region)
    
    if not auth_path.exists():
        raise FileNotFoundError(
            f"Auth state file not found at {auth_path}. "
            "Run the login script first to generate auth.json"
        )
    
    highlights = []
    fetched_at = utc_now()
    
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=str(auth_path))
        page: Page = context.new_page()
        
        print(f"Navigating to {notebook_url}...")
        page.goto(notebook_url, wait_until="networkidle", timeout=60000)
        
        page.wait_for_timeout(3000)
        
        if "signin" in page.url.lower() or "ap/signin" in page.url:
            browser.close()
            raise RuntimeError(
                "Auth session expired. Please regenerate auth.json by running "
                "the login script locally."
            )
        
        print("Loading Kindle Notebook page...")
        
        try:
            page.wait_for_selector(
                "#kp-notebook-library, .kp-notebook-library, [id*='notebook']",
                timeout=30000
            )
        except Exception:
            print("Warning: Could not find notebook library selector, continuing anyway...")
        
        book_selectors = [
            ".kp-notebook-library-each-book",
            "[id^='library-section'] .a-row",
            ".library-book",
            "div[data-asin]",
        ]
        
        books = []
        for selector in book_selectors:
            books = page.query_selector_all(selector)
            if books:
                print(f"Found {len(books)} books using selector: {selector}")
                break
        
        if not books:
            print("No books found with standard selectors, trying alternative approach...")
            page.screenshot(path="debug_screenshot.png")
            
            all_links = page.query_selector_all("a[href*='notebook']")
            print(f"Found {len(all_links)} notebook links")
        
        for i, book_el in enumerate(books[:10]):
            try:
                title_selectors = [
                    "h2",
                    ".kp-notebook-searchable",
                    ".book-title",
                    "span[id*='title']",
                    "a",
                ]
                
                book_title = None
                for sel in title_selectors:
                    title_el = book_el.query_selector(sel)
                    if title_el:
                        book_title = title_el.inner_text().strip()
                        if book_title:
                            break
                
                if not book_title:
                    continue
                
                print(f"Processing book: {book_title[:50]}...")
                
                try:
                    book_el.click()
                    page.wait_for_timeout(2000)
                except Exception as e:
                    print(f"Could not click book: {e}")
                    continue
                
                highlight_selectors = [
                    "#highlight",
                    ".kp-notebook-highlight",
                    "[id*='highlight']",
                    ".highlight-text",
                    ".a-size-base-plus",
                ]
                
                highlight_elements = []
                for sel in highlight_selectors:
                    highlight_elements = page.query_selector_all(sel)
                    if highlight_elements:
                        break
                
                for hl_el in highlight_elements[:5]:
                    highlight_text = hl_el.inner_text().strip()
                    
                    if not highlight_text or len(highlight_text) < 10:
                        continue
                    
                    time_selectors = [
                        "#annotationHighlightHeader",
                        ".kp-notebook-metadata",
                        "[id*='highlight'] + *",
                        ".a-color-secondary",
                    ]
                    
                    highlight_time = None
                    for sel in time_selectors:
                        time_el = page.query_selector(sel)
                        if time_el:
                            time_str = time_el.inner_text()
                            highlight_time = parse_highlight_time(time_str)
                            if highlight_time:
                                break
                    
                    highlights.append({
                        "book_title": book_title,
                        "highlight_text": highlight_text,
                        "highlight_time": highlight_time,
                        "fetched_at": fetched_at,
                    })
                    
                    break
                    
            except Exception as e:
                print(f"Error processing book {i}: {e}")
                continue
        
        browser.close()
    
    print(f"Scraped {len(highlights)} highlights total")
    return highlights


def login_and_save_auth(region: str) -> None:
    """Interactive login to Amazon and save auth state.
    
    This should be run locally with headful browser to log in manually.
    """
    auth_path = get_auth_path()
    notebook_url = get_kindle_notebook_url(region)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Opening {notebook_url}...")
        print("Please log in manually in the browser window.")
        print("After successful login and seeing your highlights, press Enter here.")
        
        page.goto(notebook_url)
        
        input("Press Enter after you've logged in successfully...")
        
        context.storage_state(path=str(auth_path))
        print(f"Auth state saved to {auth_path}")
        
        browser.close()
    
    print("\nTo use this in GitHub Actions, base64 encode the file:")
    print(f"  base64 -i {auth_path} | tr -d '\\n'")
    print("\nThen add the output as a GitHub secret named AMAZON_AUTH_JSON_B64")
