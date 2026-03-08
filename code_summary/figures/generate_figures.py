#!/usr/bin/env python3
"""
Generate publication-quality figures for JUDIAgent paper.

Horizontal layout with hand-drawn aesthetic.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, PathPatch
from matplotlib.path import Path
import numpy as np
from pathlib import Path as FilePath

# =============================================================================
# Configuration - Hand-drawn style settings
# =============================================================================
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'serif'  # More academic/hand-drawn feel
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1.0

# =============================================================================
# Color Palette - Softer, more natural colors (less corporate)
# =============================================================================
COLORS = {
    'primary': '#4A6FA5',      # Muted blue
    'secondary': '#4A8C6F',    # Muted green
    'accent': '#C45C5C',       # Muted red/coral
    'neutral': '#5C6B7A',      # Blue-gray
    'light': '#F5F5F0',        # Warm off-white
    'text': '#2D3436',         # Near black
    'white': '#FFFFFF',
    'border': '#A0A0A0',       # Medium gray
    'bg_blue': '#E8EEF4',      # Light blue bg
    'bg_green': '#E8F4EE',     # Light green bg
    'bg_gray': '#F0F0F0',      # Light gray bg
}


def add_slight_variation(value, amount=0.02):
    """Add slight randomness for hand-drawn effect."""
    return value + np.random.uniform(-amount, amount)


def create_hand_drawn_box(ax, x, y, width, height, label, color, fontsize=10, 
                          text_color='white', alpha=0.95):
    """
    Create a box with subtle hand-drawn feel.
    """
    # Slightly irregular corners for hand-drawn feel
    pad = 0.015
    rounding = add_slight_variation(0.08, 0.02)
    
    box = FancyBboxPatch(
        (x - width/2 + add_slight_variation(0, pad), 
         y - height/2 + add_slight_variation(0, pad)), 
        width, height,
        boxstyle=f"round,pad=0.02,rounding_size={rounding}",
        facecolor=color, 
        edgecolor=COLORS['text'], 
        linewidth=1.2,
        alpha=alpha,
        zorder=2
    )
    ax.add_patch(box)
    
    ax.text(x, y, label, 
            ha='center', va='center', 
            fontsize=fontsize,
            color=text_color, 
            fontweight='medium', 
            zorder=3,
            linespacing=1.1)
    
    return box


def create_simple_box(ax, x, y, width, height, label, bg_color, edge_color, 
                      fontsize=9, text_color=None):
    """Create a simple annotation box."""
    if text_color is None:
        text_color = COLORS['text']
    
    box = FancyBboxPatch(
        (x - width/2, y - height/2), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        facecolor=bg_color, 
        edgecolor=edge_color, 
        linewidth=1.0,
        zorder=1
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha='center', va='center', 
            fontsize=fontsize, color=text_color)
    return box


def create_diamond(ax, x, y, size, label, color):
    """Create a diamond shape for decision nodes."""
    s = size * 0.85
    coords = np.array([
        [x, y + s],
        [x + s*0.75, y],
        [x, y - s],
        [x - s*0.75, y]
    ])
    diamond = Polygon(coords, closed=True, 
                      facecolor=color, 
                      edgecolor=COLORS['text'], 
                      linewidth=1.2, 
                      zorder=2)
    ax.add_patch(diamond)
    ax.text(x, y, label, 
            ha='center', va='center', 
            fontsize=9,
            color='white', 
            fontweight='medium', 
            zorder=3)


def draw_arrow(ax, start, end, color=None, style='-', lw=1.5, 
               connectionstyle="arc3,rad=0"):
    """Draw a clean arrow between two points."""
    if color is None:
        color = COLORS['neutral']
    
    arrow = FancyArrowPatch(
        start, end,
        arrowstyle='-|>',
        mutation_scale=12,
        color=color,
        linewidth=lw,
        connectionstyle=connectionstyle,
        zorder=1,
        linestyle=style
    )
    ax.add_patch(arrow)


def draw_curved_arrow(ax, start, end, color=None, rad=0.2, style='-'):
    """Draw a curved arrow."""
    if color is None:
        color = COLORS['neutral']
    draw_arrow(ax, start, end, color, style, 
               connectionstyle=f"arc3,rad={rad}")


# =============================================================================
# Figure 1: Agent Workflow (Horizontal)
# =============================================================================
def create_agent_workflow_figure():
    """
    Create horizontal agent workflow diagram.
    Flow: Query -> Retrieve -> Generate -> Validate -> Output
    """
    fig, ax = plt.subplots(1, 1, figsize=(13, 5.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    ax.text(6.5, 5.5, 'JUDIAgent Workflow', 
            fontsize=17, fontweight='bold',
            ha='center', va='center', 
            color=COLORS['text'])
    
    # Main flow boxes (left to right)
    y_main = 3.5
    box_w, box_h = 2.0, 0.85
    
    # Positions
    x_query = 1.3
    x_retrieve = 3.8
    x_generate = 6.3
    x_validate = 8.8
    x_decision = 10.6
    x_output = 11.9
    
    create_hand_drawn_box(ax, x_query, y_main, box_w, box_h, 
                          'User Query', COLORS['primary'], fontsize=12)
    create_hand_drawn_box(ax, x_retrieve, y_main, box_w, box_h, 
                          'Retrieve\nExamples', COLORS['secondary'], fontsize=12)
    create_hand_drawn_box(ax, x_generate, y_main, box_w, box_h, 
                          'Generate\nCode', COLORS['primary'], fontsize=12)
    create_hand_drawn_box(ax, x_validate, y_main, box_w, box_h, 
                          'Validate', COLORS['accent'], fontsize=12)
    
    # Decision diamond
    create_diamond(ax, x_decision, y_main, 0.5, 'OK?', COLORS['neutral'])
    
    # Output box
    create_hand_drawn_box(ax, x_output, y_main + 0.9, 1.4, 0.7, 
                          'Output', COLORS['secondary'], fontsize=12)
    
    # Refine box (below)
    y_refine = 1.6
    create_hand_drawn_box(ax, x_decision, y_refine, 1.6, 0.7, 
                          'Refine', COLORS['neutral'], fontsize=12)
    
    # Main flow arrows
    draw_arrow(ax, (x_query + 1.0, y_main), (x_retrieve - 1.0, y_main))
    draw_arrow(ax, (x_retrieve + 1.0, y_main), (x_generate - 1.0, y_main))
    draw_arrow(ax, (x_generate + 1.0, y_main), (x_validate - 1.0, y_main))
    draw_arrow(ax, (x_validate + 1.0, y_main), (x_decision - 0.42, y_main))
    
    # Decision to Output (Yes)
    draw_curved_arrow(ax, (x_decision + 0.35, y_main + 0.35), 
                      (x_output - 0.7, y_main + 0.75), rad=0.3)
    ax.text(x_output - 0.35, y_main + 0.4, 'Yes', fontsize=11, 
            color=COLORS['text'])
    
    # Decision to Refine (No)
    draw_arrow(ax, (x_decision, y_main - 0.45), (x_decision, y_refine + 0.35))
    ax.text(x_decision + 0.28, y_main - 0.8, 'No', fontsize=11, 
            color=COLORS['text'])
    
    # Feedback loop from Refine back to Generate
    ax.annotate('', 
                xy=(x_generate, y_main - 0.43), 
                xytext=(x_decision - 0.8, y_refine),
                arrowprops=dict(arrowstyle='-|>', 
                               color=COLORS['neutral'], 
                               connectionstyle='arc3,rad=0.3', 
                               lw=1.5,
                               linestyle='--'))
    
    # Vector Store annotation (near Retrieve)
    create_simple_box(ax, x_retrieve, y_main + 1.2, 1.3, 0.55, 
                      'Vector\nStore', COLORS['light'], COLORS['border'], 
                      fontsize=10)
    draw_arrow(ax, (x_retrieve, y_main + 0.43), (x_retrieve, y_main + 0.92),
               color=COLORS['border'])
    
    # Legend at bottom
    legend_y = 0.6
    legend_items = [
        (COLORS['primary'], 'Input/Generate'),
        (COLORS['secondary'], 'Retrieve/Output'),
        (COLORS['accent'], 'Validate'),
    ]
    for i, (color, label) in enumerate(legend_items):
        x = 3.2 + i * 2.8
        ax.add_patch(FancyBboxPatch((x-0.15, legend_y-0.14), 0.28, 0.28,
                                    boxstyle="round,pad=0.01",
                                    facecolor=color, edgecolor='none'))
        ax.text(x + 0.28, legend_y, label, fontsize=11, va='center', 
                color=COLORS['text'])
    
    plt.tight_layout()
    return fig


# =============================================================================
# Figure 2: System Architecture (Horizontal)
# =============================================================================
def create_system_architecture_figure():
    """
    Create horizontal system architecture diagram.
    Three columns: Interface -> Agent -> Julia Runtime
    """
    fig, ax = plt.subplots(1, 1, figsize=(13, 5.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    ax.text(6.5, 5.5, 'JUDIAgent Architecture', 
            fontsize=14, fontweight='bold',
            ha='center', va='center', 
            color=COLORS['text'])
    
    # Layer positions (left to right)
    layer_y = 2.8
    layer_h = 3.8
    
    # =================================
    # Column 1: Interface Layer
    # =================================
    layer1_x = 1.8
    layer1_w = 2.8
    
    layer1_bg = FancyBboxPatch((layer1_x - layer1_w/2, layer_y - layer_h/2), 
                                layer1_w, layer_h, 
                                boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor=COLORS['bg_blue'], 
                                edgecolor=COLORS['primary'], 
                                linewidth=1.5)
    ax.add_patch(layer1_bg)
    ax.text(layer1_x, layer_y + 1.6, 'Interface\nLayer', fontsize=10, 
            fontweight='bold', ha='center', color=COLORS['primary'])
    
    # Interface boxes
    interfaces = ['CLI', 'REST API', 'VSCode']
    for i, name in enumerate(interfaces):
        y = layer_y + 0.5 - i * 0.9
        create_hand_drawn_box(ax, layer1_x, y, 2.0, 0.65, name, 
                              COLORS['primary'], fontsize=9)
    
    # =================================
    # Column 2: Agent Layer
    # =================================
    layer2_x = 6.5
    layer2_w = 4.5
    
    layer2_bg = FancyBboxPatch((layer2_x - layer2_w/2, layer_y - layer_h/2), 
                                layer2_w, layer_h, 
                                boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor=COLORS['bg_green'], 
                                edgecolor=COLORS['secondary'], 
                                linewidth=1.5)
    ax.add_patch(layer2_bg)
    ax.text(layer2_x, layer_y + 1.6, 'Agent Layer\n(LangGraph)', fontsize=10, 
            fontweight='bold', ha='center', color=COLORS['secondary'])
    
    # Agent components (2x2 grid)
    components = [('LLM', -0.9, 0.5), ('RAG', 0.9, 0.5),
                  ('Tools', -0.9, -0.5), ('Validate', 0.9, -0.5)]
    for name, dx, dy in components:
        create_hand_drawn_box(ax, layer2_x + dx, layer_y + dy, 1.4, 0.6, 
                              name, COLORS['secondary'], fontsize=9)
    
    # Arrows between components
    draw_arrow(ax, (layer2_x - 0.2, layer_y + 0.5), 
               (layer2_x + 0.2, layer_y + 0.5))
    draw_arrow(ax, (layer2_x - 0.9, layer_y + 0.2), 
               (layer2_x - 0.9, layer_y - 0.2))
    draw_arrow(ax, (layer2_x - 0.2, layer_y - 0.5), 
               (layer2_x + 0.2, layer_y - 0.5))
    
    # Config note
    ax.text(layer2_x, layer_y - 1.4, 'model="gpt-4.1"',
            fontsize=8, ha='center', color=COLORS['neutral'], 
            family='monospace',
            bbox=dict(facecolor='white', edgecolor=COLORS['border'], 
                     boxstyle='round,pad=0.2', linewidth=0.8))
    
    # =================================
    # Column 3: Julia Runtime
    # =================================
    layer3_x = 11.2
    layer3_w = 2.8
    
    layer3_bg = FancyBboxPatch((layer3_x - layer3_w/2, layer_y - layer_h/2), 
                                layer3_w, layer_h, 
                                boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor=COLORS['bg_gray'], 
                                edgecolor=COLORS['neutral'], 
                                linewidth=1.5)
    ax.add_patch(layer3_bg)
    ax.text(layer3_x, layer_y + 1.6, 'Julia\nRuntime', fontsize=10, 
            fontweight='bold', ha='center', color=COLORS['neutral'])
    
    # JUDI.jl box (enlarged to contain all text)
    judi_bg = FancyBboxPatch((layer3_x - 1.2, layer_y - 0.4), 2.4, 1.9, 
                              boxstyle="round,pad=0.02,rounding_size=0.08",
                              facecolor='white', 
                              edgecolor=COLORS['neutral'], 
                              linewidth=1.0)
    ax.add_patch(judi_bg)
    ax.text(layer3_x, layer_y + 0.65, 'JUDI.jl', fontsize=10, 
            fontweight='bold', ha='center', color=COLORS['neutral'])
    ax.text(layer3_x, layer_y + 0.2, 'Model | Geometry', fontsize=8, 
            ha='center', color=COLORS['text'])
    ax.text(layer3_x, layer_y - 0.15, 'Operators', fontsize=8, 
            ha='center', color=COLORS['text'])
    
    # Devito
    create_hand_drawn_box(ax, layer3_x, layer_y - 1.1, 2.0, 0.5, 
                          'Devito (PDE)', COLORS['neutral'], fontsize=8)
    
    # Arrows between layers
    # Interface -> Agent
    for i in range(3):
        y = layer_y + 0.5 - i * 0.9
        draw_curved_arrow(ax, (layer1_x + 1.0, y), 
                         (layer2_x - 2.25, layer_y + 0.2 - i*0.2), 
                         rad=0.1 if i == 1 else 0.15)
    
    # Agent -> Julia (with subprocess label on the arrow)
    draw_arrow(ax, (layer2_x + 2.25, layer_y), (layer3_x - 1.4, layer_y))
    ax.text((layer2_x + layer3_x)/2 + 0.4, layer_y + 0.25, 'subprocess', 
            fontsize=8, color=COLORS['neutral'], ha='center',
            bbox=dict(facecolor='white', edgecolor='none', pad=1))
    
    plt.tight_layout()
    return fig


# =============================================================================
# Figure 3: Wave Design Loop (Horizontal)
# =============================================================================
def create_wave_design_loop_figure():
    """
    Create horizontal wave-equation design loop diagram.
    Circular loop: Configure -> Simulate -> Evaluate -> Analyze -> Configure
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 7)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    ax.text(6, 6.5, 'Wave-Equation Design Loop', 
            fontsize=18, fontweight='bold',
            ha='center', va='center', 
            color=COLORS['text'])
    
    # Central wave equation box
    center_x, center_y = 6, 3.3
    eq_w, eq_h = 3.2, 1.4
    
    eq_bg = FancyBboxPatch((center_x - eq_w/2, center_y - eq_h/2), eq_w, eq_h, 
                            boxstyle="round,pad=0.02,rounding_size=0.1",
                            facecolor=COLORS['light'], 
                            edgecolor=COLORS['border'],
                            linewidth=1.2)
    ax.add_patch(eq_bg)
    ax.text(center_x, center_y + 0.35, 'Wave Equation', fontsize=13, 
            fontweight='bold', ha='center', color=COLORS['text'])
    ax.text(center_x, center_y - 0.22, 
            r'$\nabla^2 u - \frac{1}{c^2}\frac{\partial^2 u}{\partial t^2} = q$',
            fontsize=14, ha='center', color=COLORS['text'])
    
    # Four boxes arranged around the center (more vertical spacing)
    box_w, box_h = 2.4, 1.0
    
    # Top: Configure (Agent) - moved higher
    x_config = center_x
    y_config = center_y + 2.3
    create_hand_drawn_box(ax, x_config, y_config, box_w, box_h, 
                          'Configure\n(sources, receivers)', 
                          COLORS['secondary'], fontsize=13)
    
    # Right: Simulate (JUDI)
    x_sim = center_x + 3.3
    y_sim = center_y
    create_hand_drawn_box(ax, x_sim, y_sim, box_w, box_h, 
                          'JUDI\nSimulates', 
                          COLORS['neutral'], fontsize=13)
    
    # Bottom: Evaluate - moved lower
    x_eval = center_x
    y_eval = center_y - 2.35
    create_hand_drawn_box(ax, x_eval, y_eval, box_w, box_h, 
                          'Evaluate\n(resolution, SNR)', 
                          COLORS['accent'], fontsize=13)
    
    # Left: Analyze (Agent)
    x_analyze = center_x - 3.3
    y_analyze = center_y
    create_hand_drawn_box(ax, x_analyze, y_analyze, box_w, box_h, 
                          'Agent\nAnalyzes', 
                          COLORS['secondary'], fontsize=13)
    
    # Clear, prominent arrows forming the loop (clockwise)
    arrow_color = COLORS['text']
    arrow_lw = 2.0
    
    # Config -> Simulate (top-right)
    ax.annotate('', xy=(x_sim - 0.5, y_sim + 0.5), 
                xytext=(x_config + 0.85, y_config - 0.5),
                arrowprops=dict(arrowstyle='-|>', color=arrow_color, 
                               lw=arrow_lw, connectionstyle='arc3,rad=-0.3'))
    
    # Simulate -> Evaluate (right-bottom)
    ax.annotate('', xy=(x_eval + 0.85, y_eval + 0.5), 
                xytext=(x_sim - 0.5, y_sim - 0.5),
                arrowprops=dict(arrowstyle='-|>', color=arrow_color, 
                               lw=arrow_lw, connectionstyle='arc3,rad=-0.3'))
    
    # Evaluate -> Analyze (bottom-left)
    ax.annotate('', xy=(x_analyze + 0.5, y_analyze - 0.5), 
                xytext=(x_eval - 0.85, y_eval + 0.5),
                arrowprops=dict(arrowstyle='-|>', color=arrow_color, 
                               lw=arrow_lw, connectionstyle='arc3,rad=-0.3'))
    
    # Analyze -> Config (left-top)
    ax.annotate('', xy=(x_config - 0.85, y_config - 0.5), 
                xytext=(x_analyze + 0.5, y_analyze + 0.5),
                arrowprops=dict(arrowstyle='-|>', color=arrow_color, 
                               lw=arrow_lw, connectionstyle='arc3,rad=-0.3'))
    
    # Side annotations (moved closer to center)
    # Design space (left)
    ax.text(1.6, center_y + 1.8, 'Design\nSpace', fontsize=13, 
            ha='center', va='center', color=COLORS['neutral'],
            bbox=dict(facecolor=COLORS['light'], 
                     edgecolor=COLORS['border'],
                     boxstyle='round,pad=0.2', linewidth=0.8))
    ax.text(1.6, center_y + 1.0, r'$\theta$', fontsize=20, 
            ha='center', color=COLORS['text'])
    
    # Data space (right)
    ax.text(10.4, center_y + 1.8, 'Data', fontsize=13,
            ha='center', va='center', color=COLORS['neutral'],
            bbox=dict(facecolor=COLORS['light'], 
                     edgecolor=COLORS['border'],
                     boxstyle='round,pad=0.2', linewidth=0.8))
    ax.text(10.4, center_y + 1.0, r'$d_{obs}$', fontsize=20, 
            ha='center', color=COLORS['text'])
    
    # Bottom text
    ax.text(6, 0.2, r'Objective: $\theta^* = \arg\max\, I(\theta)$',
            fontsize=13, ha='center', color=COLORS['text'])
    
    # Legend
    legend_y = -0.25
    legend_items = [
        (COLORS['secondary'], 'Agent'),
        (COLORS['neutral'], 'Simulation'),
        (COLORS['accent'], 'Evaluation'),
    ]
    for i, (color, label) in enumerate(legend_items):
        x = 3.5 + i * 2.4
        ax.add_patch(FancyBboxPatch((x-0.15, legend_y-0.12), 0.28, 0.28,
                                    boxstyle="round,pad=0.01",
                                    facecolor=color, edgecolor='none'))
        ax.text(x + 0.28, legend_y, label, fontsize=12, va='center', 
                color=COLORS['text'])
    
    plt.tight_layout()
    return fig


