"""
Task 1 — Thu thập tài liệu chính sách/quy định tuyển sinh ĐHBK Hà Nội.
"""

from pathlib import Path

import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

# PDF chính thức từ hust.edu.vn (phương thức, chỉ tiêu, học phí, ĐGTD).
# Mỗi mục là danh sách URL dự phòng (có/không www).
SOURCES = {
    "qd-phe-duyet-thong-tin-tuyen-sinh-2025.pdf": [
        "https://hust.edu.vn/uploads/sys/tuyen-sinh/2025_06/"
        "qd-phe-duyet-thong-tin-tuyen-sinh-nam-2025-10.06.2025-1.pdf",
    ],
    "qd-quy-dinh-xttn-2025.pdf": [
        "https://hust.edu.vn/uploads/sys/tuyen-sinh/2025_04/qd-dhbk_xttn_2025.pdf",
        "https://www.hust.edu.vn/uploads/sys/tuyen-sinh/2025_04/qd-dhbk_xttn_2025.pdf",
    ],
    "quy-che-thi-danh-gia-tu-duy.pdf": [
        "https://hust.edu.vn/uploads/sys/tuyen-sinh/2023_10/"
        "03102023-quy-che-thi-tu-duy-final.pdf",
        "https://hust.edu.vn/uploads/sys/tuyen-sinh/2023_06/"
        "qd-ban-hanh-quy-che-thi-dgtd-tren-may-tinh.pdf",
    ],
}

LEGAL_METADATA = {
    "qd-phe-duyet-thong-tin-tuyen-sinh-2025.pdf": {
        "title": "QĐ 5919/QĐ-ĐHBK phê duyệt Thông tin tuyển sinh đại học năm 2025",
        "url": SOURCES["qd-phe-duyet-thong-tin-tuyen-sinh-2025.pdf"][0],
    },
    "qd-quy-dinh-xttn-2025.pdf": {
        "title": "Quy định phương thức Xét tuyển tài năng từ năm 2025",
        "url": SOURCES["qd-quy-dinh-xttn-2025.pdf"][0],
    },
    "quy-che-thi-danh-gia-tu-duy.pdf": {
        "title": "Quy chế thi Đánh giá tư duy ĐHBK Hà Nội",
        "url": SOURCES["quy-che-thi-danh-gia-tu-duy.pdf"][0],
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải ít nhất 3 PDF từ nguồn công khai ĐHBK Hà Nội."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for filename, urls in SOURCES.items():
        destination = DATA_DIR / filename
        if destination.exists() and destination.stat().st_size > 1024:
            print(f"Skip (exists): {destination.name}")
            continue
        last_error: Exception | None = None
        for url in urls:
            try:
                print(f"Downloading: {url}")
                response = requests.get(url, headers=HEADERS, timeout=60)
                response.raise_for_status()
                if len(response.content) <= 1024:
                    raise RuntimeError("Downloaded file too small")
                destination.write_bytes(response.content)
                print(f"Saved: {destination} ({destination.stat().st_size} bytes)")
                last_error = None
                break
            except Exception as error:
                last_error = error
                print(f"Failed {url}: {error}")
        if last_error is not None and (
            not destination.exists() or destination.stat().st_size <= 1024
        ):
            raise last_error


if __name__ == "__main__":
    setup_directory()
    download_documents()
