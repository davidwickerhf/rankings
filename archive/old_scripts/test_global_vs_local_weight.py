"""
Test global weight (same across all networks) vs. local weight (per-network optimization).

This validates the claim in the paper about the "alternative evaluation" approach.
"""

import os
import pandas as pd
import numpy as np
from scipy import stats
from collections import defaultdict
import json


BASE_DIR = 'results/fixed-merged-subarticles-edges/importance-merged-50-cutoff'
BALANCED_NETWORKS_DIR = 'networks/merged-article-edges'
GROUND_TRUTHS = ['importance', 'doctypebranch']

# Test Degree+Eigenvector (best combination)
HIGH_CENT = 'degree_centrality'
LOW_CENT = 'eigenvector_centrality'

CENTRALITIES = [
    'degree_centrality', 'in_degree_centrality', 'out_degree_centrality',
    'betweenness_centrality', 'closeness_centrality', 'core_number',
    'relative_in_degree_centrality', 'eigenvector_centrality', 'pagerank',
    'hits_hub', 'hits_authority', 'harmonic_centrality', 'disruption'
]


def normalize_centrality(values):
    """Normalize using percentile ranking."""
    non_zero = values[values != 0]
    if len(non_zero) == 0:
        return values
    ranks = pd.Series(index=non_zero.index)
    ranks.loc[non_zero.index] = non_zero.rank(pct=True, ascending=False)
    ranks = ranks * 999 + 1
    ranks = ranks.reindex(values.index, fill_value=1000)
    return ranks


def weighted_combine(high, low, weight):
    """Combine using weighted geometric mean."""
    epsilon = 1e-10
    return np.power(high + epsilon, weight) * np.power(low + epsilon, (1-weight))


def find_optimal_weight(df, high_cent, low_cent, ground_truth):
    """Find optimal weight for a single network."""
    high_values = df[high_cent]
    low_values = df[low_cent]
    
    high_norm = normalize_centrality(high_values)
    low_norm = normalize_centrality(low_values)
    
    best_weight = None
    best_corr = float('-inf')
    
    for weight in np.arange(0.01, 1.00, 0.01):
        composite = weighted_combine(high_norm, low_norm, weight)
        corr, _ = stats.spearmanr(composite, df[ground_truth])
        
        if corr > best_corr:
            best_corr = corr
            best_weight = weight
    
    return best_weight, best_corr


def evaluate_with_weight(df, high_cent, low_cent, ground_truth, weight):
    """Evaluate composite with a specific weight."""
    high_values = df[high_cent]
    low_values = df[low_cent]
    
    high_norm = normalize_centrality(high_values)
    low_norm = normalize_centrality(low_values)
    
    composite = weighted_combine(high_norm, low_norm, weight)
    composite_corr, _ = stats.spearmanr(composite, df[ground_truth])
    
    # Get all individual correlations
    individual_corrs = {}
    for centrality in CENTRALITIES:
        if centrality in df.columns:
            corr, _ = stats.spearmanr(df[centrality], df[ground_truth])
            individual_corrs[centrality] = abs(corr)
    
    # Check if composite wins
    composite_abs = abs(composite_corr)
    composite_wins = all(composite_abs > corr for corr in individual_corrs.values())
    
    return composite_wins, composite_abs


def load_balanced_network(network_set, article_dir, unbalanced_df):
    """Load balanced network."""
    balanced_dir_name = f"split-{network_set}"
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


