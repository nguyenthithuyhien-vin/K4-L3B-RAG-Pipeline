"""
Task 10 — Generation có citation.
"""

import os
import re
import unicodedata

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.1

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")

SAFE_REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."

SMALL_TALK_ANSWER = (
    "Chào bạn! Mình là trợ lý tuyển sinh ĐHBK Hà Nội. Bạn có thể hỏi về "
    "phương thức xét tuyển, chỉ tiêu, học phí hoặc điểm chuẩn năm 2025, "
    "ví dụ: \"Học phí chương trình chuẩn năm 2025 là bao nhiêu?\""
)

SYSTEM_PROMPT = f"""Bạn là trợ lý tư vấn tuyển sinh Đại học Bách khoa Hà Nội (ĐHBK Hà Nội).

Quy tắc bắt buộc:
1. Chỉ dùng thông tin trong các tài liệu được đánh số [1], [2], ... ở phần Context. Không dùng kiến thức bên ngoài, không suy đoán.
2. Trả lời thẳng vào câu hỏi ngay câu đầu tiên. Ngắn gọn: tối đa 4 câu, hoặc gạch đầu dòng nếu liệt kê.
3. Giữ nguyên con số, đơn vị, mã ngành, tổ hợp, năm đúng như trong nguồn.
4. Đặt citation [n] ngay sau mỗi ý lấy từ tài liệu n; nhiều nguồn thì viết [1][3]. Chỉ trích dẫn tài liệu thực sự chứa thông tin đó.
5. Nếu Context chỉ trả lời được một phần, vẫn trả lời phần có căn cứ (kèm citation), rồi nói ngắn gọn phần nào nguồn chưa đề cập.
6. Chỉ khi Context hoàn toàn không có thông tin liên quan, hoặc câu hỏi không thuộc chủ đề tuyển sinh ĐHBK Hà Nội, mới trả lời đúng một câu duy nhất: "{SAFE_REFUSAL}"
7. Không chào hỏi, không lặp lại câu hỏi, không nhắc tới "Context" hay "tài liệu được cung cấp".
8. Viết bằng tiếng Việt."""

THANKS_ANSWER = "Không có gì! Nếu cần thêm thông tin tuyển sinh ĐHBK Hà Nội, bạn cứ hỏi nhé."

_GREETING_PATTERN = re.compile(
    r"^(hi|hello|hey|alo|chao|xin chao|chao ban|chao bot|hi bot|hello bot|"
    r"ban la ai|ban la gi|ban lam duoc gi|ban giup duoc gi)[\s!.?]*$"
)
_THANKS_PATTERN = re.compile(
    r"^(cam on|cam on ban|thanks|thank you|thank|ok|oke|okay|bye|tam biet)[\s!.?]*$"
)
_CITATION_PATTERN = re.compile(r"\[(?:Document\s+|Tài liệu\s+)?(\d+)\]", re.IGNORECASE)


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower().strip())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d")


def small_talk_reply(query: str) -> str | None:
    normalized = _normalize(query)
    if _GREETING_PATTERN.match(normalized):
        return SMALL_TALK_ANSWER
    if _THANKS_PATTERN.match(normalized):
        return THANKS_ANSWER
    return None


def _dedupe(chunks: list[dict]) -> list[dict]:
    """Drop chunks whose text duplicates a higher-ranked one (mirrored articles)."""
    seen = set()
    unique = []
    for chunk in chunks:
        key = " ".join(chunk["content"].split())[:200].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(chunk)
    return unique


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        parts.append(
            f"[{index}] Title: {metadata['title']} | Source: {metadata['source']}\n"
            f"{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    provider = LLM_PROVIDER.lower()
    model = LLM_MODEL or "gpt-4o"

    if provider == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return (response.choices[0].message.content or "").strip()

    if provider == "gemini":
        from google import genai

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        prompt = f"{system_prompt}\n\n{user_message}"
        response = client.models.generate_content(model=model, contents=prompt)
        return (response.text or "").strip()

    if provider == "anthropic":
        from anthropic import Anthropic

        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return "".join(
            block.text for block in response.content if getattr(block, "text", None)
        ).strip()

    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


def _refusal() -> dict:
    return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}


def _attach_cited_sources(
    answer: str, context_chunks: list[dict], ranked_chunks: list[dict]
) -> tuple[str, list[dict]]:
    """Keep only cited chunks and renumber citations to match the sources list.

    Context labels follow ``context_chunks`` (reordered), while ``sources`` must
    stay sorted by score, so every label is remapped to its position in sources.
    """
    cited_ids = set()
    for match in _CITATION_PATTERN.finditer(answer):
        label = int(match.group(1))
        if 1 <= label <= len(context_chunks):
            cited_ids.add(context_chunks[label - 1]["id"])

    sources = [chunk for chunk in ranked_chunks if chunk["id"] in cited_ids]
    position = {chunk["id"]: index for index, chunk in enumerate(sources, 1)}

    def renumber(match: re.Match) -> str:
        label = int(match.group(1))
        if not 1 <= label <= len(context_chunks):
            return ""
        return f"[{position[context_chunks[label - 1]['id']]}]"

    return _CITATION_PATTERN.sub(renumber, answer).strip(), sources


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    from .task5_semantic_search import semantic_search
    from .task9_retrieval_pipeline import SCORE_THRESHOLD

    if not query.strip():
        return _refusal()
    reply = small_talk_reply(query)
    if reply:
        return {"answer": reply, "sources": [], "retrieval_source": "none"}

    try:
        chunks = _dedupe(retrieve(query, top_k=top_k * 2))[:top_k]
    except Exception:
        return _refusal()
    if not chunks:
        return _refusal()

    is_pageindex = chunks[0].get("retrieval_method") == "pageindex"
    if not is_pageindex:
        try:
            dense_probe = semantic_search(query, top_k=1)
            best_dense = dense_probe[0]["score"] if dense_probe else 0.0
        except Exception:
            best_dense = 0.0
        if best_dense < SCORE_THRESHOLD:
            return _refusal()

    reordered = reorder_for_llm(chunks)
    user_message = (
        f"Context:\n{format_context(reordered)}\n\n"
        f"Câu hỏi: {query}"
    )
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception:
        # Provider unavailable: return the top evidence extractively.
        snippet = chunks[0]["content"].strip()[:500]
        return {
            "answer": f"Chưa gọi được mô hình ngôn ngữ; đoạn nguồn liên quan nhất:\n\n{snippet} [1]",
            "sources": [chunks[0]],
            "retrieval_source": "pageindex" if is_pageindex else "hybrid",
        }

    if not answer.strip() or answer.strip().strip('"').rstrip(".") == SAFE_REFUSAL.rstrip("."):
        return _refusal()

    answer, sources = _attach_cited_sources(answer, reordered, chunks)
    if not sources:
        return _refusal()

    return {
        "answer": answer,
        "sources": sources,
        "retrieval_source": "pageindex" if is_pageindex else "hybrid",
    }


if __name__ == "__main__":
    print(generate_with_citation("ĐHBK Hà Nội có bao nhiêu phương thức xét tuyển?"))
