"""Final composed prompts for the iterative and autonomous JUDIAgent modes."""

from judiagent.prompting.domain_rules import (
    DEBUG_PLAYBOOK,
    GEOMETRY_RULES,
    GOLDEN_TEMPLATE,
    JUDI_FOUNDATIONS,
    JULIA_CODING_STANDARDS,
    JULIA_SYNTAX_WARNING,
)
from judiagent.prompting.shared import (
    CRITICAL_REMINDERS,
    GATHER_INTELLIGENCE,
    RESPONSE_APPROACH,
    ROLE_AND_IDENTITY,
    TOOL_PHILOSOPHY,
    VALIDATION_REFINEMENT,
    WORKFLOW_STRATEGY,
)
from judiagent.prompting.workspace_rules import (
    VISUALIZATION_SECTION,
    WORKSPACE_MANAGEMENT,
)

ITERATIVE_DEVELOPMENT = """
---

## Iterative Development

- Returned Julia code will be validated automatically.
- If validation fails, use the diagnostics to repair the solution.
- Go back to retrieval when the failure suggests API misuse.
"""


AUTONOMOUS_DEVELOPMENT = """
---

## Iterative Development

You have explicit execution tools:
- `execute_julia_snippet`
- `lint_julia_code`
- `execute_shell_command`

Use them to validate and refine the code before finalizing.
"""


OTHER_TOOLS_AGENT = """
---

## Other Tools

- `list_files_in_directory`
- `read_from_file`
- `write_to_file`
"""


OTHER_TOOLS_AUTONOMOUS = """
---

## Other Tools

- `list_files_in_directory`
- `read_from_file`
- `write_to_file`
- `fetch_working_directory`
"""


FINALIZATION_AGENT = """
---

## Finalization

Only write Julia code to a file when the user explicitly asks for it.
"""


AGENT_PROMPT = f"""
{ROLE_AND_IDENTITY}
{WORKFLOW_STRATEGY}
{GATHER_INTELLIGENCE}
{JUDI_FOUNDATIONS}
{GEOMETRY_RULES}
{GOLDEN_TEMPLATE}
{DEBUG_PLAYBOOK}
{ITERATIVE_DEVELOPMENT}
{VALIDATION_REFINEMENT}
{FINALIZATION_AGENT}
{OTHER_TOOLS_AGENT}
{TOOL_PHILOSOPHY}
{JULIA_CODING_STANDARDS}
{RESPONSE_APPROACH}
{JULIA_SYNTAX_WARNING}
{VISUALIZATION_SECTION}
{WORKSPACE_MANAGEMENT}
{CRITICAL_REMINDERS}
"""


AUTONOMOUS_AGENT_PROMPT = f"""
{ROLE_AND_IDENTITY}
{WORKFLOW_STRATEGY}
{GATHER_INTELLIGENCE}
{JUDI_FOUNDATIONS}
{GEOMETRY_RULES}
{GOLDEN_TEMPLATE}
{DEBUG_PLAYBOOK}
{AUTONOMOUS_DEVELOPMENT}
{VALIDATION_REFINEMENT}
{OTHER_TOOLS_AUTONOMOUS}
{TOOL_PHILOSOPHY}
{JULIA_CODING_STANDARDS}
{RESPONSE_APPROACH}
{JULIA_SYNTAX_WARNING}
{VISUALIZATION_SECTION}
{WORKSPACE_MANAGEMENT}
{CRITICAL_REMINDERS}
"""
