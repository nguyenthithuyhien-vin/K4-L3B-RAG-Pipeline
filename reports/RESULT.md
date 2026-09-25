# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-25 |
| Framework and version              | custom RAG pipeline + 4-metric A/B |
| Evaluator model                    | keyword-overlap heuristic on gpt-4o answers |
| Generator model                    | gpt-4o |
| Embedding model                    | BAAI/bge-m3 via sentence_transformers |
| Corpus version/commit              | HUST 2025 admissions: 3 legal PDF + 5 news pages |
| Golden dataset size                | 18 |
| `top_k`                            | 5 |
| Fallback threshold and calibration | 0.55 (in-domain dense ~0.66–0.69; out-of-domain ~0.46–0.47) |

## Configurations

- **Config A — dense-only:** `semantic_search` top_k=5, no BM25, no RRF
- **Config B — hybrid + RRF:** dense + BM25 fused once with RRF (k=60), same generator/prompt/top_k

Hai config dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |   0.8168 |   0.8228 |   +0.0060 |
| Answer relevance  |   0.5196 |   0.5743 |   +0.0547 |
| Context recall    |   0.8435 |   0.8986 |   +0.0551 |
| Context precision |   0.8667 |   0.9000 |   +0.0333 |
| **Average**       |   0.7616 |   0.7989 |   +0.0373 |

## A/B comparison

- Cấu hình tốt hơn: **Config B (hybrid + RRF)**
- Evidence: Hybrid thắng trên cả 4 metric. Mức cải thiện rõ nhất ở context recall (+0.0551) và answer relevance (+0.0547); average +0.0373.
- Trade-off về latency/cost: Hybrid chậm hơn nhẹ vì thêm BM25 + RRF trên ~1175 chunks; embedding query vẫn chỉ chạy một lần dense. Không tăng số lần gọi gpt-4o so với dense-only.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------- | ---------- |
|   1 | Tỷ lệ chỉ tiêu dự kiến của phương thức Đánh giá tư duy là bao nhiêu? | A | 0.20 | 0.00 | 0.00 | 0.00 | retrieval | Dense miss đoạn “ĐGTD ≈40%”; không lấy được context chứa tỷ lệ chỉ tiêu |
|   2 | Tỷ lệ chỉ tiêu dự kiến của phương thức Đánh giá tư duy là bao nhiêu? | B | 0.71 | 0.62 | 0.67 | 0.20 | retrieval | Hybrid bắt được keyword nhưng precision thấp vì chunk lân cận loãng |
|   3 | Thí sinh đăng ký thi Đánh giá tư duy ở đâu? | B | 0.92 | 0.10 | 0.50 | 0.80 | generation | Context có `tsa.hust.edu.vn` nhưng answer paraphrase làm giảm overlap expected |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Giữ hybrid làm mặc định; dense-only chỉ baseline A/B | Hybrid average 0.7989 > dense 0.7616; thắng cả 4 metric | Demo ổn định hơn trên câu hỏi tỷ lệ/chỉ tiêu | So cùng câu ĐGTD trên UI |
|        2 | Chunk theo heading/section cho khối “Thông tin chung / chỉ tiêu” | Worst case tỷ lệ ĐGTD ≈40% | +context recall/precision trên câu số liệu ngắn | Re-run A/B subset 5 câu tỷ lệ/học phí |
|        3 | Bổ sung alias trong retrieval (ĐGTD / TSA / đánh giá tư duy) | Query “Đánh giá tư duy” dễ lệch semantic | Ít miss trên synonym | Test 3 paraphrases cùng intent |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| (không chạy trong lab 3 giờ) | hybrid | n/a | n/a | Ưu tiên core pipeline, citation UX và A/B dense vs hybrid |
