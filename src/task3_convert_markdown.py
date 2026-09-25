"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.
"""

import json
from pathlib import Path

from markitdown import MarkItDown

from .task1_collect_legal_docs import LEGAL_METADATA


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()
    for path in sorted(legal_dir.iterdir()):
        if path.suffix.lower() not in {".pdf", ".doc", ".docx"}:
            continue
        if path.name.startswith("."):
            continue
        result = converter.convert(str(path))
        text = (result.text_content or "").strip()
        if not text:
            print(f"Skip empty: {path.name}")
            continue
        meta = LEGAL_METADATA.get(path.name, {})
        header = (
            f"# {meta.get('title', path.stem)}\n\n"
            f"**Source:** {meta.get('url', path.name)}\n\n"
            f"**Source file:** {path.name}\n\n---\n\n"
        )
        (output_dir / f"{path.stem}.md").write_text(header + text, encoding="utf-8")
        print(f"Converted legal: {path.name}")


def convert_news_articles() -> None:
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(news_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        header = (
            f"# {data['title']}\n\n"
            f"**Source:** {data['url']}\n\n"
            f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
        )
        body = (data.get("content_markdown") or "").strip()
        (output_dir / f"{path.stem}.md").write_text(header + body, encoding="utf-8")
        print(f"Converted news: {path.name}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
