"""Build and deduplicate highlights data."""

from typing import Optional
from .utils import utc_now, get_latest_path, load_json, save_json


def deduplicate_highlights(highlights: list[dict]) -> list[dict]:
    """Keep only the most recent highlight per book.
    
    Args:
        highlights: List of highlight dictionaries
        
    Returns:
        Deduplicated list with one highlight per book (most recent)
    """
    book_highlights: dict[str, dict] = {}
    
    for hl in highlights:
        title = hl.get("book_title", "")
        if not title:
            continue
        
        existing = book_highlights.get(title)
        
        if existing is None:
            book_highlights[title] = hl
        else:
            new_time = hl.get("highlight_time") or hl.get("fetched_at")
            existing_time = existing.get("highlight_time") or existing.get("fetched_at")
            
            if new_time and existing_time:
                if new_time > existing_time:
                    book_highlights[title] = hl
            elif new_time:
                book_highlights[title] = hl
    
    return list(book_highlights.values())


def sort_by_recency(highlights: list[dict]) -> list[dict]:
    """Sort highlights by most recent first.
    
    Uses highlight_time if available, falls back to fetched_at.
    """
    def get_sort_key(hl: dict) -> str:
        return hl.get("highlight_time") or hl.get("fetched_at") or ""
    
    return sorted(highlights, key=get_sort_key, reverse=True)


def build_output(highlights: list[dict]) -> dict:
    """Build the final output JSON structure.
    
    Args:
        highlights: List of highlight dictionaries
        
    Returns:
        Output dictionary with updated_at and items
    """
    deduped = deduplicate_highlights(highlights)
    sorted_highlights = sort_by_recency(deduped)
    
    return {
        "updated_at": utc_now(),
        "items": sorted_highlights,
    }


def merge_with_existing(new_highlights: list[dict], existing_path: Optional[str] = None) -> list[dict]:
    """Merge new highlights with existing ones from file.
    
    Args:
        new_highlights: Newly scraped highlights
        existing_path: Path to existing latest.json (optional)
        
    Returns:
        Merged and deduplicated highlights
    """
    existing_highlights = []
    
    path = existing_path or get_latest_path()
    
    try:
        if hasattr(path, 'exists') and path.exists():
            data = load_json(path)
            existing_highlights = data.get("items", [])
            print(f"Loaded {len(existing_highlights)} existing highlights")
    except Exception as e:
        print(f"Could not load existing highlights: {e}")
    
    all_highlights = new_highlights + existing_highlights
    return deduplicate_highlights(all_highlights)


def save_output(highlights: list[dict], path: Optional[str] = None) -> dict:
    """Build and save the output JSON.
    
    Args:
        highlights: List of highlight dictionaries
        path: Output path (optional, defaults to data/latest.json)
        
    Returns:
        The output dictionary that was saved
    """
    output = build_output(highlights)
    output_path = path or get_latest_path()
    save_json(output, output_path)
    return output
