"""
CLI Utilities for JUDIAgent.

This module provides utility functions for the command-line interface,
including console output formatting, streaming display, and user interaction.

Key Components:
- print_to_console: Display formatted text in panels
- stream_to_console: Stream LLM responses with live updates
- show_startup_screen: Display the branded welcome screen
- edit_document_content: Interactive content editing
- save_code_to_file: Save generated code to files

Dependencies:
- rich: For terminal formatting and live updates
- langchain_core: For message handling
"""

import time
from typing import List, Optional

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from rich.align import Align
from rich.console import Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from judiagent.globals import console
from judiagent.state import JuliaCodeBlock


def quick_select(
    options: list[tuple[str, str]],  # (key, label)
    prompt: str = "Choice",
    default: str = "",
) -> str:
    """
    Quick inline selection for rapid choices (e.g., document review).
    
    Displays options inline with amber/gold theme and returns the selected key.
    
    Args:
        options: List of (key, label) tuples
        prompt: Prompt text
        default: Default option key
    
    Returns:
        The selected option key
    """
    valid_keys = [k for k, _ in options]
    opts_display = " [dim]│[/dim] ".join(
        f"[bold gold1]({k})[/bold gold1][bright_white]{label}[/bright_white]" 
        for k, label in options
    )
    console.print(f"\n{opts_display}")
    
    while True:
        choice = console.input("[bold gold1]>[/bold gold1] ").strip().lower()
        
        if not choice and default:
            return default
        if choice in valid_keys:
            return choice
        
        console.print(f"[bold orange1]  >> Invalid! Enter:[/bold orange1] [bright_white]{', '.join(valid_keys)}[/bright_white]")


def menu_select(
    title: str,
    options: list[tuple[str, str, str]],  # (key, label, icon)
    default: str = "1",
) -> str:
    """
    Display a styled menu with options and return the user's choice.
    
    Features a distinctive amber/gold design with icons and clear key bindings.
    
    Args:
        title: The menu title/question
        options: List of (key, label, icon) tuples
        default: Default option key
    
    Returns:
        The selected option key
    
    Example:
        >>> choice = menu_select(
        ...     "What would you like to do?",
        ...     [("1", "Continue", "▶"), ("2", "Edit", "✏"), ("q", "Quit", "×")],
        ...     default="1"
        ... )
    """
    import rich.box as box
    
    # Build the menu display - left-aligned with consistent spacing
    menu_lines = []
    valid_choices = []
    
    # Define emoji icons with spacing adjustments for alignment
    # Some emojis (like ✏️, ⏭️) display narrower in terminals, so we add extra space
    icons_map = {
        "1": ("🔍", ""),   # (emoji, extra_space)
        "2": ("💬", ""),
        "3": ("✏️ ", ""),  # extra space after emoji to compensate width
        "4": ("⏭️ ", ""),  # extra space after emoji to compensate width
        "y": ("✓", " "),
        "n": ("✗", " "),
        "q": ("🚪", "")
    }
    
    for key, label, icon in options:
        valid_choices.append(key)
        # Get emoji icon with spacing (fallback to provided icon or default)
        emoji_info = icons_map.get(key, (icon if icon else "▸", " "))
        emoji, extra_space = emoji_info if isinstance(emoji_info, tuple) else (emoji_info, "")
        # Fixed-width format: emoji [key] label (aligned numbers with consistent spacing)
        menu_lines.append(f"    {emoji}{extra_space} [bright_white][{key}][/bright_white] {label}")
    
    menu_text = "\n".join(menu_lines)
    
    # Create a styled panel for the menu with distinctive border
    panel_content = Text.from_markup(f"[bold bright_yellow]{title}[/bold bright_yellow]\n\n{menu_text}")
    
    panel = Panel(
        panel_content,
        border_style="dark_orange",
        box=box.ROUNDED,
        padding=(0, 2),
    )
    console.print(panel)
    
    # Get user input with validation
    while True:
        choice = console.input("[bold gold1]>[/bold gold1] ").strip()
        
        if not choice:
            return default
        if choice in valid_choices:
            return choice
        
        # Show prominent error message (use ASCII arrow instead of emoji)
        console.print(f"[bold orange1]  >> Invalid! Enter:[/bold orange1] [bright_white]{', '.join(valid_choices)}[/bright_white]")


