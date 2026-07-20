"""Google Gemini LLM adapter."""

from langchain_google_genai import ChatGoogleGenerativeAI

from src.config.settings import Settings
from src.domain.exceptions import LLMError
from src.domain.interfaces import LLMPort
from src.infrastructure.logging import InfrastructureLogger, get_infrastructure_logger


class GeminiLLM(LLMPort):
    """Generate natural-language completions using Google Gemini via LangChain."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the Gemini chat client.

        Args:
            settings: Validated application settings.
        """
        self._settings = settings
        self._logger = InfrastructureLogger(get_infrastructure_logger(__name__))
        self._client = ChatGoogleGenerativeAI(
            model=settings.model_name,
            google_api_key=settings.google_api_key,
        )

    def generate(self, prompt: str) -> str:
        """Generate a completion for the given prompt.

        Args:
            prompt: Fully constructed prompt including retrieved context.

        Returns:
            Generated response text.

        Raises:
            LLMError: If the prompt is empty or generation fails.
        """
        normalized_prompt = prompt.strip()
        if not normalized_prompt:
            raise LLMError("Cannot generate a completion for an empty prompt.")

        self._logger.operation_start("generate", prompt_length=len(normalized_prompt))

        try:
            result = self._client.invoke(normalized_prompt)
        except Exception as exc:
            self._logger.operation_failure(
                "generate",
                exc,
                prompt_length=len(normalized_prompt),
            )
            raise LLMError(
                "Failed to generate a response using Gemini.",
                cause=exc,
            ) from exc

        answer = self._extract_text(result)
        if not answer:
            error = LLMError("Gemini returned an empty response.")
            self._logger.operation_failure(
                "generate",
                error,
                prompt_length=len(normalized_prompt),
            )
            raise error

        self._logger.operation_success(
            "generate",
            prompt_length=len(normalized_prompt),
            response_length=len(answer),
        )
        return answer

    @staticmethod
    def _extract_text(result: object) -> str:
        """Extract plain text content from a LangChain chat model response."""
        content = getattr(result, "content", result)

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict) and isinstance(item.get("text"), str):
                    parts.append(item["text"])
            return "".join(parts).strip()

        return str(content).strip()