# =============================================================================
# Main Execution
# =============================================================================
def main():
    """Generate all three figures and save as PNG files."""
    output_dir = FilePath(__file__).parent
    
    print("Generating JUDIAgent figures (horizontal layout)...")
    print("=" * 50)
    
    # Figure 1: Agent Workflow
    print("  [1/3] Creating agent_workflow.png...")
    fig1 = create_agent_workflow_figure()
    fig1.savefig(output_dir / 'agent_workflow.png', 
                 bbox_inches='tight', 
                 facecolor='white', 
                 edgecolor='none',
                 pad_inches=0.15)
    plt.close(fig1)
    print("        Done")
    
    # Figure 2: System Architecture
    print("  [2/3] Creating system_architecture.png...")
    fig2 = create_system_architecture_figure()
    fig2.savefig(output_dir / 'system_architecture.png', 
                 bbox_inches='tight', 
                 facecolor='white', 
                 edgecolor='none',
                 pad_inches=0.15)
    plt.close(fig2)
    print("        Done")
    
    # Figure 3: Wave Design Loop
    print("  [3/3] Creating wave_design_loop.png...")
    fig3 = create_wave_design_loop_figure()
    fig3.savefig(output_dir / 'wave_design_loop.png', 
                 bbox_inches='tight', 
                 facecolor='white', 
                 edgecolor='none',
                 pad_inches=0.15)
    plt.close(fig3)
    print("        Done")
    
    print("=" * 50)
    print(f"All figures saved to: {output_dir}")


if __name__ == '__main__':
    main()
