"""Prompt construction utilities for RAG use cases."""

from collections.abc import Sequence

from src.domain.models.document import RetrievedChunk

_SYSTEM_INSTRUCTIONS = """You are a helpful assistant that answers questions strictly based on the provided context from uploaded PDF documents.

Rules:
- Use only the supplied context to answer the question.
- If the context does not contain enough information, clearly state that you cannot answer from the documents.
- Be concise, accurate, and factual.
- Do not invent information that is not supported by the context.
"""


class RAGPromptBuilder:
    """Build prompts for retrieval-augmented generation."""

    def build(self, question: str, contexts: Sequence[RetrievedChunk]) -> str:
        """Construct a RAG prompt from a question and retrieved context chunks.

        Args:
            question: User question to answer.
            contexts: Retrieved document chunks ordered by relevance.

        Returns:
            Fully formatted prompt ready for LLM generation.
        """
        context_block = self._format_contexts(contexts)

        return (
            f"{_SYSTEM_INSTRUCTIONS}\n\n"
            f"Context:\n{context_block}\n\n"
            f"Question: {question.strip()}\n\n"
            "Answer:"
        )

    def _format_contexts(self, contexts: Sequence[RetrievedChunk]) -> str:
        """Format retrieved chunks into a numbered context block."""
        formatted_sections: list[str] = []

        for index, retrieved in enumerate(contexts, start=1):
            metadata = retrieved.chunk.metadata
            page_label = (
                f"page {metadata.page}" if metadata.page is not None else "page unknown"
            )
            formatted_sections.append(
                "\n".join(
                    [
                        f"[Source {index}]",
                        f"Document: {metadata.source}",
                        f"Location: {page_label}",
                        f"Relevance: {retrieved.score:.4f}",
                        f"Content: {retrieved.chunk.content}",
                    ]
                )
            )

        return "\n\n".join(formatted_sections)
