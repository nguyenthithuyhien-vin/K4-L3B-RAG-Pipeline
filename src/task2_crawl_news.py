"""
Task 2 — Crawl bài viết/thông báo tuyển sinh ĐHBK Hà Nội.
"""

import asyncio
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://ts.hust.edu.vn/tin-tuc/dhbk-ha-noi-cong-bo-phuong-an-tuyen-sinh-dai-hoc-chinh-quy-nam-2025",
    "https://hust.edu.vn/vi/news/hoat-dong-chung/dai-hoc-bach-khoa-ha-noi-cong-bo-diem-chuan-xet-tuyen-dai-hoc-nam-2025-655575.html",
    "https://hust.edu.vn/vi/news/tuyen-sinh-dao-tao-cong-tac-sinh-vien/do-lech-giua-cac-to-hop-xet-tuyen-bang-quy-doi-diem-chuan-va-du-bao-muc-diem-trung-tuyen-vao-cac-nganh-cua-dai-hoc-bach-khoa-ha-noi-nam-2025-655521.html",
    "https://smse.hust.edu.vn/vi/tuyen-sinh/tuyen-sinh-truong-vat-lieu/diem-chuan-dai-hoc-bach-khoa-ha-noi-2025-14.html",
    "https://research.hust.edu.vn/seee/tin-tuc/thong-tin-tuyen-sinh-dai-hoc-chinh-quy-nam-2025-post2K1kBGw0oZixw8nZrRm2",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip = False
        self.parts: list[str] = []
        self.title = ""

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "nav", "footer", "header", "noscript"}:
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "footer", "header", "noscript"}:
            self._skip = False
        if tag in {"p", "div", "br", "li", "h1", "h2", "h3", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        text = data.strip()
        if text:
            self.parts.append(text + " ")


def _html_to_markdown(html: str) -> tuple[str, str]:
    parser = _TextExtractor()
    parser.feed(html)
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = ""
    if title_match:
        title = re.sub(r"\s+", " ", title_match.group(1)).strip()
    content = re.sub(r"[ \t]+", " ", "".join(parser.parts))
    content = re.sub(r"\n{3,}", "\n\n", content).strip()
    return title, content


def _title_from_markdown(content: str) -> str | None:
    """Fallback for pages without <title>: first heading, or the line above the post date."""
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    for current, following in zip(lines, lines[1:]):
        if re.fullmatch(r"\d{1,2}[/-]\d{1,2}[/-]\d{4}", following) and not current.startswith(("[", "!", "*")):
            return current
    return None


async def crawl_article(url: str) -> dict:
    """Crawl một URL; ưu tiên Crawl4AI, fallback requests."""
    try:
        from crawl4ai import AsyncWebCrawler

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            title = "Unknown"
            if getattr(result, "metadata", None):
                title = result.metadata.get("title") or title
            content = getattr(result, "markdown", None) or ""
            if content and len(content.strip()) >= 200:
                if title == "Unknown":
                    title = _title_from_markdown(content) or title
                return {
                    "url": url,
                    "title": title,
                    "date_crawled": datetime.now().isoformat(),
                    "content_markdown": content.strip(),
                }
    except Exception as error:
        print(f"Crawl4AI failed for {url}: {error}; falling back to requests")

    response = await asyncio.to_thread(
        requests.get, url, headers=HEADERS, timeout=60
    )
    response.raise_for_status()
    title, content = _html_to_markdown(response.text)
    if len(content) < 200:
        raise RuntimeError(f"Content too short for {url}")
    if not title:
        title = urlparse(url).path.rsplit("/", 1)[-1] or "Unknown"
    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": content,
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
