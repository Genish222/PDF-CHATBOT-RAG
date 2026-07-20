"""Infrastructure layer — external system adapters and factories."""

from dataclasses import dataclass

from src.config.settings import Settings
from src.domain.interfaces import (
    EmbeddingPort,
    LLMPort,
    PDFLoaderPort,
    TextSplitterPort,
    VectorStorePort,
)
from src.infrastructure.embeddings.gemini_embeddings import GeminiEmbeddingsAdapter
from src.infrastructure.llm.gemini_llm import GeminiLLM
from src.infrastructure.logging import InfrastructureLogger, get_infrastructure_logger
from src.infrastructure.pdf.pypdf_loader import PyPDFLoader
from src.infrastructure.text_splitter.langchain_splitter import LangChainTextSplitter
from src.infrastructure.vectorstore.faiss_store import FAISSVectorStore


@dataclass(frozen=True, slots=True)
class InfrastructureServices:
    """Container for wired infrastructure adapters.

    Attributes:
        pdf_loader: PDF loading adapter.
        text_splitter: Document chunking adapter.
        embeddings: Gemini embeddings adapter.
        vector_store: FAISS vector store adapter.
        llm: Gemini chat completion adapter.
    """

    pdf_loader: PDFLoaderPort
    text_splitter: TextSplitterPort
    embeddings: EmbeddingPort
    vector_store: VectorStorePort
    llm: LLMPort


def build_infrastructure_services(settings: Settings) -> InfrastructureServices:
    """Construct and wire all infrastructure adapters.

    Args:
        settings: Validated application settings.

    Returns:
        Wired infrastructure services ready for application-layer use.
    """
    logger = InfrastructureLogger(get_infrastructure_logger(__name__))
    logger.operation_start("build_infrastructure_services")

    embeddings = GeminiEmbeddingsAdapter(settings)
    vector_store = FAISSVectorStore(settings, embeddings)
    llm = GeminiLLM(settings)

    services = InfrastructureServices(
        pdf_loader=PyPDFLoader(settings),
        text_splitter=LangChainTextSplitter(settings),
        embeddings=embeddings,
        vector_store=vector_store,
        llm=llm,
    )

    logger.operation_success("build_infrastructure_services")
    return services


__all__ = [
    "FAISSVectorStore",
    "GeminiEmbeddingsAdapter",
    "GeminiLLM",
    "InfrastructureLogger",
    "InfrastructureServices",
    "LangChainTextSplitter",
    "PyPDFLoader",
    "build_infrastructure_services",
    "get_infrastructure_logger",
]
