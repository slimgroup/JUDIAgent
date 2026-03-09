"""
Core agent foundation for the JUDIAgent framework.

:class:`AgentCore` provides the shared infrastructure that every concrete
agent (iterative code-generation, autonomous ReAct, etc.) inherits:

* LLM initialisation, tool binding, and retry-resilient invocation
* Conversation-history compaction (token-aware trimming)
* LangGraph workflow scaffolding (entry points, tool routing, user input)
* CLI / MCP mode dispatching
"""

from __future__ import annotations

import os
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Literal, Optional, Sequence, Union, cast

from langchain_core.language_models import BaseChatModel, LanguageModelLike
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import (
    Runnable,
    RunnableBinding,
    RunnableConfig,
    RunnableSequence,
)
from langchain_core.tools import BaseTool
from langgraph.errors import ErrorCode, create_error_message
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.utils.runnable import RunnableCallable

import judiagent.state as state_mod
from judiagent.cli import colorscheme, show_startup_screen, stream_to_console
from judiagent.configuration import LLM_TEMPERATURE, PROJECT_ROOT, RECURSION_LIMIT
from judiagent.core.history import compact_message_history, strip_orphaned_tool_messages
from judiagent.core.models import instantiate_chat_model, resolve_provider_and_model
from judiagent.globals import console
from judiagent.state import AgentState


