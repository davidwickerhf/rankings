"""
Script to manually test specific centrality combinations and generate performance graphs.
FIXED VERSION: Correctly handles balanced networks by matching to unbalanced centralities.

Usage:
    python test_centrality_combinations_fixed.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from collections import defaultdict
import json


# ==================== CONFIGURATION ====================
COMBINATIONS_TO_TEST = [
    ('in_degree_centrality', 'hits_hub', 'InDegree+HitsHub'),
    ('degree_centrality', 'in_degree_centrality', 'Degree+InDegree'),
    ('degree_centrality', 'pagerank', 'Degree+PageRank'),
]

BASE_DIR = 'results/fixed-merged-subarticles-edges/importance-merged-50-cutoff'
BALANCED_NETWORKS_DIR = 'networks/merged-article-edges'
GROUND_TRUTHS = ['importance', 'doctypebranch']
OUTPUT_DIR = 'results/fixed-merged-subarticles-edges/composite_manual_test_corrected'

CENTRALITIES = [
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


# ==================== COMPOSITE FUNCTIONS ====================
def normalize_centrality(values):
    """
    Normalize centrality values using percentile ranking.
    Lower values = higher importance (inverted scale).
    """
    non_zero = values[values != 0]
    if len(non_zero) == 0:
        return values
    
    ranks = pd.Series(index=non_zero.index)
    ranks.loc[non_zero.index] = non_zero.rank(pct=True, ascending=False)
    
    # Scale to 1-1000 range
    ranks = ranks * 999 + 1
    
    # Fill zeros with lowest importance
    ranks = ranks.reindex(values.index, fill_value=1000)
    return ranks


def weighted_combine(high, low, weight):
    """Combine using weighted geometric mean."""
    epsilon = 1e-10
    return np.power(high + epsilon, weight) * np.power(low + epsilon, (1-weight))


def create_composite_ranking(df, high_centrality, low_centrality, ground_truth):
    """
    Create composite ranking by optimizing weight parameter.
    
    Returns:
        tuple: (best_composite, best_weight, best_corr)
    """
    high_values = df[high_centrality]
    low_values = df[low_centrality]
    
    high_norm = normalize_centrality(high_values)
    low_norm = normalize_centrality(low_values)
    
    best_weight = None
    best_corr = float('-inf')
    best_composite = None
    
    # Try different weights
    for weight in np.arange(0.01, 1.00, 0.01):
        composite = weighted_combine(high_norm, low_norm, weight)
        
        # Calculate correlation with ground truth
        corr, _ = stats.spearmanr(composite, df[ground_truth])
        
        if corr > best_corr:
            best_corr = corr
            best_weight = weight
            best_composite = composite
    
    return best_composite, best_weight, best_corr


# ==================== ANALYSIS FUNCTIONS ====================
def analyze_network_with_combination(df, high_cent, low_cent, ground_truth):
    """
    Analyze a single network with a specific centrality combination.
    
    Returns:
        dict: Contains correlation for composite and all individual centralities
    """
    results = {}
    
    # Calculate composite
    composite, weight, composite_corr = create_composite_ranking(df, high_cent, low_cent, ground_truth)
    results['composite'] = {
        'correlation': abs(composite_corr),
        'weight': weight
    }
    
    # Calculate individual centrality correlations
    for centrality in CENTRALITIES:
        if centrality in df.columns:
            corr, _ = stats.spearmanr(df[centrality], df[ground_truth])
            results[centrality] = abs(corr)
    
    return results


def find_best_performer(correlations_dict):
    """Find which measure has the highest correlation."""
    if not correlations_dict:
        return None
    
    # Handle composite separately (it's a dict)
    composite_corr = correlations_dict.get('composite', {}).get('correlation', 0)
    
    best_name = 'composite'
    best_corr = composite_corr
    
    for name, value in correlations_dict.items():
        if name == 'composite':
            continue
        if value > best_corr:
            best_corr = value
            best_name = name
    
    return best_name


def load_balanced_network(network_set, article_dir, unbalanced_df):
    """
    Load balanced network nodes and match them to unbalanced centralities.
    
    Args:
        network_set: 'balanced-importance' or 'balanced-doctypebranch'
        article_dir: e.g., 'article_10'
        unbalanced_df: DataFrame with all centralities from unbalanced network
    
    Returns:
        DataFrame with centralities for balanced nodes only
    """
    # Map network_set to directory name
    balanced_dir_name = f"split-{network_set}"
    balanced_path = os.path.join(BALANCED_NETWORKS_DIR, balanced_dir_name, article_dir, 'nodes.json')
    
    if not os.path.exists(balanced_path):
        return None
    
    # Load balanced nodes
    import json
    with open(balanced_path, 'r') as f:
        balanced_nodes = json.load(f)
    
    # Extract ECLIs from balanced nodes
    balanced_eclis = [node['ecli'] for node in balanced_nodes if 'ecli' in node]
    
    if not balanced_eclis:
        return None
    
    # Filter unbalanced_df to only balanced nodes
    if 'ecli' not in unbalanced_df.columns:
        return None
    
    balanced_df = unbalanced_df[unbalanced_df['ecli'].isin(balanced_eclis)].copy()
    
    return balanced_df if len(balanced_df) > 0 else None


def test_combination_across_networks(high_cent, low_cent, combo_name):
    """
    Test a specific centrality combination across all networks.
    
    Returns:
        dict: Performance counts per network type and ground truth
    """
    print(f"\n{'='*80}")
    print(f"Testing combination: {combo_name}")
    print(f"  HIGH: {high_cent}")
    print(f"  LOW:  {low_cent}")
    print(f"{'='*80}")
    
    results = {
        'balanced-importance': {gt: defaultdict(int) for gt in GROUND_TRUTHS},
        'balanced-doctypebranch': {gt: defaultdict(int) for gt in GROUND_TRUTHS},
        'unbalanced': {gt: defaultdict(int) for gt in GROUND_TRUTHS},
    }
    
    detailed_results = {
        'balanced-importance': {gt: [] for gt in GROUND_TRUTHS},
        'balanced-doctypebranch': {gt: [] for gt in GROUND_TRUTHS},
        'unbalanced': {gt: [] for gt in GROUND_TRUTHS},
    }
    
    # First, process unbalanced networks
    unbalanced_dir = os.path.join(BASE_DIR, 'unbalanced')
    
    if not os.path.exists(unbalanced_dir):
        print("ERROR: Unbalanced directory not found")
        return results, detailed_results
    
    article_dirs = [d for d in os.listdir(unbalanced_dir) 
                   if os.path.isdir(os.path.join(unbalanced_dir, d)) 
                   and d.startswith('article_')]
    
    print(f"\nFound {len(article_dirs)} article networks")
    
    for article_dir in sorted(article_dirs):
        print(f"\nProcessing {article_dir}...")
        
        # Load unbalanced network
        unbalanced_path = os.path.join(unbalanced_dir, article_dir, 'total_df.csv')
        
        if not os.path.exists(unbalanced_path):
            print(f"  ⚠️  No total_df.csv for {article_dir}")
            continue
        
        try:
            unbalanced_df = pd.read_csv(unbalanced_path)
        except Exception as e:
            print(f"  ❌ Error loading {article_dir}: {e}")
            continue
        
        # Check if required centralities exist
        if high_cent not in unbalanced_df.columns or low_cent not in unbalanced_df.columns:
            print(f"  ⚠️  Missing required centralities")
            continue
        
        # Process UNBALANCED network
        print(f"  → Analyzing unbalanced network ({len(unbalanced_df)} nodes)")
        for ground_truth in GROUND_TRUTHS:
            if ground_truth not in unbalanced_df.columns:
                continue
            
            correlations = analyze_network_with_combination(unbalanced_df, high_cent, low_cent, ground_truth)
            best = find_best_performer(correlations)
            
            results['unbalanced'][ground_truth][best] += 1
            detailed_results['unbalanced'][ground_truth].append({
                'network': article_dir,
                'best': best,
                'composite_corr': correlations['composite']['correlation'],
                'composite_weight': correlations['composite']['weight']
            })
            print(f"    {ground_truth}: {best} (composite={correlations['composite']['correlation']:.4f})")
        
        # Process BALANCED networks
        for network_set in ['balanced-importance', 'balanced-doctypebranch']:
            balanced_df = load_balanced_network(network_set, article_dir, unbalanced_df)
            
            if balanced_df is None:
                continue
            
            print(f"  → Analyzing {network_set} ({len(balanced_df)} nodes)")
            
            for ground_truth in GROUND_TRUTHS:
                if ground_truth not in balanced_df.columns:
                    continue
                
                correlations = analyze_network_with_combination(balanced_df, high_cent, low_cent, ground_truth)
                best = find_best_performer(correlations)
                
                results[network_set][ground_truth][best] += 1
                detailed_results[network_set][ground_truth].append({
                    'network': article_dir,
                    'best': best,
                    'composite_corr': correlations['composite']['correlation'],
                    'composite_weight': correlations['composite']['weight']
                })
                print(f"    {ground_truth}: {best} (composite={correlations['composite']['correlation']:.4f})")
    
    return results, detailed_results


def plot_combination_results(all_results, combo_names):
    """
    Create comparison plots for all tested combinations.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    network_types = ['balanced-importance', 'balanced-doctypebranch', 'unbalanced']
    
    for network_type in network_types:
        for ground_truth in GROUND_TRUTHS:
            fig, axes = plt.subplots(1, len(combo_names), figsize=(8*len(combo_names), 8))
            if len(combo_names) == 1:
                axes = [axes]
            
            for idx, combo_name in enumerate(combo_names):
                ax = axes[idx]
                counts = all_results[combo_name][network_type][ground_truth]
                
                # Sort by count descending
                sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
                names = [item[0] for item in sorted_items]
                values = [item[1] for item in sorted_items]
                
                # Highlight composite
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
                
                ax.set_xlabel('Number of Networks', fontsize=14, fontweight='bold')
                ax.set_title(f'{combo_name}\n{network_type}\n{ground_truth}',
                            fontsize=16, fontweight='bold')
                ax.grid(axis='x', alpha=0.3)
                
                # Invert y-axis so best is on top
                ax.invert_yaxis()
            
            plt.tight_layout()
            filename = f'{OUTPUT_DIR}/comparison_{network_type}_{ground_truth}.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Saved: {filename}")
            plt.close()


