"""Application service factory and container."""

from dataclasses import dataclass

from src.application.chat_service import ChatService
from src.application.constants import DEFAULT_TOP_K
from src.application.document_service import DocumentService
from src.application.prompts.rag_prompt_builder import RAGPromptBuilder
from src.config.logging_config import get_logger
from src.config.settings import Settings
from src.infrastructure import InfrastructureServices


@dataclass(frozen=True, slots=True)
class ApplicationServices:
    """Container for wired application use cases.

    Attributes:
        document_service: Document ingestion and indexing service.
        chat_service: Retrieval-augmented chat service.
    """

    document_service: DocumentService
    chat_service: ChatService


def build_application_services(
    settings: Settings,
    infrastructure: InfrastructureServices,
    *,
    top_k: int = DEFAULT_TOP_K,
) -> ApplicationServices:
    """Construct and wire application-layer services.

    Args:
        settings: Validated application settings.
        infrastructure: Wired infrastructure adapters.
        top_k: Maximum number of context chunks to retrieve during chat.

    Returns:
        Wired application services ready for the presentation layer.
    """
    logger = get_logger(__name__)
    logger.info("Building application services.")

    prompt_builder = RAGPromptBuilder()
    document_service = DocumentService(
        pdf_loader=infrastructure.pdf_loader,
        text_splitter=infrastructure.text_splitter,
        vector_store=infrastructure.vector_store,
        settings=settings,
    )
    chat_service = ChatService(
        vector_store=infrastructure.vector_store,
        llm=infrastructure.llm,
        prompt_builder=prompt_builder,
        top_k=top_k,
    )

    logger.info("Application services built successfully.")
    return ApplicationServices(
        document_service=document_service,
        chat_service=chat_service,
    )
