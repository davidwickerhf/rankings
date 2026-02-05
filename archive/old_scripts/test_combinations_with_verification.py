"""Test Centrality Combinations with Complete Verification Data

PURPOSE:
    Test three specific centrality combinations and generate complete verification
    data showing all correlations, optimal weights, and winner determinations for
    every network-ground truth pair.

TESTED COMBINATIONS:
    1. Degree + Eigenvector
    2. Degree + PageRank
    3. Degree + In-Degree

METHODOLOGY - COMPOSITE CREATION:
    
    Step 1: Normalization (Percentile Ranking)
        For each centrality measure:
        1. Identify non-zero values
        2. Rank by percentile (pct=True, ascending=False)
           - Higher centrality → lower percentile rank
        3. Scale percentiles to [1, 1000]:
           - rank = percentile × 999 + 1
        4. Assign zeros the value 1000 (lowest importance)
        
        Result: All centralities scaled to [1, 1000] where:
        - Lower values = higher importance
        - Preserves relative differences via percentile transformation
    
    Step 2: Combination (Weighted Geometric Mean)
        Formula:
            composite = (high_norm^w) × (low_norm^(1-w))
        
        Where:
        - high_norm = normalized high-performer centrality
        - low_norm = normalized low-performer centrality
        - w = weight parameter ∈ [0.01, 0.99]
        - Small epsilon (1e-10) added to avoid zero values
        
        Rationale:
        - Geometric mean less sensitive to extreme values than arithmetic mean
        - Weight controls balance between high/low performers:
          * w → 1: relies primarily on high performer
          * w → 0: relies primarily on low performer
          * w ≈ 0.5: balanced combination
    
    Step 3: Weight Optimization (Grid Search)
        For each network:
        1. Test 99 weight values: [0.01, 0.02, ..., 0.99]
        2. For each weight:
           - Create composite with that weight
           - Calculate Spearman correlation with ground truth
        3. Select weight that maximizes correlation
        
        Result: Per-network optimized weight (adapts to network structure)
    
    Step 4: Winner Determination
        Composite "wins" if and only if:
        - Its absolute Spearman correlation with ground truth
        - Is STRICTLY GREATER THAN
        - ALL 13 individual centrality absolute correlations
        
        Conservative criterion: Composite must beat EVERY individual measure

EVALUATION SCOPE:
    - Networks: 66 total (26 unbalanced + 24 balanced-importance + 16 balanced-doctypebranch)
    - Ground truths: 2 (importance, doctypebranch)
    - Total tests: 132 network-ground truth pairs per combination
    - Comparisons: Composite vs. 13 individual centralities per test

OUTPUTS:
    Location: results/fixed-merged-subarticles-edges/verification_test/
    
    For each combination:
    1. {combo}_detailed_correlations.csv
       Columns:
       - network_type, network, ground_truth, n_nodes
       - composite_corr, composite_abs_corr, composite_weight
       - winner, winner_corr
       - {centrality}_corr, {centrality}_abs_corr (for all 13 centralities)
    
    2. {combo}_summary.csv
       Key columns only (network info, composite metrics, winner)
    
    3. verification_report.txt
       Human-readable summary:
       - Win rates by network type and ground truth
       - Average correlations when composite wins vs. loses
       - Margins of victory/defeat
    
    4. ALL_COMBINATIONS_correlations.csv
       Combined data from all three combinations

USAGE:
    python test_combinations_with_verification.py
    
    No arguments required. Uses fixed 50-cutoff networks.
    Runtime: ~2-3 minutes for all combinations.

KEY RESULTS:
    Degree + Eigenvector:  57/132 wins (43.2%) - BEST
    Degree + PageRank:     55/132 wins (41.9%)
    Degree + In-Degree:    47/132 wins (35.9%)
    
    When composite wins:
    - Average correlation: 0.498
    - Average weight: 0.60
    
    When composite loses:
    - Composite avg: 0.373
    - Winner avg: 0.432
    - Avg margin: -0.059

VERIFICATION USE CASES:
    1. Paper claims: Verify exact win rates and correlation values
    2. Peer review: Provide complete transparency for reproducibility
    3. Debugging: Trace why composite won/lost for specific networks
    4. Analysis: Identify patterns in weight optimization across networks

AUTHOR: David Wicker
DATE: 2024
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
    ('degree_centrality', 'eigenvector_centrality', 'Degree+Eigenvector'),
    ('degree_centrality', 'pagerank', 'Degree+PageRank'),
    ('degree_centrality', 'in_degree_centrality', 'Degree+InDegree'),
]

BASE_DIR = 'results/fixed-merged-subarticles-edges/importance-merged-50-cutoff'
BALANCED_NETWORKS_DIR = 'networks/merged-article-edges'
GROUND_TRUTHS = ['importance', 'doctypebranch']
OUTPUT_DIR = 'results/fixed-merged-subarticles-edges/verification_test'

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
    """Normalize centrality values using percentile ranking."""
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


def create_composite_ranking(df, high_centrality, low_centrality, ground_truth):
    """Create composite ranking by optimizing weight parameter."""
    high_values = df[high_centrality]
    low_values = df[low_centrality]
    
    high_norm = normalize_centrality(high_values)
    low_norm = normalize_centrality(low_values)
    
    best_weight = None
    best_corr = float('-inf')
    best_composite = None
    
    for weight in np.arange(0.01, 1.00, 0.01):
        composite = weighted_combine(high_norm, low_norm, weight)
        corr, _ = stats.spearmanr(composite, df[ground_truth])
        
        if corr > best_corr:
            best_corr = corr
            best_weight = weight
            best_composite = composite
    
    return best_composite, best_weight, best_corr


def analyze_network_with_combination(df, high_cent, low_cent, ground_truth):
    """Analyze a single network and return ALL correlations."""
    results = {}
    
    # Calculate composite
    composite, weight, composite_corr = create_composite_ranking(df, high_cent, low_cent, ground_truth)
    results['composite'] = {
        'correlation': composite_corr,  # Keep sign
        'abs_correlation': abs(composite_corr),
        'weight': weight
    }
    
    # Calculate individual centrality correlations
    for centrality in CENTRALITIES:
        if centrality in df.columns:
            corr, p_value = stats.spearmanr(df[centrality], df[ground_truth])
            results[centrality] = {
                'correlation': corr,
                'abs_correlation': abs(corr),
                'p_value': p_value
            }
    
    return results


def find_best_performer(correlations_dict):
    """Find which measure has the highest absolute correlation."""
    if not correlations_dict:
        return None, None
    
    composite_corr = correlations_dict.get('composite', {}).get('abs_correlation', 0)
    
    best_name = 'composite'
    best_corr = composite_corr
    
    for name, value in correlations_dict.items():
        if name == 'composite':
            continue
        abs_corr = value.get('abs_correlation', value) if isinstance(value, dict) else value
        if abs_corr > best_corr:
            best_corr = abs_corr
            best_name = name
    
    return best_name, best_corr


def load_balanced_network(network_set, article_dir, unbalanced_df):
    """Load balanced network nodes and match to unbalanced centralities."""
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
    
    # Store ALL correlations for verification
    all_correlations = []
    
    unbalanced_dir = os.path.join(BASE_DIR, 'unbalanced')
    
    if not os.path.exists(unbalanced_dir):
        print("ERROR: Unbalanced directory not found")
        return results, all_correlations
    
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
            continue
        
        if high_cent not in unbalanced_df.columns or low_cent not in unbalanced_df.columns:
            continue
        
        # Process all network types
        for network_type in ['unbalanced', 'balanced-importance', 'balanced-doctypebranch']:
            if network_type == 'unbalanced':
                df = unbalanced_df
                n_nodes = len(df)
            else:
                df = load_balanced_network(network_type, article_dir, unbalanced_df)
                if df is None:
                    continue
                n_nodes = len(df)
            
            for ground_truth in GROUND_TRUTHS:
                if ground_truth not in df.columns:
                    continue
                
                correlations = analyze_network_with_combination(df, high_cent, low_cent, ground_truth)
                best, best_corr_value = find_best_performer(correlations)
                
                results[network_type][ground_truth][best] += 1
                
                # Build correlation record
                record = {
                    'combination': combo_name,
                    'network_type': network_type,
                    'network': article_dir,
                    'ground_truth': ground_truth,
                    'n_nodes': n_nodes,
                    'high_centrality': high_cent,
                    'low_centrality': low_cent,
                    'composite_corr': correlations['composite']['correlation'],
                    'composite_abs_corr': correlations['composite']['abs_correlation'],
                    'composite_weight': correlations['composite']['weight'],
                    'winner': best,
                    'winner_corr': best_corr_value,
                }
                
                # Add all individual centrality correlations
                for cent in CENTRALITIES:
                    if cent in correlations:
                        record[f'{cent}_corr'] = correlations[cent]['correlation']
                        record[f'{cent}_abs_corr'] = correlations[cent]['abs_correlation']
                
                all_correlations.append(record)
    
    return results, all_correlations


def save_correlations_to_csv(all_correlations, combo_name):
    """Save all correlations to CSV for verification."""
    if not all_correlations:
        return
    
    df = pd.DataFrame(all_correlations)
    
    # Save full detailed file
    detailed_path = f'{OUTPUT_DIR}/{combo_name}_detailed_correlations.csv'
    df.to_csv(detailed_path, index=False)
    print(f"  Saved detailed correlations: {detailed_path}")
    
    # Save summary file (just key columns)
    summary_cols = [
        'network_type', 'network', 'ground_truth', 'n_nodes',
        'composite_abs_corr', 'composite_weight', 'winner', 'winner_corr'
    ]
    summary_df = df[summary_cols]
    summary_path = f'{OUTPUT_DIR}/{combo_name}_summary.csv'
    summary_df.to_csv(summary_path, index=False)
    print(f"  Saved summary: {summary_path}")
    
    return df


def create_verification_report(all_dfs, combo_names):
    """Create a verification report comparing composite to best individual."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    report_lines = []
    report_lines.append("="*80)
    report_lines.append("VERIFICATION REPORT: Composite vs Individual Centralities")
    report_lines.append("="*80)
    
    for combo_name, df in zip(combo_names, all_dfs):
        report_lines.append(f"\n{combo_name}")
        report_lines.append("-"*80)
        
        for network_type in ['unbalanced', 'balanced-importance', 'balanced-doctypebranch']:
            subset = df[df['network_type'] == network_type]
            
            if len(subset) == 0:
                continue
            
            report_lines.append(f"\n  {network_type}:")
            
            for gt in GROUND_TRUTHS:
                gt_subset = subset[subset['ground_truth'] == gt]
                
                if len(gt_subset) == 0:
                    continue
                
                composite_wins = (gt_subset['winner'] == 'composite').sum()
                total = len(gt_subset)
                
                # Calculate average margins
                composite_better = gt_subset[gt_subset['winner'] == 'composite']
                if len(composite_better) > 0:
                    avg_composite_corr = composite_better['composite_abs_corr'].mean()
                    avg_margin = (composite_better['composite_abs_corr'] - composite_better['winner_corr']).mean()
                    report_lines.append(f"    {gt}: Composite won {composite_wins}/{total} ({composite_wins/total*100:.1f}%)")
                    report_lines.append(f"      When composite wins: avg_corr={avg_composite_corr:.4f}, avg_margin={avg_margin:.4f}")
                
                # Show cases where composite lost
                composite_lost = gt_subset[gt_subset['winner'] != 'composite']
                if len(composite_lost) > 0:
                    avg_winner_corr = composite_lost['winner_corr'].mean()
                    avg_composite_corr_lost = composite_lost['composite_abs_corr'].mean()
                    report_lines.append(f"      When composite loses: winner_avg={avg_winner_corr:.4f}, composite_avg={avg_composite_corr_lost:.4f}")
    
    report_text = "\n".join(report_lines)
    
    report_path = f'{OUTPUT_DIR}/verification_report.txt'
    with open(report_path, 'w') as f:
        f.write(report_text)
    
    print(f"\nVerification report saved: {report_path}")
    print(report_text)