def print_to_console(
    text: str,
    title: str = "Agent",
    border_style: str = "medium_purple3",
    panel_kwargs: dict = {},
    with_markdown: bool = True,
):
    """
    Print formatted text to the console with a styled panel.

    Uses JUDIAgent's distinctive amber/purple theme. Agent responses
    use purple borders, tools use orange.

    Args:
        text: The text content to display
        title: Panel title (default: "Agent")
        border_style: Rich style for the panel border (default: purple)
        panel_kwargs: Additional keyword arguments for Panel
        with_markdown: Whether to render text as markdown

    Example:
        >>> print_to_console("# Hello World", title="Greeting")
        ╭─ Greeting ───────────────────────────╮
        │ # Hello World                        │
        ╰──────────────────────────────────────╯
    """
    import rich.box as box
    
    panel_kwargs = panel_kwargs.copy()  # Don't mutate original
    
    if border_style:
        panel_kwargs["border_style"] = border_style
    if title:
        # Style the title with amber
        panel_kwargs["title"] = f"[bold bright_yellow]{title}[/bold bright_yellow]"
    
    # Use rounded box for softer appearance
    if "box" not in panel_kwargs:
        panel_kwargs["box"] = box.ROUNDED

    content = Markdown(text) if with_markdown else text
    console.print(Panel.fit(content, **panel_kwargs))


def _retry_with_exponential_backoff(
    func,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    error_msg_prefix: str = "Rate limit error",
) -> AIMessage:
    """
    Retry a function with exponential backoff on rate limit errors.

    Implements a robust retry mechanism for API calls that may encounter
    rate limiting. Automatically extracts wait times from error messages
    when available.
    
    Args:
        func: The function to retry (should return AIMessage)
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds for exponential backoff
        max_delay: Maximum delay cap in seconds
        error_msg_prefix: Prefix for log messages
        
    Returns:
        AIMessage: The successful result from the function call
        
    Raises:
        RuntimeError: If all retries are exhausted without success
        
    Note:
        The backoff formula is: delay = min(base_delay * 2^attempt, max_delay)
        Wait times extracted from error messages take precedence.
    """
    import re
    
    last_exception: Optional[Exception] = None
    
    for attempt in range(max_retries):
        try:
            result = func()
            if result is not None:
                return result
            raise RuntimeError("Function returned None unexpectedly")
        except Exception as e:
            last_exception = e
            error_type = type(e).__name__
            error_str = str(e)
            
            # Detect rate limit errors from various API providers
            is_rate_limit = (
                "RateLimitError" in error_type
                or "rate_limit" in error_str.lower()
                or "429" in error_str
                or "Rate limit" in error_str
            )
            
            if not is_rate_limit:
                # Not a rate limit error - fail immediately
                raise
            
            # Calculate wait time with exponential backoff
            wait_time = base_delay * (2 ** attempt)
            
            # Try to extract exact wait time from error message
            # Matches patterns like "try again in 112ms" or "try again in 5 seconds"
            wait_match = re.search(
                r"try again in (\d+)(ms|s|seconds?)", 
                error_str, 
                re.IGNORECASE
            )
            if wait_match:
                wait_value = float(wait_match.group(1))
                unit = wait_match.group(2).lower()
                if "ms" in unit:
                    wait_time = wait_value / 1000.0
                else:
                    wait_time = wait_value
                # Add 10% buffer to extracted wait time
                wait_time = wait_time * 1.1
            
            wait_time = min(wait_time, max_delay)
            
            if attempt < max_retries - 1:
                console.print(
                    f"[yellow]⚠  {error_msg_prefix}: {error_type}[/yellow]"
                )
                console.print(
                    f"[yellow]   Retrying in {wait_time:.1f}s... "
                    f"(attempt {attempt + 1}/{max_retries})[/yellow]"
                )
                time.sleep(wait_time)
            else:
                console.print(
                    f"[red]✗ {error_msg_prefix}: "
                    f"Maximum retries ({max_retries}) exceeded[/red]"
                )
                raise
    
    # Should not reach here, but satisfies type checker
    raise RuntimeError(f"All {max_retries} retries exhausted") from last_exception