class AgentCore(ABC):
    """
    Abstract foundation for every JUDIAgent agent variant.

    Subclasses must implement:

    * :meth:`construct_workflow` – build the LangGraph state machine
    * :meth:`resolve_model_config` – return the model identifier
    * :meth:`resolve_prompt_config` – return the system prompt
    """

    def __init__(
        self,
        tools: Union[Sequence[Union[BaseTool, Callable, dict[str, Any]]], ToolNode],
        name: Optional[str] = None,
        display_name: Optional[str] = "",
        is_sub_agent: Optional[bool] = False,
        stream_output: bool = True,
    ):
        if name is not None and (" " in name or not name):
            raise ValueError("Agent name must not contain spaces and cannot be empty.")

        self.is_sub_agent = is_sub_agent
        self.name = name or self.__class__.__name__
        self.display_name = display_name if display_name else name
        self.workflow_state_type = state_mod.AgentState
        self.stream_output = stream_output

        if isinstance(tools, ToolNode):
            self.registered_tools = list(tools.tools_by_name.values())
            self.tool_executor_node = tools
        else:
            self.tool_executor_node = ToolNode(
                [t for t in tools if not isinstance(t, dict)]
            )
            self.registered_tools = list(self.tool_executor_node.tools_by_name.values())

        self.direct_response_tools: set[str] = {
            t.name for t in self.registered_tools if t.return_direct
        }

        self.graph = self.construct_workflow()

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def resolve_prompt_config(self, config: RunnableConfig) -> str:
        """Return the system prompt appropriate for this agent variant."""

    @abstractmethod
    def resolve_model_config(
        self, config: RunnableConfig
    ) -> Union[str, LanguageModelLike]:
        """Return the model identifier (``'provider:model'``) or an instance."""

    @abstractmethod
    def construct_workflow(self) -> Any:
        """
        Assemble and compile the LangGraph state machine for this agent.

        Subclasses wire up nodes, edges, and conditional routing here.
        See the LangGraph documentation for ReAct-style and custom graphs.
        """

    # ------------------------------------------------------------------
    # Model resolution
    # ------------------------------------------------------------------

    def _resolve_model_instance(
        self, model: Union[str, LanguageModelLike]
    ) -> BaseChatModel:
        """
        Normalise *model* to a concrete :class:`BaseChatModel`.

        Handles string identifiers (``'openai:gpt-4o'``), runnable
        sequences, and pre-bound models.
        """
        if isinstance(model, str):
            resolve_provider_and_model(model)
            chat_model = instantiate_chat_model(
                model,
                temperature=LLM_TEMPERATURE,
                streaming=True,
            )
            model = cast(BaseChatModel, chat_model)

        if isinstance(model, RunnableSequence):
            model = next(
                (
                    step
                    for step in model.steps
                    if isinstance(step, (RunnableBinding, BaseChatModel))
                ),
                model,
            )
        if isinstance(model, RunnableBinding):
            model = model.bound
        if not isinstance(model, BaseChatModel):
            raise TypeError(
                f"Expected a BaseChatModel, got {type(model).__name__}"
            )
        return cast(BaseChatModel, model)

    def _setup_language_model(self, config: RunnableConfig) -> BaseChatModel:
        """Load, bind tools to, and return the chat model for this config."""
        llm = self._resolve_model_instance(self.resolve_model_config(config=config))
        if self._requires_tool_binding(llm):
            llm = llm.bind_tools(self.registered_tools)
        return cast(BaseChatModel, llm)

    def _requires_tool_binding(self, model: BaseChatModel) -> bool:
        """Return ``True`` if the model needs tools bound to it."""
        if not self.registered_tools:
            return False
        if isinstance(model, RunnableBinding) and "tools" in model.kwargs:
            already_bound = model.kwargs["tools"]
            if len(self.registered_tools) != len(already_bound):
                raise ValueError(
                    f"Tool count mismatch: expected {len(self.registered_tools)}, "
                    f"model already has {len(already_bound)}"
                )
            return False
        return True

    # ------------------------------------------------------------------
    # LLM invocation with retry
    # ------------------------------------------------------------------

    def _execute_llm_call(
        self,
        state: state_mod.AgentState,
        config: RunnableConfig,
        messages_list: Optional[List] = None,
    ) -> AIMessage:
        """
        Core LLM invocation with rate-limit retry and streaming support.
        """
        model = self._setup_language_model(config=config)

        workspace_hint = (
            f"**Current workspace:** {os.getcwd()} \n"
            f"**JUDI.jl documentation and examples can be found at:** "
            f"{PROJECT_ROOT / 'rag' / 'judi'}"
        )

        if not messages_list:
            messages_list = [
                SystemMessage(content=self.resolve_prompt_config(config=config)),
                SystemMessage(content=workspace_hint),
            ]
            trimmed = self._compact_conversation_history(state.messages, model)
            messages_list.extend(trimmed)

        if self.stream_output:
            streamed = stream_to_console(
                llm=model,
                message_list=messages_list,
                config=config,
                title=self.display_name,
                border_style=colorscheme.normal,
            )
            response = cast(AIMessage, streamed)
        else:
            response = self._invoke_with_rate_limit_retry(model, messages_list, config)

        response.name = self.name
        return response

    def _invoke_with_rate_limit_retry(
        self,
        model: BaseChatModel,
        messages: list,
        config: RunnableConfig,
        max_attempts: int = 5,
    ) -> AIMessage:
        """Retry on rate-limit (HTTP 429) with exponential back-off."""
        for attempt in range(max_attempts):
            try:
                return cast(AIMessage, model.invoke(messages, config))
            except Exception as exc:
                if not self._is_rate_limit_error(exc):
                    raise
                wait = self._compute_backoff(exc, attempt)
                if attempt < max_attempts - 1:
                    console.print(
                        f"[yellow]Rate limit hit – retrying in {wait:.1f}s "
                        f"(attempt {attempt + 1}/{max_attempts})[/yellow]"
                    )
                    time.sleep(wait)
                else:
                    console.print(
                        f"[red]Max retries ({max_attempts}) exhausted[/red]"
                    )
                    raise
        raise RuntimeError("LLM invocation failed after all retries")

    @staticmethod
    def _is_rate_limit_error(exc: Exception) -> bool:
        name = type(exc).__name__
        msg = str(exc).lower()
        return (
            "RateLimitError" in name
            or "rate_limit" in msg
            or "429" in str(exc)
            or "rate limit" in msg
        )

    @staticmethod
    def _compute_backoff(exc: Exception, attempt: int) -> float:
        base = min(1.0 * (2 ** attempt), 60.0)
        match = re.search(
            r"try again in (\d+)(ms|s|seconds?)", str(exc), re.IGNORECASE
        )
        if match:
            val = float(match.group(1))
            unit = match.group(2).lower()
            base = (val / 1000.0 if "ms" in unit else val) * 1.1
        return min(base, 60.0)

    # ------------------------------------------------------------------
    # Message-history management
    # ------------------------------------------------------------------

    def _compact_conversation_history(
        self,
        messages: Sequence[BaseMessage],
        model: Union[BaseChatModel, Runnable[LanguageModelInput, BaseMessage]],
    ) -> Sequence[BaseMessage]:
        """Trim conversation to fit token budget, then fix orphaned tool messages."""
        return compact_message_history(
            messages,
            model,
            include_system=False,
            drop_orphaned_tool_messages=True,
        )

    @staticmethod
    def _strip_orphaned_tool_messages(
        messages: Sequence[BaseMessage],
    ) -> List[BaseMessage]:
        """
        Drop leading ToolMessages whose parent AIMessage was trimmed away.

        After token-based trimming the oldest messages may vanish, leaving
        ToolMessages that reference a now-missing AIMessage.  The OpenAI API
        rejects such sequences, so we prune them.
        """
        return strip_orphaned_tool_messages(messages)

    def _verify_tool_message_integrity(
        self, messages: Sequence[BaseMessage]
    ) -> None:
        """Raise if any AIMessage.tool_calls lack a corresponding ToolMessage."""
        all_calls = [
            tc
            for m in messages if isinstance(m, AIMessage)
            for tc in m.tool_calls
        ]
        answered_ids = {
            m.tool_call_id for m in messages if isinstance(m, ToolMessage)
        }
        orphaned = [tc for tc in all_calls if tc["id"] not in answered_ids]
        if orphaned:
            raise ValueError(
                create_error_message(
                    message="AIMessages contain tool_calls without matching ToolMessages.",
                    error_code=ErrorCode.INVALID_CHAT_HISTORY,
                )
            )

    # ------------------------------------------------------------------
    # Step-budget checks
    # ------------------------------------------------------------------

    def _is_step_budget_exhausted(
        self, state: state_mod.AgentState, response: BaseMessage
    ) -> bool:
        """Return ``True`` if the graph is about to exceed its step limit."""
        has_calls = isinstance(response, AIMessage) and bool(response.tool_calls)
        all_direct = (
            all(c["name"] in self.direct_response_tools for c in response.tool_calls)
            if isinstance(response, AIMessage) and response.tool_calls
            else False
        )
        remaining = state.remaining_steps
        last = state.is_last_step

        return (
            (remaining is None and last and has_calls)
            or (remaining is not None and remaining < 1 and all_direct)
            or (remaining is not None and remaining < 2 and has_calls)
        )

    # ------------------------------------------------------------------
    # Prompt helpers
    # ------------------------------------------------------------------

    def _build_prompt_chain(
        self, prompt: Optional[Union[SystemMessage, str]]
    ) -> Runnable:
        """Create a Runnable that prepends a system prompt to state messages."""
        if prompt is None:
            return RunnableCallable(
                lambda s: s.messages, name="PassthroughPrompt"
            )
        sys_msg = (
            prompt if isinstance(prompt, SystemMessage)
            else SystemMessage(content=prompt)
        )
        return RunnableCallable(
            lambda s: [sys_msg] + list(s.messages), name="SystemPrompt"
        )

    # ------------------------------------------------------------------
    # Routing helpers
    # ------------------------------------------------------------------

    def _route_next_action(
        self, state: state_mod.AgentState
    ) -> Literal["tool_executor", "done"]:
        """
        Conditional edge: route to tool execution or signal completion.
        """
        last = state.messages[-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            return "tool_executor"
        return "done"

    # ------------------------------------------------------------------
    # Default node implementations
    # ------------------------------------------------------------------

    def generate_response(
        self, state: AgentState, config: RunnableConfig
    ) -> dict:
        """Default LLM node: invoke the model and return the response."""
        response = self._execute_llm_call(state=state, config=config)
        return {"messages": [response]}

    def _collect_user_query(
        self, state: state_mod.AgentState, config: RunnableConfig
    ) -> dict:
        """CLI node: prompt the user for input."""
        user_input = ""
        while not user_input:
            user_input = console.input("[bold bright_cyan]> [/bold bright_cyan] ")

        if user_input.strip().lower() in ("q", "quit"):
            console.print("[bold red]Goodbye![/bold red]")
            exit(0)

        return {"messages": [HumanMessage(content=user_input)]}

    def _transform_mcp_input(
        self, state: AgentState, config: RunnableConfig
    ) -> dict:
        """
        Adapt the incoming MCP payload (VSCode Copilot) into a conversation message.
        """
        question = state.mcp_question
        try:
            filepath = state.mcp_current_filepath
        except Exception:
            filepath = ""

        filepath = filepath or "Filepath not provided"

        prompt = (
            "You are called as a tool by another agent. "
            "Only your final output is visible to the caller.\n\n"
            f"Active file (read it before responding): {filepath}\n\n"
            f"Question:\n{question}"
        )
        return {"messages": [prompt]}

    # ------------------------------------------------------------------
    # Visualisation
    # ------------------------------------------------------------------

    def export_workflow_diagram(self) -> None:
        """Save a Mermaid-rendered PNG of the compiled graph."""
        try:
            path = f"./{self.name.lower()}_graph.png"
            self.graph.get_graph().draw_mermaid_png(output_file_path=path)
        except Exception as exc:
            print(f"Warning: graph visualisation failed: {exc}")

    # ------------------------------------------------------------------
    # Entry point (CLI)
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Launch the agent in interactive CLI mode."""
        if self.is_sub_agent:
            raise ValueError("Sub-agents cannot be launched standalone.")

        try:
            show_startup_screen()

            config = RunnableConfig(
                configurable={}, recursion_limit=RECURSION_LIMIT
            )

            from dataclasses import asdict
            initial = asdict(
                AgentState(
                    messages=[],
                    remaining_steps=RECURSION_LIMIT,
                    is_last_step=False,
                )
            )
            self.graph.invoke(initial, config=config)

        except KeyboardInterrupt:
            console.print("\n[bold red]Goodbye![/bold red]")
