import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap, is_color_like
from Bio import AlignIO

try:
    import logomaker
    HAS_LOGOMAKER = True
except ImportError:
    HAS_LOGOMAKER = False

from .base import BasePlot, save_plot

# Standard Clustal X colors for amino acids
AA_COLORS = {
    'A': '#80a0f0', 'R': '#f01505', 'N': '#00ff00', 'D': '#c048c0',
    'C': '#f08080', 'Q': '#00ff00', 'E': '#c048c0', 'G': '#f09048',
    'H': '#15a4a4', 'I': '#80a0f0', 'L': '#80a0f0', 'K': '#f01505',
    'M': '#80a0f0', 'F': '#80a0f0', 'P': '#ffff00', 'S': '#00ff00',
    'T': '#00ff00', 'W': '#80a0f0', 'Y': '#15a4a4', 'V': '#80a0f0',
    '-': '#ffffff', 'X': '#ffffff'
}

NT_COLORS = {
    'A': '#5050FF', 'C': '#E00000', 'G': '#00C000', 'T': '#E6E600', 
    'U': '#E6E600', '-': '#ffffff', 'N': '#ffffff'
}

# Add contrasting text colors based on background brightness
def get_text_color(hex_color):
    if hex_color == '#ffffff':
        return 'black'
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Simple brightness formula
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return 'black' if brightness > 125 else 'white'
    return 'black'

