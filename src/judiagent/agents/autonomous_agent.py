"""
Autonomous ReAct agent for JUDI.jl.

Implements a Reasoning + Acting loop: the LLM reasons about the task,
selects from a rich toolkit (code execution, linting, file I/O, RAG,
terminal commands), observes the result, and repeats until the task is
complete.  This is the more capable agent variant, recommended for
larger LLMs and open-ended / Copilot-style interactions.
"""

from __future__ import annotations

from typing import Any, Callable, Sequence, Union

from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_node import ToolNode

from judiagent.agents.agent_base import AgentCore
from judiagent.configuration import BaseConfiguration, cli_mode, mcp_mode
from judiagent.core.julia_code import parse_julia_code_block
from judiagent.core.messages import get_message_text
from judiagent.state import AgentState, MCPInputState, MCPOutputState
from judiagent.tools import (
    execute_julia_snippet,
    execute_shell_command,
    fetch_working_directory,
    lint_julia_code,
    list_files_in_directory,
    lookup_function_docs,
    read_from_file,
    search_codebase,
    search_imagegather_examples,
    search_judi_examples,
    write_to_file,
)


class ReActAgent(AgentCore):
    """
    Tool-augmented autonomous agent following a ReAct (Reason + Act) loop.

    Graph topology::

        [user_input] → llm ⇄ tool_executor → llm → ... → [user_input | END]
    """

    def __init__(
        self,
        tools: Sequence[Union[BaseTool, Callable, dict[str, Any]]] | ToolNode | None = None,
        stream_output: bool = True,
    ):
        if tools is None:
            tools = []

        super().__init__(
            tools=tools,
            name="ReActAgent",
            display_name="Agent",
            stream_output=stream_output,
        )
        self.has_user_feedback = False

    # ------------------------------------------------------------------
    # Workflow construction
    # ------------------------------------------------------------------

    def construct_workflow(self) -> Any:
        """Build and compile the ReAct-style LangGraph pipeline."""

        if mcp_mode:
            wf = StateGraph(
                self.workflow_state_type,
                input_schema=MCPInputState,
                output_schema=MCPOutputState,
                context_schema=BaseConfiguration,
            )
        else:
            wf = StateGraph(
                self.workflow_state_type,
                context_schema=BaseConfiguration,
            )

        # --- nodes ---
        wf.add_node("llm", self.generate_response)
        wf.add_node("tool_executor", self.tool_executor_node)

        # --- entry point ---
        if mcp_mode:
            wf.add_node("mcp_adapter", self._transform_mcp_input)
            wf.set_entry_point("mcp_adapter")
            wf.add_edge("mcp_adapter", "llm")
        elif cli_mode:
            wf.add_node("user_input", self._collect_user_query)
            wf.set_entry_point("user_input")
            wf.add_edge("user_input", "llm")
        else:
            wf.set_entry_point("llm")

        # --- edges ---
        wf.add_edge("tool_executor", "llm")
        wf.add_conditional_edges(
            "llm",
            self._route_next_action,
            {
                "tool_executor": "tool_executor",
                "done": "user_input" if cli_mode else END,
            },
        )

        return wf.compile()

    # ------------------------------------------------------------------
    # Config resolution
    # ------------------------------------------------------------------

    def resolve_model_config(
        self, config: RunnableConfig
    ) -> Union[str, LanguageModelLike]:
        return BaseConfiguration.from_runnable_config(config).autonomous_agent_model

    def resolve_prompt_config(self, config: RunnableConfig) -> str:
        return BaseConfiguration.from_runnable_config(config).autonomous_agent_prompt

    # ------------------------------------------------------------------
    # Node implementations
    # ------------------------------------------------------------------

    def generate_response(self, state: AgentState, config: RunnableConfig) -> dict:
        """Invoke LLM, extract Julia code if present, and update state."""
        response = self._execute_llm_call(state=state, config=config)

        if self._is_step_budget_exhausted(state, response):
            return {
                "messages": [
                    AIMessage(
                        id=response.id,
                        content="Sorry, need more steps to process this request.",
                    )
                ]
            }

        text = get_message_text(response)
        code_block = parse_julia_code_block(response=text)

        return {
            "messages": [response],
            "code_block": code_block,
            "error": False,
            "mcp_answer": response.content,
        }


# =====================================================================
# Default singleton
# =====================================================================

react_agent = ReActAgent(
    tools=[
        execute_julia_snippet,
        lint_julia_code,
        execute_shell_command,
        fetch_working_directory,
        list_files_in_directory,
        read_from_file,
        write_to_file,
        search_codebase,
        lookup_function_docs,
        search_judi_examples,
        search_imagegather_examples,
    ],
    stream_output=True,
)

react_agent_graph = react_agent.graph

if __name__ == "__main__":
    react_agent.run()
