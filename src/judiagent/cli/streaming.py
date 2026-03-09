"""Streaming output utilities for live JUDIAgent model responses."""

from __future__ import annotations

import re
import time
from typing import List, Optional

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from judiagent.globals import console


def _retry_with_exponential_backoff(
    func,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    error_msg_prefix: str = "Rate limit error",
) -> AIMessage:
    """Retry a function with exponential backoff for rate-limit failures."""
    last_exception: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            result = func()
            if result is not None:
                return result
            raise RuntimeError("Function returned None unexpectedly")
        except Exception as exc:
            last_exception = exc
            error_type = type(exc).__name__
            error_str = str(exc)
            is_rate_limit = (
                "RateLimitError" in error_type
                or "rate_limit" in error_str.lower()
                or "429" in error_str
                or "rate limit" in error_str.lower()
            )
            if not is_rate_limit:
                raise

            wait_time = base_delay * (2**attempt)
            wait_match = re.search(
                r"try again in (\d+)(ms|s|seconds?)",
                error_str,
                re.IGNORECASE,
            )
            if wait_match:
                wait_value = float(wait_match.group(1))
                unit = wait_match.group(2).lower()
                wait_time = wait_value / 1000.0 if "ms" in unit else wait_value
                wait_time *= 1.1
            wait_time = min(wait_time, max_delay)

            if attempt < max_retries - 1:
                console.print(
                    f"[yellow]{error_msg_prefix}: {error_type}. "
                    f"Retrying in {wait_time:.1f}s ({attempt + 1}/{max_retries})[/yellow]"
                )
                time.sleep(wait_time)
            else:
                console.print(
                    f"[red]{error_msg_prefix}: maximum retries exceeded[/red]"
                )
                raise

    raise RuntimeError(f"All {max_retries} retries exhausted") from last_exception


def stream_to_console(
    llm,
    message_list: List,
    config: RunnableConfig,
    title: Optional[str] = "JUDIAgent",
    border_style: str = "steel_blue3",
    panel_kwargs: dict | None = None,
    with_markdown: bool = True,
) -> AIMessage:
    """Stream model output into a live-updating Rich panel."""
    ai_message: Optional[AIMessage] = None
    streamed_text = ""
    panel_kwargs = (panel_kwargs or {}).copy()
    panel_kwargs.setdefault("border_style", border_style)
    panel_kwargs.setdefault("title", f"[bold bright_cyan]{title}[/bold bright_cyan]")

    def _stream_and_process():
        nonlocal ai_message, streamed_text
        ai_message = None
        streamed_text = ""

        stream = llm.stream(message_list, config=config)
        for chunk in stream:
            if chunk.content:
                streamed_text += chunk.content
                ai_message = chunk if ai_message is None else ai_message + chunk
                with Live(
                    Panel(
                        Markdown(streamed_text) if with_markdown else streamed_text,
                        **panel_kwargs,
                    ),
                    console=console,
                    refresh_per_second=6,
                ) as live:
                    for chunk in stream:
                        ai_message = chunk if ai_message is None else ai_message + chunk
                        if chunk.content:
                            streamed_text += chunk.content
                            live.update(
                                Panel.fit(
                                    Markdown(streamed_text)
                                    if with_markdown
                                    else streamed_text,
                                    **panel_kwargs,
                                )
                            )
                break
            elif ai_message is None:
                ai_message = chunk
            else:
                ai_message += chunk

        if ai_message is None:
            raise ValueError("No message content received from the model")
        return ai_message

    return _retry_with_exponential_backoff(
        _stream_and_process,
        max_retries=5,
        base_delay=1.0,
        max_delay=60.0,
        error_msg_prefix="Streaming rate limit exceeded",
    )
