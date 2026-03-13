"""
Script to test composite measure as described in the paper.

Methodology (from paper lines 545-558):
1. Rank judgments by high-relevance centrality (descending, rank 1 = most relevant)
2. Rank judgments by low-relevance centrality (descending, rank 1 = most relevant)
3. Use dynamic threshold based on proportion of high-relevance ground truth:
   - For doctypebranch: proportion of Grand Chamber cases (doctypebranch=1)
   - For importance: proportion of Importance=1 judgments
4. Composite ranking: Top n% from high-relevance ranking, remaining from low-relevance ranking

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
OUTPUT_DIR = 'results/analysis/03_paper_composite'

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
def create_paper_composite_ranking(df, high_centrality, low_centrality, ground_truth):
    """
    Create composite ranking using paper's threshold-based method.
    
    From paper (lines 552-558):
    - Rank by high-relevance centrality (descending)
    - Calculate dynamic threshold based on proportion of high-relevance ground truth
    - Top n% from high-relevance ranking, rest from low-relevance ranking
    """
    n_total = len(df)
    
    # Calculate threshold based on proportion of high-relevance ground truth
    if ground_truth == 'doctypebranch':
        # Proportion of Grand Chamber cases (doctypebranch=1)
        n_high_relevance = (df[ground_truth] == 1).sum()
    elif ground_truth == 'importance':
        # Proportion of Importance=1 judgments
        n_high_relevance = (df[ground_truth] == 1).sum()
    else:
        raise ValueError(f"Unknown ground truth: {ground_truth}")
    
    threshold_proportion = n_high_relevance / n_total if n_total > 0 else 0
    n_threshold = int(threshold_proportion * n_total)
    
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
    
    # Calculate correlation with ground truth (negative because lower rank = higher relevance)
    corr, _ = stats.spearmanr(composite_ranks, df[ground_truth])
    
    return composite_ranks, threshold_proportion, corr


def analyze_network_with_combination(df, high_cent, low_cent, ground_truth):
    """Analyze a single network with a specific centrality combination."""
    results = {}
    
    composite_ranks, threshold, composite_corr = create_paper_composite_ranking(
        df, high_cent, low_cent, ground_truth
    )
    results['composite'] = {
        'correlation': abs(composite_corr),
        'threshold': threshold
    }
    
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


def test_combination_across_networks(high_cent, low_cent, combo_name):
    """Test a specific centrality combination across all networks."""
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
    
    unbalanced_dir = os.path.join(BASE_DIR, 'unbalanced')
    
    if not os.path.exists(unbalanced_dir):
        print("ERROR: Unbalanced directory not found")
        return results, detailed_results
    
    article_dirs = [d for d in os.listdir(unbalanced_dir) 
                   if os.path.isdir(os.path.join(unbalanced_dir, d)) 
                   and d.startswith('article_')]
    
    print(f"Found {len(article_dirs)} networks")
    
    for article_dir in sorted(article_dirs):
        unbalanced_path = os.path.join(unbalanced_dir, article_dir, 'total_df.csv')
        
        if not os.path.exists(unbalanced_path):
            continue
        
        try:
            unbalanced_df = pd.read_csv(unbalanced_path)
        except Exception as e:
            print(f"  Error loading {article_dir}: {e}")
            continue
        
        if high_cent not in unbalanced_df.columns or low_cent not in unbalanced_df.columns:
            print(f"  Skipping {article_dir}: missing centralities")
            continue
        
        # Process UNBALANCED network
        for ground_truth in GROUND_TRUTHS:
            if ground_truth not in unbalanced_df.columns:
                continue
            
            corr_results = analyze_network_with_combination(
                unbalanced_df, high_cent, low_cent, ground_truth
            )
            
            best_performer = find_best_performer(corr_results)
            if best_performer:
                results['unbalanced'][ground_truth][best_performer] += 1
                detailed_results['unbalanced'][ground_truth].append({
                    'network': article_dir,
                    'best_performer': best_performer,
                    'composite_corr': corr_results['composite']['correlation'],
                    'threshold': corr_results['composite']['threshold']
                })
        
        # Process BALANCED networks
        for network_type in ['importance', 'doctypebranch']:
            balanced_df = load_balanced_network(network_type, article_dir, unbalanced_df)
            
            if balanced_df is None:
                continue
            
            network_key = f'balanced-{network_type}'
            
            for ground_truth in GROUND_TRUTHS:
                if ground_truth not in balanced_df.columns:
                    continue
                
                corr_results = analyze_network_with_combination(
                    balanced_df, high_cent, low_cent, ground_truth
                )
                
                best_performer = find_best_performer(corr_results)
                if best_performer:
                    results[network_key][ground_truth][best_performer] += 1
                    detailed_results[network_key][ground_truth].append({
                        'network': article_dir,
                        'best_performer': best_performer,
                        'composite_corr': corr_results['composite']['correlation'],
                        'threshold': corr_results['composite']['threshold']
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
                
                # Sort by count, but keep composite at top if it has any wins
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
                ax.set_title(f'{combo_name}\n{network_type}\n{ground_truth}',
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
    
    all_results = {}
    
    # Test each combination
    for high_cent, low_cent, combo_name in COMBINATIONS_TO_TEST:
        results, detailed_results = test_combination_across_networks(
            high_cent, low_cent, combo_name
        )
        
        all_results[combo_name] = {
            'results': results,
            'detailed': detailed_results
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