class MsaPlot(BasePlot):
    """
    Multiple Sequence Alignment Plot.
    """

    @save_plot
    def plot(self, data: str, seq_type: str = None, show_logo: bool = None,
             font_size: int = None, figsize: tuple = None, bases_per_line: int = None,
             base_colors: dict = None,
             **kwargs) -> Figure:
        """
        Plot an MSA.
        
        Args:
            data (str): Path to the MSA file (FASTA).
            seq_type (str): 'aa' for amino acids, 'nt' for nucleotides.
            show_logo (bool): Whether to show a sequence logo at the top.
            font_size (int): Font size for sequence labels.
            figsize (tuple): Figure size (width, height). If None, calculated automatically.
            bases_per_line (int): Wrap alignment by this many residues per line.
            base_colors (dict): Custom color map for residues, e.g. {'A': '#000000'}.
            **kwargs: Extra parameters.
        """
        theme_params = self.get_chart_specific_params("msa")
        seq_type = seq_type if seq_type is not None else theme_params.get("seq_type", "aa")
        show_logo = show_logo if show_logo is not None else theme_params.get("show_logo", True)
        font_size = font_size if font_size is not None else theme_params.get("font_size", 10)
        figsize = figsize if figsize is not None else theme_params.get("figsize")
        bases_per_line = bases_per_line if bases_per_line is not None else theme_params.get("bases_per_line")
        theme_base_colors = theme_params.get("base_colors", {})
        if theme_base_colors is None:
            theme_base_colors = {}
        if not isinstance(theme_base_colors, dict):
            raise ValueError("Theme parameter 'msa.base_colors' must be a dictionary")
        if base_colors is None:
            base_colors = {}
        if not isinstance(base_colors, dict):
            raise ValueError("base_colors must be a dictionary")
        merged_base_colors = {**theme_base_colors, **base_colors}

        alignment = AlignIO.read(data, "fasta")
        n_seqs = len(alignment)
        seq_len = alignment.get_alignment_length()
        
        ids = [rec.id for rec in alignment]
        seqs = [str(rec.seq).upper() for rec in alignment]
        
        colors_dict = dict(AA_COLORS if seq_type.lower() == "aa" else NT_COLORS)
        if merged_base_colors:
            for base, color in merged_base_colors.items():
                base_key = str(base).upper()
                if not is_color_like(color):
                    raise ValueError(f"Invalid color for base '{base}': {color}")
                colors_dict[base_key] = color
        colors_dict.setdefault("-", "#ffffff")
        fallback_color = colors_dict["-"]
        for seq in seqs:
            for base in seq:
                if base not in colors_dict:
                    colors_dict[base] = fallback_color
        text_colors_dict = {c: get_text_color(hex_c) for c, hex_c in colors_dict.items()}
        
        # Map characters to integers for imshow
        char_list = list(colors_dict.keys())
        char_to_int = {c: i for i, c in enumerate(char_list)}

        if bases_per_line is not None and bases_per_line <= 0:
            raise ValueError("bases_per_line must be a positive integer")

        line_len = min(seq_len, bases_per_line) if bases_per_line else seq_len
        n_blocks = max(1, int(np.ceil(seq_len / line_len)))
        n_rows = n_blocks * n_seqs + (n_blocks - 1)
        row_to_seq_idx = []
        row_to_block_idx = []
        y_ticks = []
        y_ticklabels = []

        row_idx = 0
        for block_idx in range(n_blocks):
            for seq_idx in range(n_seqs):
                row_to_seq_idx.append(seq_idx)
                row_to_block_idx.append(block_idx)
                y_ticks.append(row_idx)
                y_ticklabels.append(ids[seq_idx])
                row_idx += 1
            if block_idx < n_blocks - 1:
                row_to_seq_idx.append(None)
                row_to_block_idx.append(None)
                row_idx += 1
        
        # Build matrix
        matrix = np.full((n_rows, line_len), char_to_int.get('-', 0), dtype=int)
        for row_i, (seq_idx, block_idx) in enumerate(zip(row_to_seq_idx, row_to_block_idx)):
            if seq_idx is None:
                continue
            start = block_idx * line_len
            end = min(start + line_len, seq_len)
            for j, c in enumerate(seqs[seq_idx][start:end]):
                matrix[row_i, j] = char_to_int.get(c, char_to_int.get('-', 0))
                
        # Create colormap
        cmap = ListedColormap([colors_dict[c] for c in char_list])
        
        if figsize is None:
            width = max(10, line_len * 0.3)
            height_msa = max(4, n_rows * 0.4)
            height_logo = 2.0 if show_logo else 0
            figsize = (width, height_msa + height_logo)
            
        if show_logo and HAS_LOGOMAKER:
            fig = plt.figure(figsize=figsize)
            # Reduce spacing between logo and msa plot
            gs = fig.add_gridspec(2, 1, height_ratios=[1, max(1, n_seqs * 0.2)], hspace=0.05)
            ax_logo = fig.add_subplot(gs[0])
            ax_msa = fig.add_subplot(gs[1])
            
            # Create logo data
            df_seqs = pd.DataFrame([list(s) for s in seqs])
            counts_df = pd.DataFrame(0.0, index=range(seq_len), columns=[c for c in char_list if c != '-'])
            
            for j in range(seq_len):
                col_counts = df_seqs[j].value_counts()
                for c, count in col_counts.items():
                    if c in counts_df.columns:
                        counts_df.at[j, c] = count
                        
            # Only draw logo if we have columns left after removing invariant gaps
            if len(counts_df.columns) > 0:
                # Convert counts to probabilities (or information content)
                prob_df = counts_df.div(counts_df.sum(axis=1) + 1e-9, axis=0)
                
                # Check if prob_df is completely empty before passing to logomaker
                if not prob_df.empty and prob_df.shape[0] >= 1:
                    try:
                        logo = logomaker.Logo(prob_df, ax=ax_logo, color_scheme=colors_dict)
                        logo.style_spines(visible=False)
                    except Exception as e:
                        print(f"Warning: Could not create logo: {e}")
                        ax_logo.set_visible(False)
                else:
                    ax_logo.set_visible(False)
            else:
                ax_logo.set_visible(False)
                
            ax_logo.set_xticks([])
            ax_logo.set_yticks([])
            ax_logo.set_xlim(-0.5, seq_len - 0.5)
        else:
            fig, ax_msa = self.get_fig_ax(figsize=figsize)
            
        # Draw MSA grid
        ax_msa.imshow(matrix, cmap=cmap, aspect='auto', interpolation='nearest')
        
        # Add gridlines to separate sequences
        ax_msa.set_xticks(np.arange(-0.5, line_len, 1), minor=True)
        ax_msa.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
        ax_msa.grid(which="minor", color="white", linestyle='-', linewidth=1.5)
        ax_msa.tick_params(which="minor", size=0)
        
        # Add text if not too long
        if line_len <= 150:
            for i, (seq_idx, block_idx) in enumerate(zip(row_to_seq_idx, row_to_block_idx)):
                if seq_idx is None:
                    continue
                start = block_idx * line_len
                end = min(start + line_len, seq_len)
                seq = seqs[seq_idx][start:end]
                for j, c in enumerate(seq):
                    if c != '-':
                        ax_msa.text(
                            j, i, c, ha='center', va='center', 
                            fontsize=max(6, font_size - 2),
                            color=text_colors_dict.get(c, 'black'),
                            fontweight='bold',
                            fontfamily='monospace'
                        )
                        
        ax_msa.set_yticks(y_ticks)
        ax_msa.set_yticklabels(y_ticklabels, fontsize=font_size, fontfamily='monospace')
        
        # Improve x-axis labels
        x_ticks = np.arange(0, line_len, max(1, line_len // 10))
        ax_msa.set_xticks(x_ticks)
        ax_msa.set_xticklabels(x_ticks + 1, fontsize=font_size)
        
        ax_msa.set_xlim(-0.5, line_len - 0.5)
        
        # Remove spines for a cleaner look
        for spine in ax_msa.spines.values():
            spine.set_visible(False)
            
        # Ensure tight layout and save space for labels
        # When aspect is auto and sequence is long, bounding box calculation can clip labels
        # Use constrained_layout instead of tight_layout, or adjust subplots
        try:
            fig.tight_layout(pad=1.5, rect=[0.05, 0.05, 0.95, 0.95])
        except Exception:
            pass
        return fig
