"""Main Streamlit application."""

from typing import Any

import streamlit as st

from src.application.chat_service import ChatService
from src.application.document_service import DocumentService
from src.application.factory import ApplicationServices, build_application_services
from src.config.logging_config import get_logger, setup_logging
from src.config.settings import Settings, get_settings
from src.domain.exceptions import ChatError, DocumentError, DomainError
from src.domain.models.chat import ChatMessage, MessageRole
from src.infrastructure import InfrastructureServices, build_infrastructure_services

_logger = get_logger(__name__)


@st.cache_resource(show_spinner=False)
def _bootstrap() -> ApplicationServices:
    """Build and cache application services for the Streamlit session.

    Streamlit reruns the script on every interaction, so the wired
    services are cached process-wide via ``st.cache_resource`` and are
    only constructed once per server process.

    Returns:
        Wired application services (document ingestion + RAG chat).
    """
    settings: Settings = get_settings()
    setup_logging(settings)
    settings.ensure_runtime_directories()

    infrastructure: InfrastructureServices = build_infrastructure_services(settings)
    services = build_application_services(settings, infrastructure)
    services.document_service.initialize_index()
    return services


def _init_session_state() -> None:
    """Initialize Streamlit session state containers."""
    if "messages" not in st.session_state:
        st.session_state.messages: list[ChatMessage] = []
    if "indexed_documents" not in st.session_state:
        st.session_state.indexed_documents: list[str] = []


def _render_sidebar(document_service: DocumentService) -> None:
    """Render the sidebar: PDF upload, ingestion, and index status."""
    with st.sidebar:
        st.header("📁 Documents")

        uploaded_file = st.file_uploader(
            "Upload a PDF",
            type=["pdf"],
            help="Upload a PDF document to index and chat with.",
        )

        if uploaded_file is not None:
            already_indexed = uploaded_file.name in st.session_state.indexed_documents
            if not already_indexed and st.button(
                "📥 Ingest document", use_container_width=True
            ):
                _ingest_document(document_service, uploaded_file)

        st.divider()

        if document_service.is_index_ready():
            st.success("✅ Index ready — you can start asking questions.")
        else:
            st.info("ℹ️ Upload and ingest a PDF to get started.")

        if st.session_state.indexed_documents:
            st.subheader("Indexed documents")
            for name in st.session_state.indexed_documents:
                st.markdown(f"- {name}")

        st.divider()
        if st.button("🗑️ Clear chat history", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def _ingest_document(document_service: DocumentService, uploaded_file: Any) -> None:
    """Persist and index an uploaded PDF, surfacing progress and errors."""
    with st.spinner(f"Indexing '{uploaded_file.name}'..."):
        try:
            content = uploaded_file.getvalue()
            result = document_service.ingest_upload(uploaded_file.name, content)
        except DomainError as exc:
            _logger.warning("Ingestion failed | filename=%s", uploaded_file.name)
            st.error(f"❌ Failed to ingest '{uploaded_file.name}': {exc.message}")
            return
        except Exception:
            _logger.exception(
                "Unexpected ingestion failure | filename=%s", uploaded_file.name
            )
            st.error("❌ An unexpected error occurred while ingesting the document.")
            return

    st.session_state.indexed_documents.append(result.document_name)
    st.success(
        f"✅ Indexed '{result.document_name}' "
        f"({result.page_count} pages, {result.chunk_count} chunks)."
    )
    st.rerun()


def _render_chat_history() -> None:
    """Render previously exchanged chat messages."""
    for message in st.session_state.messages:
        with st.chat_message(message.role.value):
            st.markdown(message.content)


def _render_chat_input(chat_service: ChatService, document_service: DocumentService) -> None:
    """Render the chat input box and handle new question submission."""
    question = st.chat_input(
        "Ask a question about your documents...",
        disabled=not document_service.is_index_ready(),
    )
    if not question:
        return

    user_message = ChatMessage(role=MessageRole.USER, content=question)
    st.session_state.messages.append(user_message)
    with st.chat_message(MessageRole.USER.value):
        st.markdown(question)

    with st.chat_message(MessageRole.ASSISTANT.value):
        with st.spinner("Thinking..."):
            try:
                response = chat_service.ask(question)
            except ChatError as exc:
                st.warning(f"⚠️ {exc.message}")
                return
            except DomainError as exc:
                _logger.warning("Chat request failed | error=%s", exc.message)
                st.error(f"❌ {exc.message}")
                return
            except Exception:
                _logger.exception("Unexpected chat failure.")
                st.error("❌ An unexpected error occurred while answering your question.")
                return

        st.markdown(response.answer)
        if response.sources:
            with st.expander("📚 Sources"):
                for index, source in enumerate(response.sources, start=1):
                    page_label = f", page {source.page}" if source.page else ""
                    st.markdown(f"**[{index}] {source.source}{page_label}** (score: {source.score:.3f})")
                    st.caption(source.excerpt)

    assistant_message = ChatMessage(role=MessageRole.ASSISTANT, content=response.answer)
    st.session_state.messages.append(assistant_message)


def render_app() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="PDF Chatbot (RAG)",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("📄 PDF Chatbot (RAG)")
    st.caption("Chat with your PDF documents using Retrieval-Augmented Generation (RAG).")

    try:
        services = _bootstrap()
    except Exception as exc:  # Settings/validation or adapter construction failure.
        _logger.exception("Failed to bootstrap application services.")
        st.error(
            "❌ Failed to start the application. Check your configuration "
            f"(e.g. GOOGLE_API_KEY in `.env`).\n\nDetails: {exc}"
        )
        st.stop()
        return

    _init_session_state()
    _render_sidebar(services.document_service)
    _render_chat_history()
    _render_chat_input(services.chat_service, services.document_service)


# Alias kept for direct-run / import-by-name compatibility.
main = render_app


if __name__ == "__main__":
    render_app()
