from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from judiagent.core.history import compact_message_history, strip_orphaned_tool_messages
from judiagent.core.models import resolve_provider_and_model


def test_resolve_provider_and_model_supports_provider_model_strings():
    provider, model = resolve_provider_and_model("ollama:qwen3:14b")
    assert provider == "ollama"
    assert model == "qwen3:14b"


def test_strip_orphaned_tool_messages_removes_leading_unpaired_tool_messages():
    messages = [
        ToolMessage(content="orphaned", tool_call_id="missing"),
        HumanMessage(content="continue"),
    ]
    cleaned = strip_orphaned_tool_messages(messages)
    assert len(cleaned) == 1
    assert isinstance(cleaned[0], HumanMessage)


def test_compact_message_history_falls_back_when_model_cannot_count_tokens():
    messages = [
        HumanMessage(content="intro"),
        AIMessage(
            content="tool call",
            tool_calls=[{"id": "call-1", "name": "demo", "args": {}}],
        ),
        ToolMessage(content="tool result", tool_call_id="call-1"),
        HumanMessage(content="tail " * 200),
    ]

    trimmed = compact_message_history(
        messages,
        model=object(),  # Forces the fallback token counter path.
        max_tokens=400,
        drop_orphaned_tool_messages=False,
    )

    assert trimmed
    assert isinstance(trimmed[-1], HumanMessage)
