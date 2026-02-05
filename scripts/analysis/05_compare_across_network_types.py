"""
NOTE: This script currently only shows AGGREGATED sub-network results.
For testing on FULL networks (from master_centralities.csv), 
use a separate script that loads full network data.
"""
Visualize how composite (with optimal universal threshold) performs across network types.

Shows a comprehensive view of composite wins vs. individual centrality wins across:
- Unbalanced networks
- Balanced-importance networks  
- Balanced-doctypebranch networks

For each combination and ground truth.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np

# Configuration
INPUT_DIR = 'results/analysis/04_optimized_threshold_composite'
OUTPUT_DIR = 'results/analysis/05_network_type_comparison'
COMBINATIONS = ['PageRank+Degree', 'Degree+Eigenvector', 'Degree+InDegree']
GROUND_TRUTHS = ['importance', 'doctypebranch']

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


def load_results():
    """Load results from the optimized threshold analysis."""
    json_path = os.path.join(INPUT_DIR, 'detailed_results.json')
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    return data


def create_network_type_comparison_plots(all_results):
    """Create plots comparing performance across network types."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # For each combination and ground truth
    for combo_name in COMBINATIONS:
        if combo_name not in all_results:
            continue
        
        results = all_results[combo_name]['results']
        optimal_thresholds = all_results[combo_name]['optimal_thresholds']
        
        for ground_truth in GROUND_TRUTHS:
            # Create a figure with 3 subplots (one per network type)
            fig, axes = plt.subplots(1, 3, figsize=(24, 8))
            
            network_types = ['unbalanced', 'balanced-importance', 'balanced-doctypebranch']
            
            for idx, network_type in enumerate(network_types):
                ax = axes[idx]
                counts = results[network_type][ground_truth]
                
                # Create full list including all centralities
                count_dict = {measure: counts.get(measure, 0) for measure in CENTRALITIES}
                
                # Sort by count
                sorted_items = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
                names = [item[0] for item in sorted_items]
                values = [item[1] for item in sorted_items]
                
                # Color composite differently
                colors = ['#ff6b6b' if name == 'composite' else '#4ecdc4' for name in names]
                
                bars = ax.barh(names, values, color=colors)
                
                # Add value labels
                for bar in bars:
                    width = bar.get_width()
                    if width > 0:
                        ax.text(width, bar.get_y() + bar.get_height()/2.,
                               f'{int(width)}',
                               ha='left', va='center',
                               fontsize=12, fontweight='bold')
                
                ax.set_xlabel('Number of Networks Won', fontsize=14, fontweight='bold')
                
                # Total networks for this type
                total_networks = sum(values)
                composite_wins = count_dict.get('composite', 0)
                win_rate = (composite_wins / total_networks * 100) if total_networks > 0 else 0
                
                ax.set_title(f'{network_type}\n(n={total_networks}, composite: {composite_wins}/{total_networks} = {win_rate:.1f}%)',
                            fontsize=14, fontweight='bold', pad=10)
                ax.grid(axis='x', alpha=0.3)
                ax.invert_yaxis()
            
            # Overall figure title
            opt_threshold = optimal_thresholds[ground_truth]
            fig.suptitle(f'{combo_name} - {ground_truth}\nOptimal Threshold: {opt_threshold:.2f}',
                        fontsize=18, fontweight='bold', y=0.98)
            
            plt.tight_layout(rect=[0, 0, 1, 0.96], pad=2.0, w_pad=3.0)
            
            filename = os.path.join(OUTPUT_DIR, f'{combo_name.replace("+", "_")}_{ground_truth}.png')
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Saved: {filename}")
            plt.close()


def create_aggregated_comparison(all_results):
    """Create aggregated view showing total wins across ALL networks."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for combo_name in COMBINATIONS:
        if combo_name not in all_results:
            continue
        
        results = all_results[combo_name]['results']
        optimal_thresholds = all_results[combo_name]['optimal_thresholds']
        
        for ground_truth in GROUND_TRUTHS:
            # Aggregate counts across all network types
            aggregated_counts = {measure: 0 for measure in CENTRALITIES}
            total_networks = 0
            
            for network_type in ['unbalanced', 'balanced-importance', 'balanced-doctypebranch']:
                counts = results[network_type][ground_truth]
                for measure, count in counts.items():
                    aggregated_counts[measure] = aggregated_counts.get(measure, 0) + count
                total_networks += sum(counts.values())
            
            # Create plot
            fig, ax = plt.subplots(figsize=(12, 10))
            
            # Sort by count
            sorted_items = sorted(aggregated_counts.items(), key=lambda x: x[1], reverse=True)
            names = [item[0] for item in sorted_items]
            values = [item[1] for item in sorted_items]
            
            colors = ['#ff6b6b' if name == 'composite' else '#4ecdc4' for name in names]
            
            bars = ax.barh(names, values, color=colors)
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                if width > 0:
                    ax.text(width, bar.get_y() + bar.get_height()/2.,
                           f'{int(width)}',
                           ha='left', va='center',
                           fontsize=14, fontweight='bold')
            
            ax.set_xlabel('Total Networks Won (Across All Types)', fontsize=16, fontweight='bold')
            
            composite_wins = aggregated_counts.get('composite', 0)
            win_rate = (composite_wins / total_networks * 100) if total_networks > 0 else 0
            
            opt_threshold = optimal_thresholds[ground_truth]
            ax.set_title(f'{combo_name} - {ground_truth}\n' +
                        f'Optimal Threshold: {opt_threshold:.2f}\n' +
                        f'Total: {composite_wins}/{total_networks} networks won ({win_rate:.1f}%)',
                        fontsize=16, fontweight='bold', pad=15)
            ax.grid(axis='x', alpha=0.3)
            ax.invert_yaxis()
            
            plt.tight_layout()
            
            filename = os.path.join(OUTPUT_DIR, f'{combo_name.replace("+", "_")}_{ground_truth}_AGGREGATED.png')
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Saved: {filename}")
            plt.close()


