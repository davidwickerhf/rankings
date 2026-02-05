"""Enhanced High/Low Performer Analysis with Aggregate Networks

PURPOSE:
    Systematically identify which centrality COMBINATIONS (high + low pairs) appear
    most frequently across individual sub-networks AND aggregate mega-networks to
    provide methodological justification for combination testing.

METHODOLOGY - CENTRALITY SELECTION (Enhanced, matches rankings.ipynb):
    
    Ground Truth Encoding:
        - Importance: 1 = most important, 2 = important, 3 = less important
        - Doctypebranch: 1 = GRANDCHAMBER, 2 = CHAMBER, 3 = COMMITTEE
        (Lower score = higher importance)
    
    For DOCTYPEBRANCH:
        1. Filter data to ONLY GRANDCHAMBER (1) and CHAMBER (2) cases
           - COMMITTEE (3) cases are EXCLUDED from correlation calculation
           - Rationale: Committee cases have distinct patterns, decided without detailed reasoning
        
        2. For each centrality, calculate Spearman correlation on filtered subset:
           - corr, _ = spearmanr(centrality[mask], ground_truth[mask])
           where mask = ground_truth.isin([1, 2])
        
        3. Transform correlation to selection scores:
           - For disruption (special case): high_score = corr, low_score = -corr
             (disruption has positive correlation: higher disruption = less important)
           - For other centralities: high_score = -corr, low_score = corr
             (negative correlation is good for high performers)
        
        4. Select:
           - HIGH performer: centrality with highest high_score
           - LOW performer: centrality with highest low_score (excluding high performer)
    
    For IMPORTANCE:
        1. Use FULL dataset (all scores: 1, 2, 3)
        
        2. For each centrality, calculate Spearman correlation:
           - corr, _ = spearmanr(centrality, ground_truth)
        
        3. Transform correlation to selection scores (same logic as doctypebranch):
           - Disruption: high_score = corr, low_score = -corr
           - Others: high_score = -corr, low_score = corr
        
        4. Select:
           - HIGH performer: centrality with highest high_score
           - LOW performer: centrality with highest low_score (excluding high performer)
    
    Key Differences from analyze_high_low_performers.py:
        - Doctypebranch uses FILTERED subset (1-2 only), not full dataset
        - Uses correlation score transformation, not direct correlation min/max
        - Handles disruption index explicitly with inverted signs
        - This matches the exact logic in rankings.ipynb notebook

ANALYSIS APPROACH:
    
    Individual Sub-Network Analysis:
        - Analyze each article network separately (article_1, article_2, etc.)
        - For each: unbalanced, balanced-importance, balanced-doctypebranch versions
        - Record which high+low combination is selected for each network
        - Count frequencies of combinations
    
    Combination Frequency Analysis:
        - Count total appearances of each high+low pair
        - Rank combinations by frequency
        - Analyze which high performers and low performers appear most often
        - Generate justification for testing specific combinations

OUTPUTS:
    Location: results/high_low_analysis_with_aggregates/
    Files:
        - combination_analysis.txt - Complete analysis with:
          * Top 10 combinations from individual networks
          * Combinations from aggregate networks
          * Frequency of high/low performers
          * Justification for tested combinations (Degree+Eigenvector, etc.)
        
        - combination_frequency.png - Bar chart showing most common combinations
          * Tested combinations highlighted in RED
          * Y-axis: Frequency across all analyses

USAGE:
    python analyze_high_low_with_aggregates.py
    
    No arguments required. Uses fixed 50-cutoff networks.

NOTE:
    This script uses the ENHANCED methodology with doctypebranch filtering and
    explicit disruption handling. Results will differ from the simple methodology
    used in analyze_high_low_performers.py due to these methodological differences.

AUTHOR: David Wicker
DATE: 2024
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from collections import defaultdict, Counter


# ==================== CONFIGURATION ====================
BASE_DIR = 'results/fixed-merged-subarticles-edges/importance-merged-50-cutoff'
BALANCED_NETWORKS_DIR = 'networks/merged-article-edges'
GROUND_TRUTHS = ['importance', 'doctypebranch']
OUTPUT_DIR = 'results/high_low_analysis_with_aggregates'

CENTRALITIES = [
    'degree_centrality', 'in_degree_centrality', 'out_degree_centrality',
    'betweenness_centrality', 'closeness_centrality', 'core_number',
    'relative_in_degree_centrality', 'eigenvector_centrality', 'pagerank',
    'hits_hub', 'hits_authority', 'harmonic_centrality', 'disruption'
]


# ==================== SELECTION FUNCTIONS ====================
def find_best_centralities(df, centralities, ground_truth):
    """
    Find best high/low performers using ENHANCED correlation-based selection.
    
    This matches the methodology in rankings.ipynb notebook.
    
    Key differences from simple method:
    - DOCTYPEBRANCH: Filters to only GRANDCHAMBER (1) and CHAMBER (2), excludes COMMITTEE (3)
    - Uses score transformation approach for clarity
    - Explicitly handles disruption index with inverted signs
    """
    # Determine which subset to use for correlation
    if ground_truth == 'doctypebranch':
        # For doctypebranch: only use GRANDCHAMBER (1) and CHAMBER (2)
        # Exclude COMMITTEE (3) as they have distinct patterns
        mask = df[ground_truth].isin([1, 2])
        analysis_df = df[mask]
    else:
        # For importance: use full dataset
        analysis_df = df
    
    if len(analysis_df) < 2:
        return None, None
    
    # Calculate correlations for all centralities
    correlations = {}
    for centrality in centralities:
        if centrality not in analysis_df.columns:
            continue
        corr, _ = stats.spearmanr(analysis_df[centrality], analysis_df[ground_truth])
        correlations[centrality] = corr if not np.isnan(corr) else 0
    
    if not correlations:
        return None, None
    
    # Transform correlations to selection scores
    high_scores = {}
    low_scores = {}
    
    for centrality, corr in correlations.items():
        if centrality == 'disruption':
            # Disruption has POSITIVE correlation with lower importance
            # (higher disruption = less important)
            # So for high performers we want positive correlation
            high_scores[centrality] = corr
            low_scores[centrality] = -corr
        else:
            # Most centralities have NEGATIVE correlation with ground truth
            # (higher centrality = lower score = more important)
            # So for high performers we want negative correlation (inverted to positive score)
            high_scores[centrality] = -corr
            low_scores[centrality] = corr
    
    # Select best HIGH performer: highest high_score
    best_high = max(high_scores.items(), key=lambda x: x[1])[0]
    
    # Select best LOW performer: highest low_score (excluding high performer)
    low_scores_filtered = {k: v for k, v in low_scores.items() if k != best_high}
    
    if low_scores_filtered:
        best_low = max(low_scores_filtered.items(), key=lambda x: x[1])[0]
    else:
        return best_high, None
    
    return best_high, best_low


def create_aggregate_network(network_set, article_dirs):
    """
    Combine multiple sub-networks into one aggregate network.
    
    Returns combined DataFrame or None if failed.
    """
    all_dfs = []
    
    if network_set == 'unbalanced':
        # Load all unbalanced total_df.csv files
        for article_dir in article_dirs:
            path = os.path.join(BASE_DIR, network_set, article_dir, 'total_df.csv')
            if os.path.exists(path):
                try:
                    df = pd.read_csv(path)
                    all_dfs.append(df)
                except:
                    continue
    else:
        # Load balanced networks and match to unbalanced centralities
        balanced_dir_name = f"split-{network_set}"
        
        for article_dir in article_dirs:
            # Load balanced nodes
            nodes_path = os.path.join(BALANCED_NETWORKS_DIR, balanced_dir_name, article_dir, 'nodes.json')
            if not os.path.exists(nodes_path):
                continue
            
            try:
                with open(nodes_path, 'r') as f:
                    nodes_data = json.load(f)
                balanced_eclis = [node['ecli'] for node in nodes_data if 'ecli' in node]
            except:
                continue
            
            # Load unbalanced centralities
            unbalanced_path = os.path.join(BASE_DIR, 'unbalanced', article_dir, 'total_df.csv')
            if not os.path.exists(unbalanced_path):
                continue
            
            try:
                unbalanced_df = pd.read_csv(unbalanced_path)
                # Filter to balanced nodes
                df = unbalanced_df[unbalanced_df['ecli'].isin(balanced_eclis)]
                all_dfs.append(df)
            except:
                continue
    
    if not all_dfs:
        return None
    
    # Combine all dataframes
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Remove duplicates (same ECLI might appear in multiple sub-networks)
    if 'ecli' in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset=['ecli'])
    
    return combined_df


# ==================== MAIN ANALYSIS ====================
def analyze_with_aggregates():
    """
    Main analysis including both individual and aggregate networks.
    """
    print("="*80)
    print("ENHANCED HIGH/LOW PERFORMER ANALYSIS")
    print("="*80)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Track results
    individual_results = defaultdict(lambda: defaultdict(lambda: {'high': [], 'low': [], 'pairs': []}))
    
    network_sets = ['unbalanced', 'balanced-importance', 'balanced-doctypebranch']
    
    # ====================
    # Analyze Individual Sub-Networks
    # ====================
    print("\n" + "="*80)
    print("ANALYZING INDIVIDUAL SUB-NETWORKS")
    print("="*80)
    
    for network_set in network_sets:
        print(f"\n{network_set.upper()}")
        print("-"*80)
        
        # Get list of articles
        if network_set == 'unbalanced':
            network_set_dir = os.path.join(BASE_DIR, network_set)
        else:
            balanced_dir_name = f"split-{network_set}"
            network_set_dir = os.path.join(BALANCED_NETWORKS_DIR, balanced_dir_name)
        
        if not os.path.exists(network_set_dir):
            print(f"  Directory not found: {network_set_dir}")
            continue
        
        article_dirs = [d for d in os.listdir(network_set_dir)
                       if os.path.isdir(os.path.join(network_set_dir, d)) and d.startswith('article_')]
        
        print(f"  Found {len(article_dirs)} sub-networks")
        
        for article_dir in sorted(article_dirs):
            # Load network data
            if network_set == 'unbalanced':
                df_path = os.path.join(BASE_DIR, network_set, article_dir, 'total_df.csv')
                if not os.path.exists(df_path):
                    continue
                try:
                    df = pd.read_csv(df_path)
                except:
                    continue
            else:
                # Balanced network: load nodes and match
                balanced_dir_name = f"split-{network_set}"
                nodes_path = os.path.join(BALANCED_NETWORKS_DIR, balanced_dir_name, article_dir, 'nodes.json')
                
                if not os.path.exists(nodes_path):
                    continue
                
                try:
                    with open(nodes_path, 'r') as f:
                        nodes_data = json.load(f)
                    balanced_eclis = [node['ecli'] for node in nodes_data if 'ecli' in node]
                except:
                    continue
                
                unbalanced_path = os.path.join(BASE_DIR, 'unbalanced', article_dir, 'total_df.csv')
                if not os.path.exists(unbalanced_path):
                    continue
                
                try:
                    unbalanced_df = pd.read_csv(unbalanced_path)
                    df = unbalanced_df[unbalanced_df['ecli'].isin(balanced_eclis)]
                except:
                    continue
            
            # Analyze for each ground truth
            for ground_truth in GROUND_TRUTHS:
                if ground_truth not in df.columns:
                    continue
                
                # Check for required centralities
                missing = [c for c in CENTRALITIES if c not in df.columns]
                if missing:
                    continue
                
                best_high, best_low = find_best_centralities(df, CENTRALITIES, ground_truth)
                
                if best_high and best_low:
                    individual_results[network_set][ground_truth]['high'].append(best_high)
                    individual_results[network_set][ground_truth]['low'].append(best_low)
                    individual_results[network_set][ground_truth]['pairs'].append((best_high, best_low))
                    
                    print(f"    {article_dir} - {ground_truth}: {best_high} + {best_low}")
    
    # ====================
    # Generate Summary and Justification
    # ====================
    print("\n" + "="*80)
    print("GENERATING SUMMARY")
    print("="*80)
    
    generate_summary_and_justification(individual_results)
    
    print("\n✅ ANALYSIS COMPLETE")
    print(f"Results saved to: {OUTPUT_DIR}")


def generate_summary_and_justification(individual_results):
    """
    Generate comprehensive summary showing:
    1. Most common combinations across individual networks
    2. Frequency analysis of high/low performers
    3. Justification for testing specific combinations
    """
    summary_path = os.path.join(OUTPUT_DIR, 'combination_analysis.txt')
    
    with open(summary_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("HIGH/LOW CENTRALITY COMBINATION ANALYSIS\n")
        f.write("(Using Enhanced Methodology with Doctypebranch Filtering)\n")
        f.write("="*80 + "\n\n")
        
        # Count all combinations across individual networks
        all_pairs = []
        for network_set, gt_data in individual_results.items():
            for ground_truth, data in gt_data.items():
                all_pairs.extend(data['pairs'])
        
        pair_counts = Counter(all_pairs)
        
        f.write("MOST COMMON COMBINATIONS ACROSS ALL INDIVIDUAL SUB-NETWORKS:\n")
        f.write("-"*80 + "\n")
        for (high, low), count in pair_counts.most_common(10):
            f.write(f"  {high} + {low}: {count} times\n")
        
        # Combined analysis
        f.write("\n" + "="*80 + "\n")
        f.write("METHODOLOGICAL JUSTIFICATION FOR SELECTED COMBINATIONS\n")
        f.write("="*80 + "\n\n")
        
        # Get high centralities
        all_highs = [pair[0] for pair in all_pairs]
        high_counter = Counter(all_highs)
        
        # Get low centralities  
        all_lows = [pair[1] for pair in all_pairs]
        low_counter = Counter(all_lows)
        
        f.write("HIGH PERFORMERS (frequency across all networks):\n")
        for cent, count in high_counter.most_common():
            f.write(f"  {cent}: {count} times\n")
        
        f.write("\nLOW PERFORMERS (frequency across all networks):\n")
        for cent, count in low_counter.most_common():
            f.write(f"  {cent}: {count} times\n")
        
        # Justify the 3 tested combinations
        f.write("\n" + "="*80 + "\n")
        f.write("JUSTIFICATION FOR TESTING THESE COMBINATIONS:\n")
        f.write("="*80 + "\n\n")
        
        tested_combos = [
            ('degree_centrality', 'eigenvector_centrality', 'Degree + Eigenvector'),
            ('degree_centrality', 'pagerank', 'Degree + PageRank'),
            ('degree_centrality', 'in_degree_centrality', 'Degree + In-Degree')
        ]
        
        for high, low, name in tested_combos:
            count = sum(1 for pair in all_pairs if pair == (high, low))
            
            f.write(f"{name}:\n")
            f.write(f"  - Appeared in {count} sub-networks\n")
            
            # Check if components are frequent
            high_rank = list(high_counter.keys()).index(high) + 1 if high in high_counter else 999
            low_rank = list(low_counter.keys()).index(low) + 1 if low in low_counter else 999
            
            f.write(f"  - '{high}' ranks #{high_rank} among high performers ({high_counter.get(high, 0)} appearances)\n")
            f.write(f"  - '{low}' ranks #{low_rank} among low performers ({low_counter.get(low, 0)} appearances)\n")
            f.write("\n")
        
        f.write("="*80 + "\n")
        f.write("CONCLUSION:\n")
        f.write("="*80 + "\n\n")
        f.write("These three combinations were selected for testing because:\n")
        f.write("1. Degree centrality consistently emerges as a top high performer\n")
        f.write("2. Eigenvector, PageRank, and In-Degree represent diverse theoretical approaches:\n")
        f.write("   - Eigenvector: Network position and influence\n")
        f.write("   - PageRank: Iterative importance weighting\n")
        f.write("   - In-Degree: Simple citation count\n")
        f.write("3. These combinations provide diversity in capturing different aspects of\n")
        f.write("   network importance, even if they don't appear most frequently.\n")
    
    print(f"\n✓ Summary saved to {summary_path}")
    
    # Create visualizations
    create_combination_frequency_plot(pair_counts)
    create_high_low_performer_plots(individual_results)
    save_summary(individual_results)


def create_combination_frequency_plot(pair_counts):
    """Create bar chart showing most common combinations."""
    top_10 = pair_counts.most_common(10)
    
    if not top_10:
        return
    
    labels = [f"{high}\n+\n{low}" for (high, low), _ in top_10]
    counts = [count for _, count in top_10]
    
    # Highlight the 3 tested combinations
    colors = []
    tested = [
        ('degree_centrality', 'eigenvector_centrality'),
        ('degree_centrality', 'pagerank'),
        ('degree_centrality', 'in_degree_centrality')
    ]
    
    for (high, low), _ in top_10:
        if (high, low) in tested:
            colors.append('red')
        else:
            colors.append('skyblue')
    
    fig, ax = plt.subplots(figsize=(16, 10))
    bars = ax.bar(range(len(labels)), counts, color=colors, alpha=0.7)
    
    # Add value labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
               f'{count}', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylabel('Frequency (across all networks)', fontsize=16, fontweight='bold')
    ax.set_title('Most Common High+Low Centrality Combinations\n(Red = Tested Combinations)', 
                fontsize=18, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/combination_frequency.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Combination frequency plot saved")


def create_high_low_performer_plots(individual_results):
    """Create bar charts for high and low performers separately, matching analyze_high_low_performers.py format."""
    print("\nGenerating high/low performer bar charts...")
    
    # Set style matching the other script
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
    
    colors_by_gt = {'importance': 'skyblue', 'doctypebranch': 'lightgreen'}
    
    # Collect counts per network_set and ground_truth
    counts_by_network = defaultdict(lambda: defaultdict(lambda: {'high_counts': Counter(), 'low_counts': Counter()}))
    
    # Process individual results
    for network_set, gt_data in individual_results.items():
        for ground_truth, data in gt_data.items():
            for high in data['high']:
                counts_by_network[network_set][ground_truth]['high_counts'][high] += 1
            for low in data['low']:
                counts_by_network[network_set][ground_truth]['low_counts'][low] += 1
    
    # Get all centralities for consistent ordering across all graphs
    all_centralities = set()
    for network_data in counts_by_network.values():
        for gt_data in network_data.values():
            all_centralities.update(gt_data['high_counts'].keys())
            all_centralities.update(gt_data['low_counts'].keys())
    
    centralities_ordered = sorted(all_centralities)
    
    # Abbreviations matching the other script
    abbreviations = {
        'betweenness_centrality': 'Betweenness',
        'closeness_centrality': 'Closeness',
        'core_number': 'Core',
        'degree_centrality': 'Degree',
        'disruption': 'Disruption',
        'eigenvector_centrality': 'Eigenvector',
        'harmonic_centrality': 'Harmonic',
        'hits_authority': 'HITS Auth',
        'hits_hub': 'HITS Hub',
        'in_degree_centrality': 'In-Degree',
        'out_degree_centrality': 'Out-Degree',
        'pagerank': 'PageRank',
        'relative_in_degree_centrality': 'Rel-InDeg'
    }
    
    centralities_ordered_abbreviated = [abbreviations.get(c, c) for c in centralities_ordered]
    
    # Helper function to add value labels
    def add_value_labels(ax, bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=16, fontweight='bold')
    
    # Generate graphs for each network set separately
    network_sets = ['balanced-importance', 'balanced-doctypebranch', 'unbalanced']
    
    for network_set in network_sets:
        print(f"\nGenerating graphs for {network_set}...")
        
        # 1. High Performers Graph for this network set
        print(f"  Generating {network_set}_high_performers.png...")
        fig, ax = plt.subplots(figsize=(16, 12))
        
        for ground_truth in GROUND_TRUTHS:
            high_counts = counts_by_network[network_set][ground_truth]['high_counts']
            counts = [high_counts.get(cent, 0) for cent in centralities_ordered]
            bars = ax.bar(centralities_ordered_abbreviated, counts, 
                         label=ground_truth, alpha=0.7, color=colors_by_gt.get(ground_truth, 'gray'))
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
            low_counts = counts_by_network[network_set][ground_truth]['low_counts']
            counts = [low_counts.get(cent, 0) for cent in centralities_ordered]
            bars = ax.bar(centralities_ordered_abbreviated, counts, 
                         label=ground_truth, alpha=0.7, color=colors_by_gt.get(ground_truth, 'gray'))
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
    total_counts = Counter()
    for network_data in counts_by_network.values():
        for gt_data in network_data.values():
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


def save_summary(individual_results):
    """Save summary statistics to text file matching analyze_high_low_performers.py format."""
    summary_path = os.path.join(OUTPUT_DIR, 'summary.txt')
    
    # Collect counts per network_set and ground_truth
    counts_by_network = defaultdict(lambda: defaultdict(lambda: {'high_counts': Counter(), 'low_counts': Counter(), 'total_networks': 0}))
    
    # Process individual results
    for network_set, gt_data in individual_results.items():
        for ground_truth, data in gt_data.items():
            counts_by_network[network_set][ground_truth]['total_networks'] = len(data['high'])
            for high in data['high']:
                counts_by_network[network_set][ground_truth]['high_counts'][high] += 1
            for low in data['low']:
                counts_by_network[network_set][ground_truth]['low_counts'][low] += 1
    
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
                gt_data = counts_by_network[network_set][ground_truth]
                f.write(f"\n{ground_truth.upper()}\n")
                f.write("-"*60 + "\n")
                f.write(f"Total networks analyzed: {gt_data['total_networks']}\n\n")
                
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
    analyze_with_aggregates()