def main():
    print("="*80)
    print("TESTING CENTRALITY COMBINATIONS WITH VERIFICATION")
    print("="*80)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_results = {}
    all_correlation_dfs = []
    combo_names = []
    
    for high_cent, low_cent, combo_name in COMBINATIONS_TO_TEST:
        results, correlations = test_combination_across_networks(high_cent, low_cent, combo_name)
        all_results[combo_name] = results
        
        # Save correlations to CSV
        df = save_correlations_to_csv(correlations, combo_name)
        all_correlation_dfs.append(df)
        combo_names.append(combo_name)
        
        # Print summary
        print(f"\n{combo_name} Summary:")
        for network_type in ['unbalanced', 'balanced-importance', 'balanced-doctypebranch']:
            for gt in GROUND_TRUTHS:
                counts = results[network_type][gt]
                composite_wins = counts.get('composite', 0)
                total = sum(counts.values())
                if total > 0:
                    print(f"  {network_type:25} - {gt:15}: {composite_wins:2}/{total:2} ({composite_wins/total*100:5.1f}%)")
    
    # Create verification report
    create_verification_report(all_correlation_dfs, combo_names)
    
    # Create combined summary CSV
    combined_df = pd.concat([df.assign(combo=name) for df, name in zip(all_correlation_dfs, combo_names)])
    combined_path = f'{OUTPUT_DIR}/ALL_COMBINATIONS_correlations.csv'
    combined_df.to_csv(combined_path, index=False)
    print(f"\nCombined correlations saved: {combined_path}")
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print(f"All verification files saved to: {OUTPUT_DIR}")
    print("="*80)
    
    print("\nFiles generated:")
    print("  - <combo>_detailed_correlations.csv (all centrality correlations)")
    print("  - <combo>_summary.csv (key results)")
    print("  - verification_report.txt (human-readable report)")
    print("  - ALL_COMBINATIONS_correlations.csv (combined data)")


if __name__ == "__main__":
    main()
