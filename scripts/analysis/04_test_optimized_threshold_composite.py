"""
Script to test composite measure with OPTIMIZED UNIVERSAL THRESHOLD.

Key difference from 03_test_paper_composite.py:
- Paper approach: Uses ground-truth proportion per network (circular, requires knowing answer)
- This approach: Finds optimal threshold via grid search, applies universally

Methodology:
1. For each combination, test thresholds from 0.01 to 0.99 in 0.05 increments
2. Find threshold that maximizes composite wins across all networks
3. Apply that optimal threshold universally to all networks
4. Compare against paper's dynamic threshold approach

Combinations to test:
1. PageRank (high) + Degree (low)
2. Degree (high) + Eigenvector (low)
3. Degree (high) + In-Degree (low)
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
    ('pagerank', 'degree_centrality', 'PageRank+Degree'),
    ('degree_centrality', 'eigenvector_centrality', 'Degree+Eigenvector'),
    ('degree_centrality', 'in_degree_centrality', 'Degree+InDegree'),
]

BASE_DIR = 'results/fixed-merged-subarticles-edges/importance-merged-50-cutoff'
BALANCED_NETWORKS_DIR = 'networks/merged-article-edges'
GROUND_TRUTHS = ['importance', 'doctypebranch']
OUTPUT_DIR = 'results/analysis/04_optimized_threshold_composite'

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
def create_threshold_composite_ranking(df, high_centrality, low_centrality, ground_truth, threshold):
    """
    Create composite ranking using a FIXED threshold.
    
    Args:
        threshold: Proportion of judgments to take from high-relevance ranking (0.0 to 1.0)
    """
    n_total = len(df)
    n_threshold = int(threshold * n_total)
    
    # Rank by high-relevance centrality (higher centrality = higher rank = lower rank number)
    high_ranks = df[high_centrality].rank(method='first', ascending=False)
    
    # Rank by low-relevance centrality (higher centrality = higher rank = lower rank number)
    low_ranks = df[low_centrality].rank(method='first', ascending=False)
    
    # Create composite ranking:
    # - Top n_threshold judgments: use high-relevance ranking
    # - Remaining judgments: use low-relevance ranking (shifted by n_threshold)
    composite_ranks = pd.Series(index=df.index, dtype=float)
    
    # Get indices of top n_threshold from high-relevance ranking
    top_high = high_ranks.nsmallest(n_threshold).index
    
    # Assign ranks
    composite_ranks.loc[top_high] = high_ranks.loc[top_high]
    
    # For remaining judgments, use low-relevance ranking but shift by n_threshold
    remaining = df.index.difference(top_high)
    if len(remaining) > 0:
        # Rank the remaining items by low_centrality
        remaining_low_ranks = low_ranks.loc[remaining].rank(method='first', ascending=True)
        composite_ranks.loc[remaining] = n_threshold + remaining_low_ranks
    
    # Calculate correlation with ground truth
    corr, _ = stats.spearmanr(composite_ranks, df[ground_truth])
    
    return composite_ranks, abs(corr)


def analyze_network_with_threshold(df, high_cent, low_cent, ground_truth, threshold):
    """Analyze a single network with a specific threshold."""
    results = {}
    
    composite_ranks, composite_corr = create_threshold_composite_ranking(
        df, high_cent, low_cent, ground_truth, threshold
    )
    results['composite'] = composite_corr
    
    # Calculate correlations for individual centralities
    for centrality in CENTRALITIES:
        if centrality in df.columns:
            corr, _ = stats.spearmanr(df[centrality], df[ground_truth])
            results[centrality] = abs(corr)
    
    return results


def find_best_performer(correlations_dict):
    """Find which measure has the highest correlation."""
    if not correlations_dict:
        return None
    
    best_name = max(correlations_dict.items(), key=lambda x: x[1])[0]
    return best_name


def load_balanced_network(network_set, article_dir, unbalanced_df):
    """Load balanced network nodes and match to unbalanced centralities."""
    balanced_dir_name = f"split-balanced-{network_set}"
    balanced_path = os.path.join(BALANCED_NETWORKS_DIR, balanced_dir_name, article_dir, 'nodes.json')
    
    if not os.path.exists(balanced_path):
        return None
    
    with open(balanced_path, 'r') as f:
        balanced_nodes = json.load(f)
    
    balanced_eclis = [node['ecli'] for node in balanced_nodes if 'ecli' in node]
    
    if not balanced_eclis or 'ecli' not in unbalanced_df.columns:
        return None
    
    balanced_df = unbalanced_df[unbalanced_df['ecli'].isin(balanced_eclis)].copy()
    
    return balanced_df if len(balanced_df) > 0 else None


def load_all_networks():
    """Load all networks once for optimization."""
    all_networks = {
        'unbalanced': {},
        'balanced-importance': {},
        'balanced-doctypebranch': {}
    }
    
    unbalanced_dir = os.path.join(BASE_DIR, 'unbalanced')
    
    if not os.path.exists(unbalanced_dir):
        print("ERROR: Unbalanced directory not found")
        return all_networks
    
    article_dirs = [d for d in os.listdir(unbalanced_dir) 
                   if os.path.isdir(os.path.join(unbalanced_dir, d)) 
                   and d.startswith('article_')]
    
    print(f"Loading {len(article_dirs)} networks...")
    
    for article_dir in sorted(article_dirs):
        unbalanced_path = os.path.join(unbalanced_dir, article_dir, 'total_df.csv')
        
        if not os.path.exists(unbalanced_path):
            continue
        
        try:
            unbalanced_df = pd.read_csv(unbalanced_path, low_memory=False)
            all_networks['unbalanced'][article_dir] = unbalanced_df
            
            # Load balanced networks
            for network_type in ['importance', 'doctypebranch']:
                balanced_df = load_balanced_network(network_type, article_dir, unbalanced_df)
                if balanced_df is not None:
                    network_key = f'balanced-{network_type}'
                    all_networks[network_key][article_dir] = balanced_df
                    
        except Exception as e:
            print(f"  Error loading {article_dir}: {e}")
            continue
    
    print(f"Loaded: {len(all_networks['unbalanced'])} unbalanced, "
          f"{len(all_networks['balanced-importance'])} balanced-importance, "
          f"{len(all_networks['balanced-doctypebranch'])} balanced-doctypebranch")
    
    return all_networks


def optimize_threshold(all_networks, high_cent, low_cent, ground_truth):
    """Find optimal threshold by testing multiple values."""
    print(f"\n  Optimizing threshold for {ground_truth}...")
    
    # Test thresholds from 0.05 to 0.95 in 0.05 increments
    thresholds = np.arange(0.05, 1.00, 0.05)
    threshold_wins = defaultdict(int)
    
    for threshold in thresholds:
        wins = 0
        total = 0
        
        # Test across all network types
        for network_type in ['unbalanced', 'balanced-importance', 'balanced-doctypebranch']:
            for article_dir, df in all_networks[network_type].items():
                if high_cent not in df.columns or low_cent not in df.columns:
                    continue
                if ground_truth not in df.columns:
                    continue
                
                correlations = analyze_network_with_threshold(df, high_cent, low_cent, ground_truth, threshold)
                best = find_best_performer(correlations)
                
                if best == 'composite':
                    wins += 1
                total += 1
        
        threshold_wins[threshold] = wins
        win_rate = (wins / total * 100) if total > 0 else 0
        print(f"    Threshold {threshold:.2f}: {wins}/{total} wins ({win_rate:.1f}%)")
    
    # Find best threshold
    best_threshold = max(threshold_wins.items(), key=lambda x: x[1])[0]
    best_wins = threshold_wins[best_threshold]
    
    print(f"  --> Optimal threshold: {best_threshold:.2f} ({best_wins} total wins)")
    
    return best_threshold, threshold_wins


def test_with_optimal_threshold(all_networks, high_cent, low_cent, combo_name, optimal_thresholds):
    """Test combination using optimal thresholds."""
    print(f"\n{'='*80}")
    print(f"Testing: {combo_name}")
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
    
    for network_type in ['unbalanced', 'balanced-importance', 'balanced-doctypebranch']:
        for article_dir, df in all_networks[network_type].items():
            if high_cent not in df.columns or low_cent not in df.columns:
                continue
            
            for ground_truth in GROUND_TRUTHS:
                if ground_truth not in df.columns:
                    continue
                
                threshold = optimal_thresholds[ground_truth]
                correlations = analyze_network_with_threshold(df, high_cent, low_cent, ground_truth, threshold)
                best = find_best_performer(correlations)
                
                results[network_type][ground_truth][best] += 1
                detailed_results[network_type][ground_truth].append({
                    'network': article_dir,
                    'best_performer': best,
                    'composite_corr': correlations['composite'],
                    'threshold': threshold
                })
    
    return results, detailed_results


def print_summary(results):
    """Print summary of results."""
    print(f"\n{'='*80}")
    for network_type in ['balanced-importance', 'balanced-doctypebranch', 'unbalanced']:
        for ground_truth in GROUND_TRUTHS:
            counts = results[network_type][ground_truth]
            if not counts:
                continue
            
            total = sum(counts.values())
            composite_wins = counts.get('composite', 0)
            win_rate = (composite_wins / total * 100) if total > 0 else 0
            
            print(f"  {network_type:25s} - {ground_truth:15s}: Composite won {composite_wins:2d}/{total:2d} ({win_rate:5.1f}%)")


def plot_combination_results(all_results, combo_names):
    """Create comparison plots for all tested combinations."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    network_types = ['balanced-importance', 'balanced-doctypebranch', 'unbalanced']
    
    for network_type in network_types:
        for ground_truth in GROUND_TRUTHS:
            fig, axes = plt.subplots(1, len(combo_names), figsize=(8*len(combo_names), 8))
            if len(combo_names) == 1:
                axes = [axes]
            
            for idx, combo_name in enumerate(combo_names):
                ax = axes[idx]
                counts = all_results[combo_name]['results'][network_type][ground_truth]
                
                # Create full list including all centralities and composite
                all_measures = ['composite'] + CENTRALITIES
                count_dict = {measure: counts.get(measure, 0) for measure in all_measures}
                
                # Sort by count
                sorted_items = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
                names = [item[0] for item in sorted_items]
                values = [item[1] for item in sorted_items]
                
                colors = ['#ff6b6b' if name == 'composite' else '#4ecdc4' for name in names]
                
                bars = ax.barh(names, values, color=colors)
                
                for bar in bars:
                    width = bar.get_width()
                    if width > 0:
                        ax.text(width, bar.get_y() + bar.get_height()/2.,
                               f'{int(width)}',
                               ha='left', va='center',
                               fontsize=12, fontweight='bold')
                
                ax.set_xlabel('Number of Networks', fontsize=14, fontweight='bold')
                
                # Add optimal threshold to title with proper line breaks
                opt_threshold = all_results[combo_name]['optimal_thresholds'][ground_truth]
                ax.set_title(f'{combo_name}\n{network_type}\n{ground_truth}\n(threshold={opt_threshold:.2f})',
                            fontsize=14, fontweight='bold', pad=10)
                ax.grid(axis='x', alpha=0.3)
                ax.invert_yaxis()
            
            plt.tight_layout(pad=2.0, w_pad=3.0)
            filename = f'{OUTPUT_DIR}/comparison_{network_type}_{ground_truth}.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Saved: {filename}")
            plt.close()


