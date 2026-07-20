"""RAG chat use cases."""

from src.application.constants import DEFAULT_TOP_K
from src.application.prompts.rag_prompt_builder import RAGPromptBuilder
from src.config.logging_config import get_logger
from src.domain.exceptions import ChatError, LLMError
from src.domain.interfaces import LLMPort, VectorStorePort
from src.domain.models.chat import ChatResponse, SourceCitation


class ChatService:
    """Orchestrate retrieval-augmented question answering."""

    def __init__(
        self,
        vector_store: VectorStorePort,
        llm: LLMPort,
        prompt_builder: RAGPromptBuilder,
        *,
        top_k: int = DEFAULT_TOP_K,
    ) -> None:
        """Initialize the chat service with required dependencies.

        Args:
            vector_store: Adapter for retrieving relevant document chunks.
            llm: Adapter for generating natural-language answers.
            prompt_builder: Builder for RAG prompts.
            top_k: Maximum number of context chunks to retrieve.
        """
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        self._vector_store = vector_store
        self._llm = llm
        self._prompt_builder = prompt_builder
        self._top_k = top_k
        self._logger = get_logger(__name__)

    def ask(self, question: str) -> ChatResponse:
        """Answer a user question using retrieval-augmented generation.

        Args:
            question: Natural-language question from the user.

        Returns:
            Generated answer with supporting source citations.

        Raises:
            ChatError: If the question is invalid or answering fails.
            VectorStoreError: If retrieval fails unexpectedly.
        """
        normalized_question = question.strip()
        if not normalized_question:
            raise ChatError("Question must not be empty.")

        if self._vector_store.is_empty():
            raise ChatError(
                "No documents are indexed yet. Upload a PDF before asking questions."
            )

        self._logger.info(
            "Processing chat question | length=%d | top_k=%d",
            len(normalized_question),
            self._top_k,
        )

        retrieved_chunks = self._vector_store.similarity_search(
            normalized_question,
            self._top_k,
        )
        if not retrieved_chunks:
            raise ChatError(
                "No relevant context was found in the indexed documents for this question."
            )

        prompt = self._prompt_builder.build(
            question=normalized_question,
            contexts=retrieved_chunks,
        )

        try:
            answer = self._llm.generate(prompt)
        except LLMError:
            raise
        except Exception as exc:
            raise ChatError(
                "Failed to generate an answer for the given question.",
                cause=exc,
            ) from exc

        sources = tuple(
            SourceCitation.from_retrieved_chunk(chunk) for chunk in retrieved_chunks
        )
        response = ChatResponse(answer=answer, sources=sources)

        self._logger.info(
            "Completed chat response | answer_length=%d | source_count=%d",
            len(response.answer),
            len(response.sources),
        )
        return response
