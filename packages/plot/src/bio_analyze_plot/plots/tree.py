from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from Bio import Phylo

from .base import BasePlot, save_plot

def _draw_circular(
    tree,
    axes,
    show_confidence=True,
    branch_thickness=1.0,
    font_size=10,
    branch_color="black",
    label_offset_scale=0.05,
    label_bbox_alpha=0.65,
):
    """
    Custom helper function to draw a circular tree using Matplotlib, 
    as Bio.Phylo doesn't natively support circular layout out-of-the-box.
    """
    # 1. Calculate depths (radii) and number of leaves (for angles)
    depths = tree.depths()
    max_depth = max(depths.values())
    
    # Give all clades an angular position
    terminals = tree.get_terminals()
    num_terminals = len(terminals)
    label_offset = max_depth * label_offset_scale
    
    # 2. Assign angles to each leaf
    angles = {}
    for i, leaf in enumerate(terminals):
        angles[leaf] = (i / num_terminals) * 2 * np.pi
        
    # 3. Calculate internal node angles by averaging children's angles
    for node in reversed(list(tree.find_clades(order="level"))):
        if node not in angles:
            children = node.clades
            if children:
                child_angles = [angles[child] for child in children]
                angles[node] = np.mean(child_angles)
            else:
                angles[node] = 0

    # 4. Plot lines
    for node in tree.find_clades(order="level"):
        r1 = depths[node]
        theta1 = angles[node]
        
        # Plot children
        for child in node.clades:
            r2 = depths[child]
            theta2 = angles[child]
            
            # Radial line (from node radius to child radius, at child's angle)
            axes.plot([theta2, theta2], [r1, r2], color=branch_color, lw=branch_thickness, 
                      solid_capstyle='round', antialiased=True)
            
            # Arc line (connecting children at node's radius)
            # Create a smooth arc between theta1 and theta2 at radius r1
            arc_angles = np.linspace(min(theta1, theta2), max(theta1, theta2), 100)
            axes.plot(arc_angles, [r1] * len(arc_angles), color=branch_color, lw=branch_thickness, 
                      solid_capstyle='round', antialiased=True)
            
            # Draw confidence values
            if show_confidence and hasattr(child, 'confidence') and child.confidence:
                # Add a small background to confidence text for better readability
                axes.text(
                    theta2, (r1 + r2) / 2, f" {child.confidence} ", 
                    fontsize=max(6, font_size * 0.75), ha='center', va='center',
                    rotation=np.degrees(theta2),
                    rotation_mode='anchor',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.75, pad=0.5),
                    clip_on=False
                )

    # 5. Add labels to terminals
    for leaf in terminals:
        r = depths[leaf]
        theta = angles[leaf]
        # Align text properly based on angle
        rotation = np.degrees(theta)
        if 90 < rotation < 270:
            rotation += 180
            ha = 'right'
            pad_theta = theta
            pad_r = r + label_offset
        else:
            ha = 'left'
            pad_theta = theta
            pad_r = r + label_offset
            
        axes.text(
            pad_theta, pad_r, leaf.name, 
            fontsize=font_size, rotation=rotation, ha=ha, va='center',
            rotation_mode='anchor',
            fontstyle='italic',
            bbox=dict(facecolor='white', edgecolor='none', alpha=label_bbox_alpha, pad=0.15),
            clip_on=False
        )
        
    # 6. Formatting
    axes.set_rticks([])
    axes.set_xticks([])
    axes.spines['polar'].set_visible(False)
    axes.set_ylim(0, max_depth * 1.15)


