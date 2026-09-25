# Individual contribution report

## Thông tin

- Họ và tên: Nguyen Hien
- Mã học viên: (điền MSSV)
- Nhóm: K4-L3B Day 8 (2 thành viên)
- Repository/branch: K4-L3B-RAG-Pipeline / main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Data collection | Tải 3 PDF HUST + crawl 5 bài tin; URL dự phòng khi DNS lỗi | `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py` | Done |
| Convert Markdown | MarkItDown PDF→MD; gắn title/URL metadata chuẩn | `src/task3_convert_markdown.py` | Done |
| Chunk / embed / index | Recursive chunk 500/50, BGE-M3, Chroma cosine | `src/task4_chunking_indexing.py` | Done |
| Dense + BM25 | Semantic search; BM25 + token-overlap (fix IDF=0) | `src/task5_semantic_search.py`, `src/task6_lexical_search.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Embedding local `BAAI/bge-m3` + Chroma cosine, dùng chung `embed_texts()` cho index và query.  
   **Lý do/evidence:** Contract bắt buộc chung model; tiếng Việt ổn với BGE-M3; chạy được offline embedding.  
   **Trade-off:** Lần đầu tải model chậm; tốn RAM hơn embedding API.

2. **Quyết định:** Cộng token-overlap vào BM25 score trên corpus nhỏ.  
   **Lý do/evidence:** Okapi IDF = 0 khi `df = N/2` → test lexical và keyword query fail; overlap giữ ranking đúng.  
   **Trade-off:** Score không còn “thuần” BM25; cần ghi rõ trong report.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest tests/test_contracts.py` (chunk/dense/bm25); query “chỉ tiêu tuyển sinh 2025”, “học phí chương trình chuẩn”
- Kết quả trước/sau: Trước — lexical trả rỗng trên corpus 2 doc; Sau — top hit đúng keyword; index ~1175 chunks từ 8 tài liệu
- Lỗi đã phát hiện và cách xử lý: DNS `www.hust.edu.vn` → URL không www; title news “Unknown” → fallback lấy tiêu đề từ body

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Dense vẫn miss một số câu tỷ lệ ngắn (ĐGTD ≈40%) vì chunking theo độ dài chữ, không theo heading
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Chunk theo section/heading cho khối chỉ tiêu và bảng học phí

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-25
- Tên thành viên: Nguyen Hien
