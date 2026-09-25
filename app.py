import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="HUST Tuyển sinh RAG",
    page_icon="",
    layout="centered",
)

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_sources(sources: list[dict], retrieval_source: str | None) -> None:
    if not sources:
        return
    with st.expander(f"Nguồn trích dẫn ({len(sources)}) · {retrieval_source}"):
        for index, source in enumerate(sources, 1):
            meta = source.get("metadata", {})
            title = meta.get("title") or source.get("id")
            url = meta.get("url")
            heading = f"**[{index}] [{title}]({url})**" if url else f"**[{index}] {title}**"
            st.markdown(heading)
            snippet = " ".join(source.get("content", "").split())[:300]
            st.caption(f"{snippet}…  \nscore={source.get('score', 0):.3f}")


with st.sidebar:
    st.title("Tuyển sinh ĐHBK")
    st.caption("Phương thức · Chỉ tiêu · Học phí · Điểm chuẩn")
    top_k = st.slider("Số chunks", 3, 10, 5)
    if st.button("Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()

st.title("Chat tuyển sinh HUST")
st.caption("Hỏi ngắn gọn; câu trả lời kèm nguồn trích dẫn [n].")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(message.get("sources", []), message.get("retrieval_source"))

query = st.chat_input("Nhập câu hỏi về tuyển sinh...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm nguồn và trả lời..."):
            result = generate_with_citation(query, top_k=top_k)
        st.markdown(result["answer"])
        render_sources(result["sources"], result["retrieval_source"])

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
            "retrieval_source": result["retrieval_source"],
        }
    )
