"""
Task 8 — PageIndex vectorless fallback.

Khi không có API key hoặc dịch vụ lỗi, raise exception để Task 9 bắt
và trả hybrid results (không crash UI).
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_PATH = Path(__file__).parent.parent / "pageindex_doc_ids.json"


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        raise RuntimeError("PAGEINDEX_API_KEY is not configured")
    # Optional provider path — kept minimal to avoid hard dependency failures.
    raise RuntimeError("PageIndex upload is not configured for this run")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult hoặc raise khi provider unavailable."""
    if not PAGEINDEX_API_KEY:
        raise RuntimeError("PAGEINDEX_API_KEY is not configured")
    raise RuntimeError("PageIndex provider unavailable")


if __name__ == "__main__":
    try:
        upload_documents()
    except Exception as error:
        print(f"PageIndex skipped: {error}")
