"""Model-provider parsing and chat-model construction for JUDIAgent."""

from __future__ import annotations

from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

_MODEL_HINTS = {
    "openai": "Ensure the model name is correct and OPENAI_API_KEY is set.",
    "anthropic": (
        "Ensure the model name is correct and ANTHROPIC_API_KEY is set."
    ),
    "deepseek": "Ensure the DEEPSEEK_API_KEY is set.",
    "ollama": "Ensure the model is pulled and Ollama is running.",
}


def resolve_provider_and_model(fully_qualified: str) -> tuple[str, str]:
    """Split ``provider:model`` into ``(provider, model_name)``."""
    if ":" not in fully_qualified:
        raise ValueError(
            "Expected model in 'provider:model' format, "
            f"received: {fully_qualified!r}"
        )
    provider, model_name = fully_qualified.split(":", maxsplit=1)
    return provider, model_name


def build_model_init_kwargs(
    provider: str,
    model_name: str,
    *,
    temperature: float,
    streaming: bool = False,
) -> dict[str, Any]:
    """Return normalized LangChain init kwargs for a configured model."""
    kwargs: dict[str, Any] = {
        "temperature": temperature,
        "streaming": streaming,
    }
    if provider == "ollama" and model_name == "qwen3:14b":
        kwargs["reasoning"] = True
    return kwargs


def instantiate_chat_model(
    fully_qualified: str,
    *,
    temperature: float,
    streaming: bool = False,
) -> BaseChatModel:
    """Instantiate a LangChain chat model from a ``provider:model`` string."""
    provider, model_name = resolve_provider_and_model(fully_qualified)
    init_kwargs = build_model_init_kwargs(
        provider,
        model_name,
        temperature=temperature,
        streaming=streaming,
    )
    try:
        return init_chat_model(
            model_name,
            model_provider=provider,
            **init_kwargs,
        )
    except Exception as exc:
        raise ValueError(
            f"Failed to load {provider} model '{model_name}': {exc}. "
            f"{_MODEL_HINTS.get(provider, '')}"
        ) from exc
