"""
Compare HIGH-RELEVANCE PRIORITY (script 04) vs LOW-RELEVANCE PRIORITY (script 06).

This script loads results from both approaches and creates:
1. Comparison tables showing win rates for each approach
2. Visualizations comparing performance across network types
3. Analysis of when each approach performs better

This empirically answers the professor's question about whether Low-Relevance Priority
is meaningfully different from High-Relevance Priority.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json


# ==================== CONFIGURATION ====================
HIGH_RELEVANCE_RESULTS = 'results/analysis/04_optimized_threshold_composite/detailed_results.json'
LOW_RELEVANCE_RESULTS = 'results/analysis/06_low_relevance_priority/detailed_results.json'
OUTPUT_DIR = 'results/analysis/07_priority_comparison'

COMBINATIONS = ['PageRank+Degree', 'Degree+Eigenvector', 'Degree+InDegree']
NETWORK_TYPES = ['unbalanced', 'balanced-importance', 'balanced-doctypebranch']
GROUND_TRUTHS = ['importance', 'doctypebranch']


# ==================== LOADING FUNCTIONS ====================
def load_results(filepath):
    """Load detailed results from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def extract_win_rates(results):
    """Extract win rates from results structure."""
    win_rates = {}
    
    for combo in COMBINATIONS:
        if combo not in results:
            continue
        
        win_rates[combo] = {}
        combo_results = results[combo]['results']
        
        for network_type in NETWORK_TYPES:
            win_rates[combo][network_type] = {}
            
            for ground_truth in GROUND_TRUTHS:
                counts = combo_results[network_type][ground_truth]
                total = sum(counts.values())
                composite_wins = counts.get('composite', 0)
                
                win_rates[combo][network_type][ground_truth] = {
                    'wins': composite_wins,
                    'total': total,
                    'rate': (composite_wins / total * 100) if total > 0 else 0.0
                }
    
    return win_rates


def create_comparison_table(high_wins, low_wins):
    """Create comparison table showing both approaches side by side."""
    rows = []
    
    for combo in COMBINATIONS:
        for network_type in NETWORK_TYPES:
            for ground_truth in GROUND_TRUTHS:
                high_data = high_wins[combo][network_type][ground_truth]
                low_data = low_wins[combo][network_type][ground_truth]
                
                # Calculate difference
                diff = low_data['rate'] - high_data['rate']
                better = 'Low-Rel' if diff > 0 else ('High-Rel' if diff < 0 else 'Tie')
                
                rows.append({
                    'Combination': combo,
                    'Network Type': network_type,
                    'Ground Truth': ground_truth,
                    'Total Networks': high_data['total'],
                    'High-Rel Wins': high_data['wins'],
                    'High-Rel Rate': f"{high_data['rate']:.1f}%",
                    'Low-Rel Wins': low_data['wins'],
                    'Low-Rel Rate': f"{low_data['rate']:.1f}%",
                    'Difference': f"{diff:+.1f}%",
                    'Better': better
                })
    
    return pd.DataFrame(rows)


def create_summary_statistics(comparison_df):
    """Create summary statistics across all comparisons."""
    # Count wins
    high_rel_better = (comparison_df['Better'] == 'High-Rel').sum()
    low_rel_better = (comparison_df['Better'] == 'Low-Rel').sum()
    ties = (comparison_df['Better'] == 'Tie').sum()
    
    # Average differences
    comparison_df['Diff_numeric'] = comparison_df['Difference'].str.rstrip('%').astype(float)
    avg_diff = comparison_df['Diff_numeric'].mean()
    
    # By combination
    by_combo = comparison_df.groupby('Combination').agg({
        'Diff_numeric': 'mean',
        'Better': lambda x: (x == 'Low-Rel').sum()
    }).round(2)
    
    # By network type
    by_network = comparison_df.groupby('Network Type').agg({
        'Diff_numeric': 'mean',
        'Better': lambda x: (x == 'Low-Rel').sum()
    }).round(2)
    
    summary = {
        'overall': {
            'high_rel_better': int(high_rel_better),
            'low_rel_better': int(low_rel_better),
            'ties': int(ties),
            'avg_difference': float(avg_diff),
        },
        'by_combination': by_combo.to_dict(),
        'by_network_type': by_network.to_dict()
    }
    
    return summary