def main():
    print("="*80)
    print("TESTING GLOBAL vs LOCAL WEIGHT OPTIMIZATION")
    print("Combination: Degree + Eigenvector")
    print("="*80)
    
    # Collect all networks
    all_networks = []
    
    unbalanced_dir = os.path.join(BASE_DIR, 'unbalanced')
    article_dirs = [d for d in os.listdir(unbalanced_dir) 
                   if os.path.isdir(os.path.join(unbalanced_dir, d)) 
                   and d.startswith('article_')]
    
    print(f"\nLoading {len(article_dirs)} networks...")
    
    for article_dir in sorted(article_dirs):
        unbalanced_path = os.path.join(unbalanced_dir, article_dir, 'total_df.csv')
        
        if not os.path.exists(unbalanced_path):
            continue
        
        try:
            unbalanced_df = pd.read_csv(unbalanced_path)
        except:
            continue
        
        if HIGH_CENT not in unbalanced_df.columns or LOW_CENT not in unbalanced_df.columns:
            continue
        
        # Process all network types
        for network_type in ['unbalanced', 'balanced-importance', 'balanced-doctypebranch']:
            if network_type == 'unbalanced':
                df = unbalanced_df
            else:
                df = load_balanced_network(network_type, article_dir, unbalanced_df)
                if df is None:
                    continue
            
            for ground_truth in GROUND_TRUTHS:
                if ground_truth not in df.columns:
                    continue
                
                all_networks.append({
                    'network': article_dir,
                    'type': network_type,
                    'ground_truth': ground_truth,
                    'df': df
                })
    
    print(f"Total networks loaded: {len(all_networks)}")
    
    # Step 1: Find optimal weights for each network (LOCAL)
    print("\n" + "-"*80)
    print("STEP 1: Finding optimal weight per network (LOCAL approach)")
    print("-"*80)
    
    local_results = []
    for network_data in all_networks:
        optimal_weight, _ = find_optimal_weight(
            network_data['df'], 
            HIGH_CENT, 
            LOW_CENT, 
            network_data['ground_truth']
        )
        network_data['optimal_weight'] = optimal_weight
        local_results.append(optimal_weight)
    
    print(f"Optimal weights range: [{min(local_results):.2f}, {max(local_results):.2f}]")
    print(f"Mean optimal weight: {np.mean(local_results):.2f}")
    print(f"Median optimal weight: {np.median(local_results):.2f}")
    
    # Step 2: Evaluate LOCAL approach (per-network optimization)
    print("\n" + "-"*80)
    print("STEP 2: Evaluating LOCAL approach (per-network optimal weights)")
    print("-"*80)
    
    local_wins = 0
    for network_data in all_networks:
        wins, _ = evaluate_with_weight(
            network_data['df'],
            HIGH_CENT,
            LOW_CENT,
            network_data['ground_truth'],
            network_data['optimal_weight']
        )
        if wins:
            local_wins += 1
    
    local_win_rate = local_wins / len(all_networks) * 100
    print(f"LOCAL wins: {local_wins}/{len(all_networks)} ({local_win_rate:.1f}%)")
    
    # Step 3: Test GLOBAL approach with different fixed weights
    print("\n" + "-"*80)
    print("STEP 3: Testing GLOBAL approach (single fixed weight for all networks)")
    print("-"*80)
    
    # Test with median optimal weight as global weight
    global_weight = np.median(local_results)
    print(f"\nUsing global weight = {global_weight:.2f} (median of optimal weights)")
    
    global_wins = 0
    for network_data in all_networks:
        wins, _ = evaluate_with_weight(
            network_data['df'],
            HIGH_CENT,
            LOW_CENT,
            network_data['ground_truth'],
            global_weight
        )
        if wins:
            global_wins += 1
    
    global_win_rate = global_wins / len(all_networks) * 100
    print(f"GLOBAL wins: {global_wins}/{len(all_networks)} ({global_win_rate:.1f}%)")
    
    # Step 4: Try other global weights
    print("\n" + "-"*80)
    print("STEP 4: Testing alternative global weights")
    print("-"*80)
    
    test_weights = [0.25, 0.50, 0.60, 0.75, np.mean(local_results)]
    
    for test_weight in test_weights:
        wins = 0
        for network_data in all_networks:
            w, _ = evaluate_with_weight(
                network_data['df'],
                HIGH_CENT,
                LOW_CENT,
                network_data['ground_truth'],
                test_weight
            )
            if w:
                wins += 1
        
        win_rate = wins / len(all_networks) * 100
        print(f"Weight = {test_weight:.2f}: {wins}/{len(all_networks)} ({win_rate:.1f}%)")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"LOCAL (per-network optimization): {local_wins}/{len(all_networks)} ({local_win_rate:.1f}%)")
    print(f"GLOBAL (median weight={global_weight:.2f}): {global_wins}/{len(all_networks)} ({global_win_rate:.1f}%)")
    print(f"Difference: {local_win_rate - global_win_rate:.1f} percentage points")
    
    # Validate paper claim
    expected_reduction = (15, 20)  # Paper claims 15-20 pp reduction
    actual_reduction = local_win_rate - global_win_rate
    
    print(f"\nPaper claim: Global approach reduces win rate by ~15-20 pp")
    print(f"Actual reduction: {actual_reduction:.1f} pp")
    
    if expected_reduction[0] <= actual_reduction <= expected_reduction[1]:
        print("✓ Paper claim VALIDATED")
    else:
        print(f"⚠ Paper claim needs adjustment (actual: {actual_reduction:.1f} pp)")
    
    # Check if global still wins ~25% as claimed
    print(f"\nPaper claim: Global approach still wins ~25% of cases")
    print(f"Actual: {global_win_rate:.1f}%")
    
    if 20 <= global_win_rate <= 30:
        print("✓ Paper claim VALIDATED")
    else:
        print(f"⚠ Paper claim needs adjustment (actual: {global_win_rate:.1f}%)")


if __name__ == "__main__":
    main()
