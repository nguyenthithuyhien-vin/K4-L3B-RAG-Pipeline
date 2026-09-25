# Individual contribution report

## Thông tin

- Họ và tên: (điền họ tên thành viên 2)
- Mã học viên: (điền MSSV)
- Nhóm: K4-L3B Day 8 (2 thành viên)
- Repository/branch: K4-L3B-RAG-Pipeline / main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Fusion + fallback | RRF một lần; PageIndex graceful; `retrieve` hybrid | `src/task7_reranking.py`, `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py` | Done |
| Generation có citation | System prompt gpt-4o, small-talk, map `[n]` → sources | `src/task10_generation.py` | Done |
| Chatbot UI | Streamlit chat messenger; hiển thị nguồn có số và URL | `app.py` | Done |
| Evaluation + report | Golden 18 Q&A; A/B dense vs hybrid; điền RESULT | `scripts/evaluate_ab.py`, `group_project/evaluation/*`, `reports/RESULT.md` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Hybrid + RRF làm mặc định; dense-only chỉ dùng trong A/B.  
   **Lý do/evidence:** RESULT.md: hybrid average **0.7989** > dense **0.7616**; recall +0.0551, relevance +0.0547.  
   **Trade-off:** Latency tăng nhẹ vì thêm BM25 + RRF; không tăng số lần gọi gpt-4o.

2. **Quyết định:** `SCORE_THRESHOLD=0.55` + bypass small-talk + chỉ trả sources được citation.  
   **Lý do/evidence:** In-domain dense ~0.66–0.69 vs out-of-domain ~0.46–0.47; “hi” không còn kéo RAG và citation giả.  
   **Trade-off:** Threshold cao → refusal sớm hơn khi PageIndex không cấu hình.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest -q` (20 passed); “hi”, “học phí chuẩn”, “nấu phở”, A/B `python scripts/evaluate_ab.py`
- Kết quả trước/sau: Trước — greeting vẫn hybrid + `[Document 1]`; Sau — chào không nguồn; câu tuyển sinh trả lời ngắn có `[n]`; OOD safe refusal
- Lỗi đã phát hiện và cách xử lý: Deduplicate chunk trùng giữa bài tin mirror; sync `reports/RESULT.md` với `group_project/evaluation/RESULT.md`

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Answer relevance heuristic thấp hơn cảm nhận người dùng vì gpt-4o paraphrase khác wording golden
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Alias query ĐGTD/TSA + chạy lại ragas judge chính thức

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-25
- Tên thành viên: (điền họ tên thành viên 2)
