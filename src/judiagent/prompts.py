"""
Backward-compatible prompt exports for JUDIAgent.

The actual prompt library now lives under ``judiagent.prompting`` so the
prompt system can evolve in smaller, domain-oriented modules.
"""

from judiagent.prompting import AGENT_PROMPT, AUTONOMOUS_AGENT_PROMPT

__all__ = ["AGENT_PROMPT", "AUTONOMOUS_AGENT_PROMPT"]