def plot_comparison_bars(comparison_df):
    """Create bar chart comparing win rates."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for idx, combo in enumerate(COMBINATIONS):
        ax = axes[idx]
        combo_data = comparison_df[comparison_df['Combination'] == combo].copy()
        
        # Create labels
        combo_data['Label'] = (combo_data['Network Type'].str.replace('balanced-', 'bal-') + 
                               '\n' + combo_data['Ground Truth'])
        
        # Extract numeric rates
        combo_data['High_Rate'] = combo_data['High-Rel Rate'].str.rstrip('%').astype(float)
        combo_data['Low_Rate'] = combo_data['Low-Rel Rate'].str.rstrip('%').astype(float)
        
        x = np.arange(len(combo_data))
        width = 0.35
        
        # Plot bars
        bars1 = ax.bar(x - width/2, combo_data['High_Rate'], width, 
                      label='High-Relevance Priority', color='#4ecdc4', alpha=0.8)
        bars2 = ax.bar(x + width/2, combo_data['Low_Rate'], width, 
                      label='Low-Relevance Priority', color='#ff6b6b', alpha=0.8)
        
        # Styling
        ax.set_ylabel('Composite Win Rate (%)', fontsize=11)
        ax.set_title(combo, fontsize=14, fontweight='bold', pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(combo_data['Label'], fontsize=9, rotation=45, ha='right')
        ax.set_ylim(0, 100)
        ax.legend(fontsize=9, loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    return fig


def plot_difference_heatmap(comparison_df):
    """Create heatmap showing where Low-Relevance Priority outperforms."""
    # Prepare data
    comparison_df['Diff_numeric'] = comparison_df['Difference'].str.rstrip('%').astype(float)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for idx, combo in enumerate(COMBINATIONS):
        ax = axes[idx]
        combo_data = comparison_df[comparison_df['Combination'] == combo]
        
        # Create pivot table
        pivot = combo_data.pivot_table(
            values='Diff_numeric',
            index='Ground Truth',
            columns='Network Type',
            aggfunc='first'
        )
        
        # Reorder columns
        pivot = pivot[NETWORK_TYPES]
        
        # Plot heatmap
        im = ax.imshow(pivot.values, cmap='RdYlGn', aspect='auto', 
                      vmin=-20, vmax=20, interpolation='nearest')
        
        # Set ticks
        ax.set_xticks(np.arange(len(NETWORK_TYPES)))
        ax.set_yticks(np.arange(len(GROUND_TRUTHS)))
        ax.set_xticklabels([nt.replace('balanced-', 'bal-') for nt in NETWORK_TYPES], 
                          fontsize=10, rotation=45, ha='right')
        ax.set_yticklabels(GROUND_TRUTHS, fontsize=10)
        
        # Add values
        for i in range(len(GROUND_TRUTHS)):
            for j in range(len(NETWORK_TYPES)):
                value = pivot.values[i, j]
                color = 'white' if abs(value) > 10 else 'black'
                ax.text(j, i, f'{value:+.1f}%', ha='center', va='center',
                       color=color, fontsize=10, fontweight='bold')
        
        ax.set_title(combo, fontsize=14, fontweight='bold', pad=10)
        
        # Add colorbar to last subplot
        if idx == 2:
            cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('Low-Rel advantage (%)', rotation=270, labelpad=20, fontsize=10)
    
    plt.suptitle('Performance Difference: Low-Relevance - High-Relevance Priority (%)', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    return fig


def print_summary_report(summary, comparison_df):
    """Print formatted summary report."""
    print("\n" + "="*80)
    print("COMPARISON SUMMARY: HIGH-RELEVANCE vs LOW-RELEVANCE PRIORITY")
    print("="*80)
    
    print("\nOVERALL RESULTS:")
    print(f"  Low-Relevance Priority better:  {summary['overall']['low_rel_better']:2d} cases")
    print(f"  High-Relevance Priority better: {summary['overall']['high_rel_better']:2d} cases")
    print(f"  Ties:                          {summary['overall']['ties']:2d} cases")
    print(f"  Average difference:            {summary['overall']['avg_difference']:+.2f}% (positive = Low-Rel better)")
    
    print("\nBY COMBINATION:")
    for combo in COMBINATIONS:
        avg_diff = summary['by_combination']['Diff_numeric'][combo]
        low_wins = summary['by_combination']['Better'][combo]
        print(f"  {combo:25s}: {avg_diff:+6.2f}% avg diff, Low-Rel better in {low_wins}/6 cases")
    
    print("\nBY NETWORK TYPE:")
    for network_type in NETWORK_TYPES:
        avg_diff = summary['by_network_type']['Diff_numeric'][network_type]
        low_wins = summary['by_network_type']['Better'][network_type]
        print(f"  {network_type:25s}: {avg_diff:+6.2f}% avg diff, Low-Rel better in {low_wins}/6 cases")
    
    print("\n" + "="*80)
    print("DETAILED COMPARISON TABLE:")
    print("="*80)
    print(comparison_df.to_string(index=False))


def main():
    """Main execution function."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Loading results from both approaches...")
    high_results = load_results(HIGH_RELEVANCE_RESULTS)
    low_results = load_results(LOW_RELEVANCE_RESULTS)
    
    print("Extracting win rates...")
    high_wins = extract_win_rates(high_results)
    low_wins = extract_win_rates(low_results)
    
    print("Creating comparison table...")
    comparison_df = create_comparison_table(high_wins, low_wins)
    
    # Save comparison table
    comparison_path = os.path.join(OUTPUT_DIR, 'priority_comparison.csv')
    comparison_df.to_csv(comparison_path, index=False)
    print(f"Saved comparison table to: {comparison_path}")
    
    print("Generating summary statistics...")
    summary = create_summary_statistics(comparison_df)
    
    # Save summary as JSON
    summary_path = os.path.join(OUTPUT_DIR, 'summary_statistics.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary statistics to: {summary_path}")
    
    print("Creating visualizations...")
    
    # Bar chart comparison
    fig1 = plot_comparison_bars(comparison_df)
    bar_path = os.path.join(OUTPUT_DIR, 'win_rate_comparison.png')
    fig1.savefig(bar_path, dpi=300, bbox_inches='tight')
    print(f"Saved bar chart to: {bar_path}")
    plt.close(fig1)
    
    # Difference heatmap
    fig2 = plot_difference_heatmap(comparison_df)
    heatmap_path = os.path.join(OUTPUT_DIR, 'difference_heatmap.png')
    fig2.savefig(heatmap_path, dpi=300, bbox_inches='tight')
    print(f"Saved heatmap to: {heatmap_path}")
    plt.close(fig2)
    
    # Print summary report
    print_summary_report(summary, comparison_df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print(f"All results saved to: {OUTPUT_DIR}")
    print("="*80)


if __name__ == "__main__":
    main()
