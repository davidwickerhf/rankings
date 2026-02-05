"""
Generate overlay visualizations comparing composite performance across balanced networks.

Creates 2 figures:
1. Balanced-Importance: Shows all 3 composites with importance (solid) vs doctypebranch (hatched)
2. Balanced-Doctypebranch: Shows all 3 composites with importance (solid) vs doctypebranch (hatched)

Each figure has 3 subplots (one per composite combination), with overlayed bars showing
performance on both ground truths.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json


# ==================== CONFIGURATION ====================
RESULTS_PATH = 'results/analysis/04_optimized_threshold_composite/detailed_results.json'
OUTPUT_DIR = 'results/analysis/08_balanced_overlay_visualizations'

COMBINATIONS = [
    ('Degree+InDegree', 'Degree (high) + In-Degree (low)'),
    ('PageRank+Degree', 'PageRank (high) + Degree (low)'),
    ('Degree+Eigenvector', 'Degree (high) + Eigenvector (low)'),
]

CENTRALITIES = [
    'composite',
    'degree_centrality',
    'in_degree_centrality', 
    'out_degree_centrality',
    'betweenness_centrality',
    'closeness_centrality',
    'core_number',
    'relative_in_degree_centrality',
    'eigenvector_centrality',
    'pagerank',
    'hits_hub',
    'hits_authority',
    'harmonic_centrality',
    'disruption'
]

CENTRALITY_DISPLAY_NAMES = {
    'composite': 'Composite',
    'degree_centrality': 'Degree',
    'in_degree_centrality': 'In-Degree',
    'out_degree_centrality': 'Out-Degree',
    'betweenness_centrality': 'Betweenness',
    'closeness_centrality': 'Closeness',
    'core_number': 'Core Number',
    'relative_in_degree_centrality': 'Relative In-Degree',
    'eigenvector_centrality': 'Eigenvector',
    'pagerank': 'PageRank',
    'hits_hub': 'HITS Hub',
    'hits_authority': 'HITS Authority',
    'harmonic_centrality': 'Harmonic',
    'disruption': 'Disruption'
}


def load_results():
    """Load results from script 04."""
    with open(RESULTS_PATH, 'r') as f:
        return json.load(f)


def create_overlay_figure(network_type, results):
    """
    Create figure with 3 subplots showing overlay of importance vs doctypebranch.
    
    Args:
        network_type: 'balanced-importance' or 'balanced-doctypebranch'
        results: Full results from script 04
    """
    fig, axes = plt.subplots(1, 3, figsize=(24, 8))
    
    # Determine title based on network type
    if network_type == 'balanced-importance':
        title_text = "Performance on Importance-Balanced Networks: Count of networks where each measure achieved highest correlation"
    else:
        title_text = "Performance on Court-Branch-Balanced Networks: Count of networks where each measure achieved highest correlation"
    
    for idx, (combo_key, combo_name) in enumerate(COMBINATIONS):
        ax = axes[idx]
        
        if combo_key not in results:
            continue
        
        combo_data = results[combo_key]
        optimal_thresholds = combo_data['optimal_thresholds']
        
        # Get counts for both ground truths
        importance_counts = combo_data['results'][network_type]['importance']
        doctypebranch_counts = combo_data['results'][network_type]['doctypebranch']
        
        # Create full measure list
        measures = CENTRALITIES.copy()
        
        # Get counts for each measure
        importance_values = [importance_counts.get(m, 0) for m in measures]
        doctypebranch_values = [doctypebranch_counts.get(m, 0) for m in measures]
        
        # Sort by total (importance + doctypebranch) descending
        totals = [i + d for i, d in zip(importance_values, doctypebranch_values)]
        sorted_indices = np.argsort(totals)[::-1]
        
        measures_sorted = [measures[i] for i in sorted_indices]
        importance_sorted = [importance_values[i] for i in sorted_indices]
        doctypebranch_sorted = [doctypebranch_values[i] for i in sorted_indices]
        
        # Convert to display names
        measures_display = [CENTRALITY_DISPLAY_NAMES.get(m, m) for m in measures_sorted]
        
        # Create y positions
        y_pos = np.arange(len(measures_sorted))
        
        # Define colors
        composite_color_importance = '#ff6b6b'  # Red for composite-importance
        composite_color_doctypebranch = '#cc5555'  # Darker red for composite-doctypebranch
        individual_color_importance = '#4ecdc4'  # Teal for individuals-importance
        individual_color_doctypebranch = '#3da89f'  # Darker teal for individuals-doctypebranch
        
        # Plot bars with overlay
        for i, measure in enumerate(measures_sorted):
            if measure == 'composite':
                # Composite bars
                ax.barh(y_pos[i], importance_sorted[i], height=0.4, 
                       color=composite_color_importance, alpha=0.9, 
                       label='Composite - highest correlation with Importance' if i == 0 else '')
                ax.barh(y_pos[i] - 0.2, doctypebranch_sorted[i], height=0.4,
                       color=composite_color_doctypebranch, alpha=0.7,
                       hatch='///', edgecolor='white', linewidth=0.5,
                       label='Composite - highest correlation with Court Branch' if i == 0 else '')
            else:
                # Individual centrality bars
                ax.barh(y_pos[i], importance_sorted[i], height=0.4,
                       color=individual_color_importance, alpha=0.9,
                       label='Individual - highest correlation with Importance' if i == 1 else '')
                ax.barh(y_pos[i] - 0.2, doctypebranch_sorted[i], height=0.4,
                       color=individual_color_doctypebranch, alpha=0.7,
                       hatch='///', edgecolor='white', linewidth=0.5,
                       label='Individual - highest correlation with Court Branch' if i == 1 else '')
            
            # Add value labels (only show if different or if only one is non-zero)
            if importance_sorted[i] > 0 and doctypebranch_sorted[i] > 0:
                if importance_sorted[i] == doctypebranch_sorted[i]:
                    # Same count - show only once in the middle
                    ax.text(importance_sorted[i] + 0.3, y_pos[i] - 0.1,
                           str(importance_sorted[i]),
                           va='center', fontsize=11, fontweight='bold')
                else:
                    # Different counts - show both
                    ax.text(importance_sorted[i] + 0.3, y_pos[i],
                           str(importance_sorted[i]),
                           va='center', fontsize=11, fontweight='bold')
                    ax.text(doctypebranch_sorted[i] + 0.3, y_pos[i] - 0.2,
                           str(doctypebranch_sorted[i]),
                           va='center', fontsize=11, fontweight='bold')
            elif importance_sorted[i] > 0:
                ax.text(importance_sorted[i] + 0.3, y_pos[i],
                       str(importance_sorted[i]),
                       va='center', fontsize=11, fontweight='bold')
            elif doctypebranch_sorted[i] > 0:
                ax.text(doctypebranch_sorted[i] + 0.3, y_pos[i] - 0.2,
                       str(doctypebranch_sorted[i]),
                       va='center', fontsize=11, fontweight='bold')
        
        # Format plot
        ax.set_yticks(y_pos - 0.1)
        ax.set_yticklabels(measures_display, fontsize=14)
        ax.set_xlabel('Number of Networks', fontsize=14, fontweight='bold')
        
        # Get thresholds
        tau_imp = optimal_thresholds["importance"]
        tau_doc = optimal_thresholds["doctypebranch"]
        
        # Create title with thresholds
        title = f'{combo_name}'
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Add threshold info as subtitle using text (much more spacing)
        subtitle = f'Importance τ = {tau_imp:.2f}  |  Court Branch τ = {tau_doc:.2f}'
        ax.text(0.5, 1.15, subtitle, transform=ax.transAxes,
               ha='center', va='bottom', fontsize=13, style='italic')
        
        # Add legend only to first subplot
        if idx == 0:
            # Create custom legend
            legend_labels = [
                'Composite - Importance',
                'Composite - Court Branch',
                'Individual - Importance',
                'Individual - Court Branch'
            ]
            handles, _ = ax.get_legend_handles_labels()
            ax.legend(handles, legend_labels, loc='upper left', fontsize=12, 
                     framealpha=0.95, bbox_to_anchor=(0.02, 0.98))
        
        ax.grid(axis='x', alpha=0.3)
        ax.set_axisbelow(True)
    
    # Add overall title
    fig.suptitle(title_text, fontsize=17, fontweight='bold', y=0.985)
    
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    
    return fig


def main():
    """Main execution function."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Loading results from script 04...")
    results = load_results()
    
    print("\nGenerating overlay visualizations...")
    
    # Create figure for balanced-importance networks
    print("  Creating balanced-importance figure...")
    fig1 = create_overlay_figure('balanced-importance', results)
    fig1_path = os.path.join(OUTPUT_DIR, 'balanced_importance_overlay.png')
    fig1.savefig(fig1_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"  Saved: {fig1_path}")
    plt.close(fig1)
    
    # Create figure for balanced-doctypebranch networks
    print("  Creating balanced-doctypebranch figure...")
    fig2 = create_overlay_figure('balanced-doctypebranch', results)
    fig2_path = os.path.join(OUTPUT_DIR, 'balanced_doctypebranch_overlay.png')
    fig2.savefig(fig2_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"  Saved: {fig2_path}")
    plt.close(fig2)
    
    print("\n" + "="*80)
    print("VISUALIZATION COMPLETE")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*80)
    
    print("\nGenerated figures:")
    print("1. balanced_importance_overlay.png")
    print("   - Shows all 3 composites on balanced-importance networks")
    print("   - Overlays performance on Importance (solid) vs Court Branch (hatched)")
    print("\n2. balanced_doctypebranch_overlay.png")
    print("   - Shows all 3 composites on balanced-doctypebranch networks")
    print("   - Overlays performance on Importance (solid) vs Court Branch (hatched)")


if __name__ == "__main__":
    main()