def stream_to_console(
    llm,
    message_list: List,
    config: RunnableConfig,
    title: Optional[str] = "Agent",
    border_style: str = "medium_purple3",
    panel_kwargs: dict = {},
    with_markdown: bool = True,
) -> AIMessage:
    """
    Stream LLM output to the console with live updates.

    Displays LLM responses in real-time as they are generated,
    using JUDIAgent's distinctive amber/purple theme.

    Args:
        llm: The language model to stream from
        message_list: List of messages to send to the LLM
        config: LangChain runnable configuration
        title: Optional panel title (default: "Agent")
        border_style: Rich style for panel border (default: purple)
        panel_kwargs: Additional panel customization
        with_markdown: Whether to render as markdown

    Returns:
        AIMessage: The complete response message

    Raises:
        ValueError: If no content is received from the model
    """
    import rich.box as box
    
    ai_message: Optional[AIMessage] = None
    streamed_text: str = ""
    panel_kwargs = panel_kwargs.copy()  # Prevent mutation of original

    if border_style:
        panel_kwargs["border_style"] = border_style
    if title:
        panel_kwargs["title"] = f"[bold bright_yellow]{title}[/bold bright_yellow]"
    if "box" not in panel_kwargs:
        panel_kwargs["box"] = box.ROUNDED

    def _stream_and_process():
        """Inner streaming function with retry capability."""
        nonlocal ai_message, streamed_text
        
        ai_message = None
        streamed_text = ""
        
        # Initialize the stream from the LLM
        stream = llm.stream(message_list, config=config)

        for chunk in stream:
            if chunk.content:
                streamed_text += chunk.content
                ai_message = chunk if ai_message is None else ai_message + chunk

                # Start live display once we have content
                with Live(
                    Panel(
                        Markdown(streamed_text) if with_markdown else streamed_text,
                        **panel_kwargs,
                    ),
                    console=console,
                    refresh_per_second=4,
                ) as live:
                    # Process remaining chunks within live context
                    for chunk in stream:
                        ai_message += chunk
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

    # Execute with automatic retry on rate limits
    return _retry_with_exponential_backoff(
        _stream_and_process,
        max_retries=5,
        base_delay=1.0,
        max_delay=60.0,
        error_msg_prefix="API rate limit exceeded during streaming",
    )


def show_startup_screen():
    """
    Display the JUDIAgent branded startup screen.

    Features a distinctive amber/gold theme inspired by seismic
    visualization with geological motifs. Full terminal width.
    """
    import rich.box as box
    
    # Large ASCII art title
    ascii_art = Text.from_markup(
        "[bold gold1]"
        "        ██╗██╗   ██╗██████╗ ██╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗\n"
        "        ██║██║   ██║██╔══██╗██║    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝\n"
        "        ██║██║   ██║██║  ██║██║    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   \n"
        "   ██   ██║██║   ██║██║  ██║██║    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   \n"
        "   ╚█████╔╝╚██████╔╝██████╔╝██║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   \n"
        "    ╚════╝  ╚═════╝ ╚═════╝ ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   \n"
        "[/bold gold1]"
    )

    # Seismic wave motif
    wave = Text.from_markup(
        "[dim orange1]"
        "   ∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿\n"
        "[/dim orange1]"
    )

    # Tagline
    tagline = Text(
        "Seismic Intelligence for JUDI.jl",
        justify="center",
        style="italic bright_yellow",
    )

    # Subsurface visualization - wider
    layer_art = Text.from_markup(
        "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]\n"
        "[orange1]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[/orange1]\n"
        "[dark_orange]▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒[/dark_orange]\n"
        "[orange_red1]░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░[/orange_red1]"
    )

    # Usage instructions
    info_text = Text.from_markup(
        "\n[gold1]❯[/gold1] [bright_white]Type your query[/bright_white] [dim]or[/dim] [bright_white]'q'[/bright_white] [dim]to quit[/dim]"
    )

    # Compose the content
    content = Group(
        Align.center(ascii_art),
        Align.center(wave),
        Align.center(tagline),
        Align.center(layer_art),
        Align.center(info_text),
    )

    # Create and display the panel - use full width
    panel = Panel(
        content,
        border_style="gold1",
        box=box.DOUBLE,
        padding=(1, 2),
        expand=True,  # Full terminal width
    )
    console.print(panel)
    console.print()  # Add spacing


