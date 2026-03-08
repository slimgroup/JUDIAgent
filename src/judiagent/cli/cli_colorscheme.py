"""
CLI Color Scheme Configuration for JUDIAgent.

This module defines the visual theme used throughout the CLI interface.
JUDIAgent uses a distinctive amber/gold + deep purple palette inspired by
seismic data visualization - warm earth tones representing the subsurface.

Color Philosophy:
- Primary: Amber/Gold - evokes geological data, warm and distinctive
- Secondary: Deep purple/violet - complementary accent, professional
- Agent: Orchid/magenta - AI responses stand out
- Success: Emerald green
- Warning: Orange (not yellow - stays in warm palette)
- Error: Coral red
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
    # Core colors - Amber/Gold theme
    normal: str = "bright_yellow"      # Warm amber for main elements
    primary: str = "yellow"            # Gold primary accent
    secondary: str = "deep_pink"       # Deep pink/magenta secondary
    
    # Status colors
    error: str = "bright_red"          # Coral red for errors
    success: str = "green"             # Emerald for success
    warning: str = "orange1"           # Orange for warnings (warm palette)
    
    # UI element colors
    message: str = "orchid"            # Orchid/magenta for AI messages
    agent_border: str = "medium_purple3"  # Purple border for agent panels
    highlight: str = "bright_white"    # High contrast for emphasis
    muted: str = "dim white"           # De-emphasized text
    
    # Interaction colors
    human_interaction: str = "gold1"   # Gold for human input prompts
    tool_border: str = "dark_orange"   # Orange for tool panels


# Global color scheme instance - can be customized by users
colorscheme = ColorScheme()