def create_summary_table(all_results, combo_names):
    """Create a summary table comparing all combinations."""
    summary = []
    
    for combo_name in combo_names:
        for network_type in ['balanced-importance', 'balanced-doctypebranch', 'unbalanced']:
            for ground_truth in GROUND_TRUTHS:
                counts = all_results[combo_name][network_type][ground_truth]
                composite_wins = counts.get('composite', 0)
                total_networks = sum(counts.values())
                
                summary.append({
                    'Combination': combo_name,
                    'Network Type': network_type,
                    'Ground Truth': ground_truth,
                    'Composite Wins': composite_wins,
                    'Total Networks': total_networks,
                    'Win Rate': f"{(composite_wins/total_networks*100):.1f}%" if total_networks > 0 else "0%"
                })
    
    df = pd.DataFrame(summary)
    csv_path = f'{OUTPUT_DIR}/combination_summary.csv'
    df.to_csv(csv_path, index=False)
    print(f"\nSummary saved to: {csv_path}")
    
    return df


# ==================== MAIN ====================
def main():
    print("="*80)
    print("TESTING CENTRALITY COMBINATIONS (CORRECTED FOR BALANCED NETWORKS)")
    print("="*80)
    
    all_results = {}
    all_detailed = {}
    
    # Test each combination
    for high_cent, low_cent, combo_name in COMBINATIONS_TO_TEST:
        results, detailed = test_combination_across_networks(high_cent, low_cent, combo_name)
        all_results[combo_name] = results
        all_detailed[combo_name] = detailed
        
        # Print summary for this combination
        print(f"\n{'='*80}")
        print(f"{combo_name} Summary:")
        print(f"{'='*80}")
        for network_type in ['balanced-importance', 'balanced-doctypebranch', 'unbalanced']:
            for gt in GROUND_TRUTHS:
                counts = results[network_type][gt]
                composite_wins = counts.get('composite', 0)
                total = sum(counts.values())
                if total > 0:
                    print(f"  {network_type:25} - {gt:15}: Composite won {composite_wins:2}/{total:2} ({composite_wins/total*100:5.1f}%)")
    
    # Create comparison plots
    combo_names = [name for _, _, name in COMBINATIONS_TO_TEST]
    plot_combination_results(all_results, combo_names)
    
    # Create summary table
    summary_df = create_summary_table(all_results, combo_names)
    print("\n" + "="*80)
    print("SUMMARY TABLE:")
    print("="*80)
    print(summary_df.to_string(index=False))
    
    # Save detailed results to JSON
    json_path = f'{OUTPUT_DIR}/detailed_results.json'
    with open(json_path, 'w') as f:
        json.dump(all_detailed, f, indent=2)
    print(f"\nDetailed results saved to: {json_path}")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print(f"Results saved to: {OUTPUT_DIR}")
    print("="*80)


if __name__ == "__main__":
    main()
