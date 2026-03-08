"""
Global State and Singletons for JUDIAgent.

This module contains globally accessible objects that are shared across
the application. Currently provides:

- console: Shared Rich Console instance for consistent terminal output

Warning:
    The store_retrieved_context variable is a temporary workaround for
    passing context between nodes. This should be refactored to use
    proper state management through LangGraph's state schema.

Usage:
    from judiagent.globals import console
    console.print("[green]Success![/green]")
"""

from rich.console import Console


# Shared console instance for all terminal output
# Using a single instance ensures consistent styling and avoids conflicts
console = Console()


# WARNING: Global mutable state - should be refactored
# This is used to temporarily store retrieved context for debugging/logging
# TODO: Move this to proper LangGraph state management
store_retrieved_context: str = ""