def save_summary_table(all_results):
    """Save summary table of all combinations."""
    rows = []
    
    for combo_name in [combo[2] for combo in COMBINATIONS_TO_TEST]:
        if combo_name not in all_results:
            continue
        
        results = all_results[combo_name]['results']
        optimal_thresholds = all_results[combo_name]['optimal_thresholds']
        
        for network_type in ['balanced-importance', 'balanced-doctypebranch', 'unbalanced']:
            for ground_truth in GROUND_TRUTHS:
                counts = results[network_type][ground_truth]
                total = sum(counts.values())
                composite_wins = counts.get('composite', 0)
                win_rate = f"{(composite_wins / total * 100):.1f}%" if total > 0 else "0.0%"
                
                rows.append({
                    'Combination': combo_name,
                    'Network Type': network_type,
                    'Ground Truth': ground_truth,
                    'Optimal Threshold': f"{optimal_thresholds[ground_truth]:.2f}",
                    'Composite Wins': composite_wins,
                    'Total Networks': total,
                    'Win Rate': win_rate
                })
    
    summary_df = pd.DataFrame(rows)
    output_path = os.path.join(OUTPUT_DIR, 'combination_summary.csv')
    summary_df.to_csv(output_path, index=False)
    print(f"\nSummary saved to: {output_path}")
    
    return summary_df


