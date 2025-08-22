from __future__ import annotations

from typing import Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config import settings


def get_chat_model(model: Optional[str] = None,
                   temperature: Optional[float] = None) -> ChatOpenAI:
    """Return a configured LangChain ChatOpenAI model.

    Defaults are read from settings, with API key via environment.
    """
    use_model = model or settings.ai_model
    temp = settings.ai_temperature if temperature is None else temperature
    # The OpenAI SDK/LC reads api key from env OPENAI_API_KEY if not provided explicitly
    return ChatOpenAI(
        model=use_model,
        temperature=temp,
        max_tokens=settings.ai_max_tokens,
        api_key=settings.openai_api_key,
    )


def get_embedding_model(model: Optional[str] = None) -> OpenAIEmbeddings:
    """Return an embeddings model (configured for OpenAI)."""
    use_model = model or settings.embedding_model
    return OpenAIEmbeddings(
        model=use_model,
        api_key=settings.openai_api_key,
    )

