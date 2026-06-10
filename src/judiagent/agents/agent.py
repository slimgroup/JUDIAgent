"""
Iterative code-generation agent with dual-stage scientific evaluation.

This agent follows a generate → validate → refine loop:

1. The LLM produces Julia code based on the user query and retrieved examples.
2. The code is validated for correctness (static analysis + runtime execution).
3. Imaging/inversion-style code is also reviewed for JUDI-specific scientific completeness.
4. On failure the diagnostics are fed back and the LLM retries.
5. On success the interaction completes.

The simpler workflow makes this agent well-suited for smaller models or
focused tasks such as setting up a single JUDI simulation.
"""

from __future__ import annotations

from typing import Any, Callable, Literal, Sequence, Union

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
from judiagent.nodes import verify_code_output
from judiagent.state import AgentState, MCPInputState, MCPOutputState
from judiagent.tools import (
    list_files_in_directory,
    lookup_function_docs,
    read_from_file,
    search_codebase,
    search_imagegather_examples,
    search_judi_examples,
    write_to_file,
)


class IterativeCodeAgent(AgentCore):
    """
    Iterative JUDI.jl code agent with a dual-stage evaluation loop.

    The workflow graph is:

    .. code-block:: text

        [user_input] → llm ⇄ tool_executor → code_validator → complete
                                                   ↓ (error)
                                                  llm (retry)

    Attributes:
        has_user_feedback: whether the user has intervened in the current turn
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
            name="IterativeCodeAgent",
            display_name="Code Agent",
            stream_output=stream_output,
        )
        self.has_user_feedback = False

    # ------------------------------------------------------------------
    # Workflow construction
    # ------------------------------------------------------------------

    def construct_workflow(self) -> Any:
        """Build and compile the evaluator-optimizer LangGraph pipeline."""

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
        wf.add_node("complete", self._complete_interaction)
        wf.add_node("code_validator", verify_code_output)

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
                "done": "code_validator",
            },
        )

        wf.add_conditional_edges(
            "code_validator",
            self._handle_validation_result,
            {
                "llm": "llm",
                "complete": "complete",
            },
        )

        wf.add_edge("complete", "user_input" if cli_mode else END)

        return wf.compile()

    # ------------------------------------------------------------------
    # Config resolution
    # ------------------------------------------------------------------

    def resolve_model_config(
        self, config: RunnableConfig
    ) -> Union[str, LanguageModelLike]:
        return BaseConfiguration.from_runnable_config(config).agent_model

    def resolve_prompt_config(self, config: RunnableConfig) -> str:
        return BaseConfiguration.from_runnable_config(config).agent_prompt

    # ------------------------------------------------------------------
    # Node implementations
    # ------------------------------------------------------------------

    def generate_response(self, state: AgentState, config: RunnableConfig) -> dict:
        """Invoke the LLM, extract any Julia code block, and update state."""
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
        }

    def _complete_interaction(
        self, state: AgentState, config: RunnableConfig
    ) -> dict:
        """Terminal node: persist validated artifacts and signal completion."""
        from judiagent.cli import colorscheme, print_to_console
        from judiagent.configuration import BaseConfiguration, cli_mode
        from judiagent.core.run_artifacts import persist_validated_run

        saved_note = ""
        code = state.code_block.to_string(omit_if_empty=True)
        if code:
            configuration = BaseConfiguration.from_runnable_config(config)
            script_path, metadata_path = persist_validated_run(
                base_directory=".",
                messages=state.messages,
                code=code,
                agent_mode="iterative",
                model_name=configuration.agent_model,
            )
            saved_note = (
                f"\n\nSaved validated script: {script_path}"
                f"\nSaved run metadata: {metadata_path}"
            )

        if cli_mode:
            print_to_console(
                text=(
                    "Code validated successfully!"
                    f"{saved_note}\n\n"
                    "You can:\n"
                    "- Ask a new question\n"
                    "- Request modifications to the code\n"
                    "- Ask for visualisation / plotting\n"
                    "- Type **'q'** to quit"
                ),
                title="Ready",
                border_style=colorscheme.success,
            )
        return {}
    @staticmethod
    def _handle_validation_result(
        state: AgentState, config: RunnableConfig
    ) -> Literal["llm", "complete"]:
        """Route after code validation: retry on error, complete on success."""
        return "llm" if state.error else "complete"


# =====================================================================
# Default singleton
# =====================================================================

iterative_agent = IterativeCodeAgent(
    tools=[
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

iterative_agent_graph = iterative_agent.graph

if __name__ == "__main__":
    iterative_agent.run()
