from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong cơ sở tri thức."

        context_blocks = []
        for i, r in enumerate(results, 1):
            source = r.get("metadata", {}).get("source", r.get("id", f"doc_{i}"))
            context_blocks.append(f"[{i}] (Nguồn: {source})\n{r['content']}")

        context_str = "\n\n".join(context_blocks)
        prompt = (
            f"Bạn là một trợ lý giải đáp dựa trên tài liệu được cung cấp.\n\n"
            f"NGỮ CẢNH:\n{context_str}\n\n"
            f"CÂU HỎI: {question}\n\n"
            f"HƯỚNG DẪN:\n"
            f"- Hãy trả lời câu hỏi dựa trên các đoạn trích trong ngữ cảnh trên.\n"
            f"- Hãy trích dẫn số thứ tự tài liệu [1], [2] khi đưa ra thông tin.\n"
            f"- Nếu trong ngữ cảnh không có thông tin, hãy thông báo rằng tài liệu không đề cập."
        )
        return self.llm_fn(prompt)