def create_summary_table(all_results):
    """Create summary table showing performance across network types."""
    import pandas as pd
    
    rows = []
    
    for combo_name in COMBINATIONS:
        if combo_name not in all_results:
            continue
        
        results = all_results[combo_name]['results']
        optimal_thresholds = all_results[combo_name]['optimal_thresholds']
        
        for ground_truth in GROUND_TRUTHS:
            opt_threshold = optimal_thresholds[ground_truth]
            
            # Per network type
            for network_type in ['unbalanced', 'balanced-importance', 'balanced-doctypebranch']:
                counts = results[network_type][ground_truth]
                total = sum(counts.values())
                composite_wins = counts.get('composite', 0)
                win_rate = (composite_wins / total * 100) if total > 0 else 0
                
                rows.append({
                    'Combination': combo_name,
                    'Ground Truth': ground_truth,
                    'Threshold': f'{opt_threshold:.2f}',
                    'Network Type': network_type,
                    'Composite Wins': composite_wins,
                    'Total Networks': total,
                    'Win Rate': f'{win_rate:.1f}%'
                })
            
            # Aggregated
            aggregated_wins = sum(results[nt][ground_truth].get('composite', 0) 
                                for nt in ['unbalanced', 'balanced-importance', 'balanced-doctypebranch'])
            aggregated_total = sum(sum(results[nt][ground_truth].values()) 
                                  for nt in ['unbalanced', 'balanced-importance', 'balanced-doctypebranch'])
            aggregated_rate = (aggregated_wins / aggregated_total * 100) if aggregated_total > 0 else 0
            
            rows.append({
                'Combination': combo_name,
                'Ground Truth': ground_truth,
                'Threshold': f'{opt_threshold:.2f}',
                'Network Type': 'ALL (aggregated)',
                'Composite Wins': aggregated_wins,
                'Total Networks': aggregated_total,
                'Win Rate': f'{aggregated_rate:.1f}%'
            })
    
    df = pd.DataFrame(rows)
    
    # Save to CSV
    csv_path = os.path.join(OUTPUT_DIR, 'summary_across_network_types.csv')
    df.to_csv(csv_path, index=False)
    print(f"\nSummary table saved to: {csv_path}")
    
    # Print to console
    print("\n" + "="*100)
    print("PERFORMANCE ACROSS NETWORK TYPES")
    print("="*100)
    print(df.to_string(index=False))
    
    return df


def main():
    """Main execution."""
    print("="*80)
    print("COMPARING COMPOSITE PERFORMANCE ACROSS NETWORK TYPES")
    print("="*80)
    
    # Load results
    all_results = load_results()
    
    # Create visualizations
    print("\nCreating network type comparison plots...")
    create_network_type_comparison_plots(all_results)
    
    print("\nCreating aggregated comparison plots...")
    create_aggregated_comparison(all_results)
    
    # Create summary table
    create_summary_table(all_results)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print(f"Results saved to: {OUTPUT_DIR}")
    print("="*80)


if __name__ == "__main__":
    main()