def edit_document_content(original_content: str, edit_julia_file: bool = False) -> str:
    """
    Allow user to edit document content using an external editor.

    Opens the content in the user's preferred editor (from $EDITOR
    environment variable, defaulting to vim) and returns the edited
    content.

    Args:
        original_content: The initial content to edit
        edit_julia_file: If True, uses .jl extension; otherwise .md

    Returns:
        str: The edited content, or original if editing fails

    Note:
        Set the EDITOR environment variable to use a different editor:
        export EDITOR=nano
    """
    import os
    import subprocess
    import tempfile

    file_suffix = ".jl" if edit_julia_file else ".md"
    
    try:
        # Create temporary file with the content
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=file_suffix, delete=False
        ) as f:
            f.write(original_content)
            f.flush()

            # Get editor from environment or default to vim
            editor = os.environ.get("EDITOR", "vim")
            
            try:
                # Open editor and wait for completion
                subprocess.run([editor, f.name], check=True)

                # Read the edited content
                with open(f.name, "r") as edited_file:
                    edited_content = edited_file.read()

                os.unlink(f.name)
                return edited_content

            except subprocess.CalledProcessError:
                console.print(
                    f"[red]Error opening editor '{editor}'. "
                    f"Using original content.[/red]"
                )
                os.unlink(f.name)
                return original_content
                
            except FileNotFoundError:
                console.print(
                    f"[red]Editor '{editor}' not found. "
                    f"Try setting EDITOR environment variable.[/red]"
                )
                os.unlink(f.name)
                return original_content

    except Exception as e:
        console.print(f"[red]Error with external editor: {e}[/red]")
        return original_content


def save_code_to_file(code_block: JuliaCodeBlock) -> None:
    """
    Save a code block to a Julia file with user confirmation.

    Prompts the user for a filename and handles file existence
    checks with overwrite confirmation.

    Args:
        code_block: The CodeBlock object containing code to save

    Note:
        - Automatically appends .jl extension if missing
        - Prompts for confirmation before overwriting existing files
        - Combines imports and code into a single file
    """
    import os

    console.print("\n[bold bright_cyan]Save Code to File[/bold bright_cyan]")

    # Prompt for filename with default
    default_filename = "generated_code.jl"
    filename = Prompt.ask("Enter filename", default=default_filename)

    # Ensure Julia extension
    if not filename.endswith(".jl"):
        filename += ".jl"

    try:
        # Check for existing file
        if os.path.exists(filename):
            overwrite = Prompt.ask(
                f"File '{filename}' exists. Overwrite?",
                choices=["y", "n"],
                default="n",
            )
            if overwrite.lower() != "y":
                console.print("[yellow]⚠ File save cancelled[/yellow]")
                return

        # Write the code to file
        with open(filename, "w") as f:
            if code_block.imports:
                f.write(code_block.imports + "\n\n")
            f.write(code_block.body)

        console.print(f"[green]✓ Code saved to '{filename}'[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error saving file: {str(e)}[/red]")
