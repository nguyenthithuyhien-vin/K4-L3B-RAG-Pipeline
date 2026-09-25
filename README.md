# Day 8 — RAG Pipeline: Tuyển sinh ĐHBK Hà Nội

## Mục tiêu

Chatbot RAG trả lời câu hỏi về **phương thức xét tuyển, chỉ tiêu, học phí, điểm chuẩn** Đại học Bách khoa Hà Nội (2025), với hybrid retrieval, citation, Streamlit chat và báo cáo A/B.

## Sản phẩm đã hoàn thành

- ≥3 PDF chính sách HUST + ≥5 bài tin/thông báo đã chuẩn hóa Markdown
- Pipeline: convert → chunk → index → dense + BM25 → RRF → fallback → generation có citation
- Chatbot Streamlit hiển thị câu trả lời và nguồn
- Golden dataset 18 câu; A/B dense-only vs hybrid + RRF trong `group_project/evaluation/RESULT.md`
- Báo cáo cá nhân: `reports/solo-nguyen-hien.md`

## Quick start

```bash
python3.12 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
python -m playwright install chromium
cp .env.example .env
```

Điền `OPENAI_API_KEY` trong `.env` (model mặc định `gpt-4o`). Không commit file này.

```bash
# 1. Thu thập và chuẩn hoá
python -m src.task1_collect_legal_docs
python -m src.task2_crawl_news
python -m src.task3_convert_markdown

# 2. Index và kiểm tra contract
python -m src.task4_chunking_indexing
pytest -q

# 3. Chạy sản phẩm
streamlit run app.py

# 4. (Tuỳ chọn) Đánh giá A/B
python scripts/build_golden.py
python scripts/evaluate_ab.py
```

## Cấu hình chính

| Biến | Giá trị |
|---|---|
| `LLM_PROVIDER` / `LLM_MODEL` | `openai` / `gpt-4o` |
| `EMBEDDING_PROVIDER` / `EMBEDDING_MODEL` | `sentence_transformers` / `BAAI/bge-m3` |
| `SCORE_THRESHOLD` | `0.55` (calibrate: in-domain ~0.66, out-of-domain ~0.47) |

## Lưu ý quy tắc

- Dense và BM25 cùng schema `SearchResult`
- RRF chỉ fuse thứ hạng một lần
- Fallback dùng cosine score gốc của dense retrieval
- BM25 cộng token-overlap để tránh Okapi IDF=0 trên corpus nhỏ

## Tài liệu

- [Module contracts](docs/MODULE_CONTRACTS.md)
- [Step-by-step guide](docs/STEP_BY_STEP.md)
- [Grading rubric](docs/GRADING_RUBRIC.md)
- [Evaluation results](group_project/evaluation/RESULT.md)

## Kiểm tra

```bash
pytest tests/test_contracts.py -q
pytest tests/test_acceptance.py -q
pytest -q
```