class TreePlot(BasePlot):
    """
    Phylogenetic Tree Plot.
    """

    @save_plot
    def plot(
        self,
        data: str,
        format: str = "newick",
        layout: str = "rectangular",
        show_confidence: bool = True,
        branch_thickness: float = 1.0,
        font_size: int = 10,
        figsize: tuple[float, float] = (8, 6),
        label_offset_scale: float | None = None,
        label_bbox_alpha: float | None = None,
        **kwargs
    ) -> Figure:
        """
        Plot a phylogenetic tree.

        Args:
            data (str): Path to the tree file.
            format (str): Format of the tree file (default: newick).
            layout (str): Layout of the tree ('rectangular', 'circular').
            show_confidence (bool): Whether to show branch support values.      
            branch_thickness (float): Thickness of the branches.
            font_size (int): Font size for leaf labels.
            figsize (tuple): Figure size.
            label_offset_scale (float): Relative label offset from branch ends.
            label_bbox_alpha (float): Alpha of label background box.
            **kwargs: Extra parameters.
        """
        tree = Phylo.read(data, format)
        
        # Apply theme-specific params if needed
        params = self.get_chart_specific_params("tree")
        branch_color = params.get("color", "black")
        label_offset_scale = (
            label_offset_scale if label_offset_scale is not None else params.get("label_offset_scale", 0.05)
        )
        label_bbox_alpha = (
            label_bbox_alpha if label_bbox_alpha is not None else params.get("label_bbox_alpha", 0.65)
        )
        if label_offset_scale <= 0:
            raise ValueError("label_offset_scale must be positive")
        if not (0 <= label_bbox_alpha <= 1):
            raise ValueError("label_bbox_alpha must be between 0 and 1")

        if layout == "circular":
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111, polar=True)
            _draw_circular(
                tree, ax, show_confidence=show_confidence, 
                branch_thickness=branch_thickness, font_size=font_size, 
                branch_color=branch_color,
                label_offset_scale=label_offset_scale,
                label_bbox_alpha=label_bbox_alpha,
            )
        else:
            fig, ax = self.get_fig_ax(figsize=figsize)

            # Pre-calculate to improve styling
            # Configure Bio.Phylo draw options
            draw_kwargs = {
                "axes": ax,
                "do_show": False,
                # Provide an empty label function to Phylo.draw, we will draw them ourselves for better control
                "branch_labels": None,
            }

            # Biopython's Phylo.draw uses matplotlib, we can customize lines after drawing
            Phylo.draw(tree, **draw_kwargs)

            # Custom drawing for confidence values to add background and adjust position
            if show_confidence:
                # Need to manually iterate over clades to find coordinates,
                # Phylo.draw doesn't expose the coordinates easily, but we can extract them
                # Alternatively, we just use Phylo's built-in branch_labels and customize the created texts.
                # Let's re-run draw_kwargs with the label func just to get the texts
                ax.clear() # Clear and redraw with labels
                
                def get_conf(c):
                    if hasattr(c, 'confidence') and c.confidence is not None:
                        # Sometimes confidence is stored as float or string
                        try:
                            val = float(c.confidence)
                            # If it's a bootstrap out of 100, no decimals. If out of 1.0, maybe 2 decimals.
                            return f" {int(val)} " if val > 1 else f" {val:.2f} "
                        except ValueError:
                            return f" {c.confidence} "
                    return None

                Phylo.draw(tree, axes=ax, do_show=False, branch_labels=get_conf)

            # Customize line thickness, color and anti-aliasing
            for line in ax.lines:
                line.set_linewidth(branch_thickness)
                line.set_color(branch_color)
                line.set_solid_capstyle('round')
                line.set_antialiased(True)

            # Customize text (labels)
            terminal_names = {leaf.name for leaf in tree.get_terminals() if leaf.name}
            x_min, x_max = ax.get_xlim()
            x_offset = (x_max - x_min) * label_offset_scale * 0.16
            for text in ax.texts:
                content = text.get_text().strip()
                if not content:
                    continue
                # Check if this is a leaf label or a confidence value
                if content.strip().replace('.', '').isdigit():
                    # This is a confidence value
                    text.set_fontsize(max(6, font_size * 0.75))
                    text.set_color('#333333')
                    text.set_bbox(dict(facecolor='white', edgecolor='none', alpha=0.7, pad=0.2))
                    # slightly shift it up to not overlap the line
                    pos = text.get_position()
                    text.set_position((pos[0], pos[1] + 0.1))
                elif content in terminal_names:
                    text.set_fontsize(font_size)
                    text.set_fontstyle('italic')
                    text.set_ha('left')
                    text.set_va('center')
                    text.set_bbox(dict(facecolor='white', edgecolor='none', alpha=label_bbox_alpha, pad=0.15))
                    pos = text.get_position()
                    text.set_position((pos[0] + x_offset, pos[1]))
                else:
                    text.set_fontsize(max(7, font_size * 0.85))
                    text.set_ha('left')
                    text.set_va('center')
                    text.set_color('#222222')
                    text.set_bbox(dict(facecolor='white', edgecolor='none', alpha=min(1.0, label_bbox_alpha + 0.2), pad=0.15))
                    pos = text.get_position()
                    text.set_position((pos[0] + x_offset, pos[1]))

            # Optional: remove axes for cleaner look
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(True)
            ax.spines['bottom'].set_linewidth(1.5)
            ax.set_yticks([])
            ax.set_ylabel("")
            ax.set_xlabel("Evolutionary distance", fontsize=max(10, font_size * 0.9))

        fig.tight_layout()
        return fig
