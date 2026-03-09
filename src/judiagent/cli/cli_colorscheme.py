"""
CLI color scheme for JUDIAgent.

The current theme uses a cooler seismic-console palette: cyan, steel blue,
slate, and signal orange. The goal is to give JUDIAgent a visual identity
that feels distinct from the older amber-heavy styling.
"""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class ColorScheme:
    """
    Immutable color scheme configuration for CLI components.
    
    JUDIAgent uses a unique amber/purple theme inspired by seismic
    colorscales and geological visualization.
    
    Attributes:
        normal: Default text color for regular output
        primary: Primary accent color for main UI elements
        secondary: Secondary color for supporting elements
        error: Color for error messages and failures
        success: Color for success confirmations
        warning: Color for warning messages
        message: Color for AI/system messages
        highlight: Color for emphasized content
        muted: Color for less important text
    """
    # Core colors
    normal: str = "bright_cyan"
    primary: str = "cyan"
    secondary: str = "slate_blue1"
    
    # Status colors
    error: str = "bright_red"
    success: str = "green3"
    warning: str = "orange1"
    
    # UI element colors
    message: str = "steel_blue3"
    agent_border: str = "deep_sky_blue4"
    highlight: str = "bright_white"
    muted: str = "grey70"
    
    # Interaction colors
    human_interaction: str = "bright_cyan"
    tool_border: str = "dark_orange"


# Global color scheme instance - can be customized by users
colorscheme = ColorScheme()