def main():
    """Main execution function."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load all networks once
    all_networks = load_all_networks()
    
    all_results = {}
    
    # Test each combination
    for high_cent, low_cent, combo_name in COMBINATIONS_TO_TEST:
        print(f"\n{'='*80}")
        print(f"OPTIMIZING: {combo_name}")
        print(f"{'='*80}")
        
        # Optimize threshold separately for each ground truth
        optimal_thresholds = {}
        threshold_details = {}
        
        for ground_truth in GROUND_TRUTHS:
            opt_threshold, threshold_wins = optimize_threshold(
                all_networks, high_cent, low_cent, ground_truth
            )
            optimal_thresholds[ground_truth] = opt_threshold
            threshold_details[ground_truth] = threshold_wins
        
        # Test with optimal thresholds
        results, detailed_results = test_with_optimal_threshold(
            all_networks, high_cent, low_cent, combo_name, optimal_thresholds
        )
        
        all_results[combo_name] = {
            'results': results,
            'detailed': detailed_results,
            'optimal_thresholds': optimal_thresholds,
            'threshold_optimization': threshold_details
        }
        
        print_summary(results)
    
    # Save detailed results
    detailed_output = os.path.join(OUTPUT_DIR, 'detailed_results.json')
    with open(detailed_output, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nDetailed results saved to: {detailed_output}")
    
    # Create comparison plots
    combo_names = [combo[2] for combo in COMBINATIONS_TO_TEST]
    plot_combination_results(all_results, combo_names)
    
    # Save and display summary table
    summary_df = save_summary_table(all_results)
    print("\n" + "="*80)
    print("SUMMARY TABLE:")
    print("="*80)
    print(summary_df.to_string(index=False))
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print(f"Results saved to: {OUTPUT_DIR}")
    print("="*80)


if __name__ == "__main__":
    main()
