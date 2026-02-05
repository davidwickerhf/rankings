"""Analyze High/Low Centrality Performers Across Citation Networks

PURPOSE:
    Identify which centrality measures best predict high vs. low relevance judgments
    by analyzing individual sub-networks (article_1, article_2, etc.).

METHODOLOGY - CENTRALITY SELECTION:
    
    Ground Truth Encoding:
        - Importance: 1 = most important, 2 = important, 3 = less important
        - Doctypebranch: 1 = GRANDCHAMBER, 2 = CHAMBER, 3 = COMMITTEE
        (Lower score = higher importance)
    
    HIGH Performer Selection:
        1. Calculate Spearman correlation between each centrality and ground truth
           across the FULL dataset (all scores: 1, 2, 3)
        2. Select centrality with MOST NEGATIVE correlation
        3. Rationale: Negative correlation means higher centrality → lower score → higher importance
    
    LOW Performer Selection:
        1. Filter dataset to only LOW relevance cases (scores 2 and 3)
        2. For each centrality (excluding the high performer):
           - Calculate Spearman correlation with ground truth on this subset
           - Take absolute value of correlation
        3. Select centrality with HIGHEST absolute correlation
        4. Rationale: Best at distinguishing within low-relevance subset

    Special Note:
        This is a SIMPLIFIED selection method. The enhanced version in
        analyze_high_low_with_aggregates.py uses a more sophisticated approach
        that matches the rankings.ipynb notebook methodology.

ANALYSIS SCOPE:
    - Individual sub-networks: article_1, article_2, ..., article_46, article_P1, etc.
    - Network types: unbalanced (26), balanced-importance (24), balanced-doctypebranch (16)
    - Ground truths: importance, doctypebranch
    - Total: 66 networks × 2 ground truths = 132 analyses

OUTPUTS:
    Location: results/high_low_analysis_50_cutoff/
    Files:
        - {network_type}_high_performers.png - Bar chart of high performer frequencies
        - {network_type}_low_performers.png - Bar chart of low performer frequencies
        - combined_total.png - Overall frequency across all networks
        - summary.txt - Detailed text summary with counts

USAGE:
    python analyze_high_low_performers.py [cutoff]
    
    Arguments:
        cutoff (optional): Minimum network size (default: 50)
    
    Examples:
        python analyze_high_low_performers.py        # Use 50-cutoff
        python analyze_high_low_performers.py 100    # Use 100-cutoff

AUTHOR: David Wicker
DATE: 2024
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from collections import defaultdict


# ==================== CONFIGURATION ====================
import sys

# Allow cutoff to be specified as command line argument
CUTOFF = int(sys.argv[1]) if len(sys.argv) > 1 else 50

BASE_DIR = f'results/fixed-merged-subarticles-edges/importance-merged-{CUTOFF}-cutoff'
BALANCED_NETWORKS_DIR = 'networks/merged-article-edges'
GROUND_TRUTHS = ['importance', 'doctypebranch']
OUTPUT_DIR = f'results/high_low_analysis_{CUTOFF}_cutoff'

# Centralities to analyze
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


# ==================== HELPER FUNCTIONS ====================
def find_best_centralities(df, centralities, ground_truth):
    """
    Find the best centrality measures for predicting high vs low ground truth scores.
    
    Ground truth encoding:
    - Importance: 1 = most important, 2 = important, 3 = less important
    - Doctypebranch: 1 = GRANDCHAMBER, 2 = CHAMBER, 3 = COMMITTEE
    
    Selection logic:
    - best_high: centrality with strongest correlation among HIGH cases (score 1)
    - best_low: centrality with strongest correlation among LOW cases (scores 2-3)
    
    Returns:
        tuple: (best_high, best_low) - centrality names
    """
    # HIGH performer: best correlation among high-importance cases (score = 1)
    high_mask = df[ground_truth] == 1
    high_df = df[high_mask]
    
    high_correlations = {}
    for centrality in centralities:
        if len(high_df) > 1:  # Need at least 2 points for correlation
            corr, _ = stats.spearmanr(high_df[centrality], high_df[ground_truth])
            # Use absolute correlation since we're only looking at score=1 cases
            # (correlation will be weak/undefined, so we look at variance explained)
            high_correlations[centrality] = abs(corr) if not np.isnan(corr) else 0
        else:
            high_correlations[centrality] = 0
    
    # For high cases, pick centrality that best distinguishes within that group
    # Actually, since all have score=1, correlation is undefined.
    # Instead: use full dataset correlation (negative = good for high)
    full_correlations = {}
    for centrality in centralities:
        corr, _ = stats.spearmanr(df[centrality], df[ground_truth])
        full_correlations[centrality] = corr
    
    # Best HIGH predictor: most negative correlation on full dataset
    best_high = min(full_correlations.items(), key=lambda x: x[1])[0]
    
    # LOW performer: best correlation among low-importance cases (score = 2 or 3)
    low_mask = df[ground_truth].isin([2, 3])
    low_df = df[low_mask]
    
    low_correlations = {}
    for centrality in centralities:
        if centrality == best_high:
            continue  # Exclude best_high from consideration
        if len(low_df) > 1:
            corr, _ = stats.spearmanr(low_df[centrality], low_df[ground_truth])
            # Among low cases (2-3), we want strongest absolute correlation
            low_correlations[centrality] = abs(corr) if not np.isnan(corr) else 0
        else:
            low_correlations[centrality] = 0
    
    # Best LOW predictor: highest absolute correlation among low-importance subset
    best_low = max(low_correlations.items(), key=lambda x: x[1])[0]
    
    return best_high, best_low


def abbreviate_centrality_names(centralities):
    """Abbreviate long centrality names for better readability"""
    abbreviations = {
        'betweenness_centrality': 'Betweenness',
        'closeness_centrality': 'Closeness',
        'core_number': 'Core Number',
        'degree_centrality': 'Degree',
        'disruption': 'Disruption',
        'eigenvector_centrality': 'Eigenvector',
        'harmonic_centrality': 'Harmonic',
        'hits_authority': 'HITS Auth',
        'hits_hub': 'HITS Hub',
        'in_degree_centrality': 'In-Degree',
        'out_degree_centrality': 'Out-Degree',
        'pagerank': 'PageRank',
        'relative_in_degree_centrality': 'Rel In-Degree'
    }
    return [abbreviations.get(c, c) for c in centralities]


def add_value_labels(ax, rects):
    """Add value labels on top of bars"""
    for rect in rects:
        height = rect.get_height()
        if height > 0:
            ax.text(rect.get_x() + rect.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom',
                   fontsize=16, fontweight='bold')


def analyze_network_data(df, network_set, article_dir, analysis_results):
    """Analyze a network dataframe for high/low performers"""
    # Verify all centralities are present
    missing_centralities = [c for c in CENTRALITIES if c not in df.columns]
    if missing_centralities:
        print(f"    ⚠️  Missing centralities: {missing_centralities}")
        return
    
    # Analyze for each ground truth
    for ground_truth in GROUND_TRUTHS:
        if ground_truth not in df.columns:
            print(f"    ⚠️  Ground truth '{ground_truth}' not in dataframe")
            continue
        
        # Find best high and low performers
        try:
            best_high, best_low = find_best_centralities(df, CENTRALITIES, ground_truth)
            
            # Update counts for this specific network set
            analysis_results[network_set][ground_truth]['high_counts'][best_high] += 1
            analysis_results[network_set][ground_truth]['low_counts'][best_low] += 1
            analysis_results[network_set][ground_truth]['networks'].append(f"{network_set}/{article_dir}")
            
            print(f"    {ground_truth}: HIGH={best_high}, LOW={best_low}")
            
        except Exception as e:
            print(f"    ❌ Error analyzing {ground_truth}: {e}")
            import traceback
            traceback.print_exc()


# ==================== MAIN ANALYSIS ====================
def analyze_high_low_performers():
    """
    Main function to analyze high/low performers across all networks
    """
    print("="*60)
    print("ANALYZING HIGH/LOW PERFORMERS FOR 50-CUTOFF NETWORKS")
    print("="*60)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Initialize counters for each ground truth AND each network set
    analysis_results = {}
    network_sets = ['balanced-importance', 'balanced-doctypebranch', 'unbalanced']
    
    for network_set in network_sets:
        analysis_results[network_set] = {}
        for ground_truth in GROUND_TRUTHS:
            analysis_results[network_set][ground_truth] = {
                'high_counts': defaultdict(int),
                'low_counts': defaultdict(int),
                'networks': []
            }
    
    
    for network_set in network_sets:
        print(f"\n{'='*60}")
        print(f"Processing {network_set}")
        print(f"{'='*60}")
        
        # Handle balanced vs unbalanced networks differently
        if network_set == 'unbalanced':
            # For unbalanced: use total_df.csv directly
            network_set_dir = os.path.join(BASE_DIR, network_set)
            
            if not os.path.exists(network_set_dir):
                print(f"\nSkipping {network_set} (directory not found)")
                continue
            
            # Find all article subdirectories
            article_dirs = [d for d in os.listdir(network_set_dir) 
                           if os.path.isdir(os.path.join(network_set_dir, d)) 
                           and d.startswith('article_')]
            
            for article_dir in sorted(article_dirs):
                total_df_path = os.path.join(network_set_dir, article_dir, 'total_df.csv')
                
                if not os.path.exists(total_df_path):
                    print(f"  Skipping {article_dir} (no total_df.csv)")
                    continue
                
                print(f"\n  Analyzing {network_set}/{article_dir}...")
                
                # Load the data
                try:
                    df = pd.read_csv(total_df_path)
                except Exception as e:
                    print(f"    ❌ Error loading {total_df_path}: {e}")
                    continue
                    
                # Verify all centralities are present
                missing_centralities = [c for c in CENTRALITIES if c not in df.columns]
                if missing_centralities:
                    print(f"    ⚠️  Missing centralities: {missing_centralities}")
                    continue
                
                # Analyze for each ground truth
                analyze_network_data(df, network_set, article_dir, analysis_results)
        
        else:
            # For balanced networks: load nodes.json and match to unbalanced total_df
            balanced_dir_name = f"split-{network_set}"
            balanced_networks_path = os.path.join(BALANCED_NETWORKS_DIR, balanced_dir_name)
            
            if not os.path.exists(balanced_networks_path):
                print(f"\nSkipping {network_set} (directory not found at {balanced_networks_path})")
                continue
            
            # Find all article subdirectories
            article_dirs = [d for d in os.listdir(balanced_networks_path) 
                           if os.path.isdir(os.path.join(balanced_networks_path, d)) 
                           and d.startswith('article_')]
            
            for article_dir in sorted(article_dirs):
                nodes_json_path = os.path.join(balanced_networks_path, article_dir, 'nodes.json')
                
                if not os.path.exists(nodes_json_path):
                    print(f"  Skipping {article_dir} (no nodes.json)")
                    continue
                
                print(f"\n  Analyzing {network_set}/{article_dir}...")
                
                # Load balanced network nodes
                try:
                    with open(nodes_json_path, 'r') as f:
                        nodes_data = json.load(f)
                    balanced_eclis = [node['ecli'] for node in nodes_data]
                    print(f"    Found {len(balanced_eclis)} nodes in balanced network")
                except Exception as e:
                    print(f"    ❌ Error loading {nodes_json_path}: {e}")
                    continue
                
                # Load corresponding unbalanced total_df
                unbalanced_total_df_path = os.path.join(BASE_DIR, 'unbalanced', article_dir, 'total_df.csv')
                
                if not os.path.exists(unbalanced_total_df_path):
                    print(f"    ⚠️  No unbalanced total_df found at {unbalanced_total_df_path}")
                    continue
                
                try:
                    unbalanced_df = pd.read_csv(unbalanced_total_df_path)
                    print(f"    Loaded {len(unbalanced_df)} nodes from unbalanced network")
                except Exception as e:
                    print(f"    ❌ Error loading {unbalanced_total_df_path}: {e}")
                    continue
                
                # Filter to only balanced network nodes
                df = unbalanced_df[unbalanced_df['ecli'].isin(balanced_eclis)].copy()
                print(f"    Matched {len(df)} nodes with centrality scores")
                
                if len(df) == 0:
                    print(f"    ⚠️  No matching ECLIs found")
                    continue
                
                # Analyze this balanced network
                analyze_network_data(df, network_set, article_dir, analysis_results)
    
    # Generate visualizations
    print(f"\n{'='*60}")
    print("GENERATING VISUALIZATIONS")
    print(f"{'='*60}")
    
    generate_visualizations(analysis_results)
    
    # Save summary
    save_summary(analysis_results)
    
    print(f"\n{'='*60}")
    print("✅ ANALYSIS COMPLETE!")
    print(f"{'='*60}")
    print(f"Results saved to: {OUTPUT_DIR}")


def generate_visualizations(analysis_results):
    """Generate bar charts for high and low performers"""
    
    # Set style
    plt.style.use('default')
    plt.rcParams.update({
        'font.size': 18,
        'axes.titlesize': 22,
        'axes.labelsize': 20,
        'xtick.labelsize': 18,
        'ytick.labelsize': 18,
        'legend.fontsize': 16,
        'figure.titlesize': 24
    })
    
    colors = {'importance': 'skyblue', 'doctypebranch': 'lightgreen'}
    
    # Collect all unique centralities for consistent ordering across ALL network sets
    all_centralities = set()
    for network_set_data in analysis_results.values():
        for gt_data in network_set_data.values():
            all_centralities.update(gt_data['high_counts'].keys())
            all_centralities.update(gt_data['low_counts'].keys())
    
    centralities_ordered = sorted(all_centralities)
    centralities_ordered_abbreviated = abbreviate_centrality_names(centralities_ordered)
    
    # Generate graphs for each network set separately
    network_sets = ['balanced-importance', 'balanced-doctypebranch', 'unbalanced']
    
    for network_set in network_sets:
        print(f"\nGenerating graphs for {network_set}...")
        
        # 1. High Performers Graph for this network set
        print(f"  Generating {network_set}_high_performers.png...")
        fig, ax = plt.subplots(figsize=(16, 12))
        
        for ground_truth in GROUND_TRUTHS:
            high_counts = analysis_results[network_set][ground_truth]['high_counts']
            counts = [high_counts.get(cent, 0) for cent in centralities_ordered]
            bars = ax.bar(centralities_ordered_abbreviated, counts, 
                         label=ground_truth, alpha=0.7, color=colors.get(ground_truth, 'gray'))
            add_value_labels(ax, bars)
        
        plt.ylabel('Times Selected as Best High Predictor', fontsize=20, fontweight='bold')
        plt.title(f'Best Performing Centralities for High Scores\n{network_set.replace("-", " ").title()} (50-Cutoff)', 
                 fontsize=22, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right', fontsize=18)
        plt.legend(fontsize=16, frameon=True, fancybox=True, shadow=True)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/{network_set}_high_performers.png', bbox_inches='tight', dpi=300)
        plt.close()
        print("    ✓ Saved")
        
        # 2. Low Performers Graph for this network set
        print(f"  Generating {network_set}_low_performers.png...")
        fig, ax = plt.subplots(figsize=(16, 12))
        
        for ground_truth in GROUND_TRUTHS:
            low_counts = analysis_results[network_set][ground_truth]['low_counts']
            counts = [low_counts.get(cent, 0) for cent in centralities_ordered]
            bars = ax.bar(centralities_ordered_abbreviated, counts, 
                         label=ground_truth, alpha=0.7, color=colors.get(ground_truth, 'gray'))
            add_value_labels(ax, bars)
        
        plt.ylabel('Times Selected as Best Low Predictor', fontsize=20, fontweight='bold')
        plt.title(f'Best Performing Centralities for Low Scores\n{network_set.replace("-", " ").title()} (50-Cutoff)', 
                 fontsize=22, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right', fontsize=18)
        plt.legend(fontsize=16, frameon=True, fancybox=True, shadow=True)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/{network_set}_low_performers.png', bbox_inches='tight', dpi=300)
        plt.close()
        print("    ✓ Saved")
    
    # 3. Combined Total Graph (across ALL network sets)
    print("\nGenerating combined_total.png...")
    total_counts = defaultdict(int)
    for network_set_data in analysis_results.values():
        for gt_data in network_set_data.values():
            for cent, count in gt_data['high_counts'].items():
                total_counts[cent] += count
            for cent, count in gt_data['low_counts'].items():
                total_counts[cent] += count
    
    fig, ax = plt.subplots(figsize=(16, 12))
    counts = [total_counts.get(cent, 0) for cent in centralities_ordered]
    bars = ax.bar(centralities_ordered_abbreviated, counts, color='lightcoral', alpha=0.7)
    add_value_labels(ax, bars)
    
    plt.ylabel('Total Times Selected (High + Low)', fontsize=20, fontweight='bold')
    plt.title('Overall Best Performing Centralities (50-Cutoff)', fontsize=22, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=18)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/combined_total.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("  ✓ Saved")


def save_summary(analysis_results):
    """Save summary statistics to text file"""
    summary_path = os.path.join(OUTPUT_DIR, 'summary.txt')
    
    with open(summary_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write("HIGH/LOW PERFORMER ANALYSIS SUMMARY (50-CUTOFF)\n")
        f.write("="*60 + "\n\n")
        
        network_sets = ['balanced-importance', 'balanced-doctypebranch', 'unbalanced']
        
        for network_set in network_sets:
            f.write(f"\n{'='*60}\n")
            f.write(f"{network_set.upper()}\n")
            f.write(f"{'='*60}\n")
            
            for ground_truth in GROUND_TRUTHS:
                gt_data = analysis_results[network_set][ground_truth]
                f.write(f"\n{ground_truth.upper()}\n")
                f.write("-"*60 + "\n")
                f.write(f"Total networks analyzed: {len(gt_data['networks'])}\n\n")
                
                f.write("HIGH PERFORMERS:\n")
                sorted_high = sorted(gt_data['high_counts'].items(), key=lambda x: x[1], reverse=True)
                for cent, count in sorted_high:
                    f.write(f"  {cent}: {count}\n")
                
                f.write("\nLOW PERFORMERS:\n")
                sorted_low = sorted(gt_data['low_counts'].items(), key=lambda x: x[1], reverse=True)
                for cent, count in sorted_low:
                    f.write(f"  {cent}: {count}\n")
                
                f.write("\n")
    
    print(f"\n✓ Summary saved to {summary_path}")


if __name__ == "__main__":
    analyze_high_low_performers()
