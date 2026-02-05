"""
Compare different statistical methods for selecting high/low performing centralities

This script tests two approaches:
1. Cohen's d (effect size)
2. ROC-AUC (classification performance)

Usage:
    python compare_selection_methods.py
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.metrics import roc_auc_score
from collections import defaultdict


# ==================== CONFIGURATION ====================
BASE_DIR = 'results/fixed-merged-subarticles-edges/importance-merged-50-cutoff'
BALANCED_NETWORKS_DIR = 'networks/merged-article-edges'
GROUND_TRUTHS = ['importance', 'doctypebranch']
OUTPUT_DIR_COHENS = 'results/high_low_analysis_50_cutoff_cohens'
OUTPUT_DIR_AUC = 'results/high_low_analysis_50_cutoff_auc'

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


# ==================== COHEN'S D APPROACH ====================
def find_best_centralities_cohens_d(df, centralities, ground_truth):
    """
    Select centralities based on Cohen's d effect size.
    
    High: largest effect size for group 1 vs groups 2-3
    Low: largest effect size for group 3 vs groups 1-2
    """
    high_effects = {}
    low_effects = {}
    
    for centrality in centralities:
        # High: effect size for importance=1 vs importance>1
        group_high = df[df[ground_truth] == 1][centrality]
        group_not_high = df[df[ground_truth] > 1][centrality]
        
        if len(group_high) > 1 and len(group_not_high) > 1:
            # Cohen's d
            pooled_std = np.sqrt(((len(group_high)-1)*group_high.std()**2 + 
                                   (len(group_not_high)-1)*group_not_high.std()**2) / 
                                  (len(group_high) + len(group_not_high) - 2))
            if pooled_std > 0:
                cohens_d_high = abs((group_high.mean() - group_not_high.mean()) / pooled_std)
                high_effects[centrality] = cohens_d_high
            else:
                high_effects[centrality] = 0
        else:
            high_effects[centrality] = 0
        
        # Low: effect size for importance=3 vs importance<3
        group_low = df[df[ground_truth] == 3][centrality]
        group_not_low = df[df[ground_truth] < 3][centrality]
        
        if len(group_low) > 1 and len(group_not_low) > 1:
            pooled_std = np.sqrt(((len(group_low)-1)*group_low.std()**2 + 
                                   (len(group_not_low)-1)*group_not_low.std()**2) / 
                                  (len(group_low) + len(group_not_low) - 2))
            if pooled_std > 0:
                cohens_d_low = abs((group_low.mean() - group_not_low.mean()) / pooled_std)
                low_effects[centrality] = cohens_d_low
            else:
                low_effects[centrality] = 0
        else:
            low_effects[centrality] = 0
    
    if not high_effects:
        return None, None
    
    best_high = max(high_effects.items(), key=lambda x: x[1])[0]
    low_effects.pop(best_high, None)
    
    if not low_effects:
        return best_high, None
    
    best_low = max(low_effects.items(), key=lambda x: x[1])[0]
    
    return best_high, best_low


# ==================== ROC-AUC APPROACH ====================
def find_best_centralities_roc_auc(df, centralities, ground_truth):
    """
    Select centralities based on ROC-AUC for binary classification.
    
    High: best AUC for classifying 1 vs 2-3
    Low: best AUC for classifying 3 vs 1-2
    """
    high_aucs = {}
    low_aucs = {}
    
    for centrality in centralities:
        # High: AUC for importance=1 vs importance>1
        y_high = (df[ground_truth] == 1).astype(int)
        
        if len(y_high.unique()) > 1:  # Need both classes present
            try:
                auc_high = roc_auc_score(y_high, df[centrality])
                # AUC can be < 0.5, which means inverse relationship
                # We want the strongest relationship, so take max distance from 0.5
                high_aucs[centrality] = abs(auc_high - 0.5)
            except:
                high_aucs[centrality] = 0
        else:
            high_aucs[centrality] = 0
        
        # Low: AUC for importance=3 vs importance<3
        y_low = (df[ground_truth] == 3).astype(int)
        
        if len(y_low.unique()) > 1:
            try:
                auc_low = roc_auc_score(y_low, df[centrality])
                low_aucs[centrality] = abs(auc_low - 0.5)
            except:
                low_aucs[centrality] = 0
        else:
            low_aucs[centrality] = 0
    
    if not high_aucs:
        return None, None
    
    best_high = max(high_aucs.items(), key=lambda x: x[1])[0]
    low_aucs.pop(best_high, None)
    
    if not low_aucs:
        return best_high, None
    
    best_low = max(low_aucs.items(), key=lambda x: x[1])[0]
    
    return best_high, best_low


# ==================== DATA LOADING ====================
def load_network_data(network_set, article_dir):
    """Load data for a network (handles balanced vs unbalanced)"""
    if network_set == 'unbalanced':
        # Load from total_df.csv
        total_df_path = os.path.join(BASE_DIR, network_set, article_dir, 'total_df.csv')
        if os.path.exists(total_df_path):
            return pd.read_csv(total_df_path)
    else:
        # Load balanced network nodes and match to unbalanced total_df
        balanced_dir_name = f"split-{network_set}"
        nodes_json_path = os.path.join(BALANCED_NETWORKS_DIR, balanced_dir_name, article_dir, 'nodes.json')
        
        if not os.path.exists(nodes_json_path):
            return None
        
        with open(nodes_json_path, 'r') as f:
            nodes_data = json.load(f)
        balanced_eclis = [node['ecli'] for node in nodes_data]
        
        unbalanced_total_df_path = os.path.join(BASE_DIR, 'unbalanced', article_dir, 'total_df.csv')
        if not os.path.exists(unbalanced_total_df_path):
            return None
        
        unbalanced_df = pd.read_csv(unbalanced_total_df_path)
        return unbalanced_df[unbalanced_df['ecli'].isin(balanced_eclis)].copy()
    
    return None


# ==================== ANALYSIS ====================
def run_analysis(selection_function, output_dir, method_name):
    """Run analysis with a specific selection function"""
    print(f"\n{'='*60}")
    print(f"ANALYZING WITH {method_name}")
    print(f"{'='*60}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize counters
    network_sets = ['balanced-importance', 'balanced-doctypebranch', 'unbalanced']
    analysis_results = {}
    
    for network_set in network_sets:
        analysis_results[network_set] = {}
        for ground_truth in GROUND_TRUTHS:
            analysis_results[network_set][ground_truth] = {
                'high_counts': defaultdict(int),
                'low_counts': defaultdict(int),
                'networks': []
            }
    
    # Process each network set
    for network_set in network_sets:
        print(f"\nProcessing {network_set}...")
        
        if network_set == 'unbalanced':
            network_dir = os.path.join(BASE_DIR, network_set)
        else:
            balanced_dir_name = f"split-{network_set}"
            network_dir = os.path.join(BALANCED_NETWORKS_DIR, balanced_dir_name)
        
        if not os.path.exists(network_dir):
            continue
        
        article_dirs = [d for d in os.listdir(network_dir) 
                       if os.path.isdir(os.path.join(network_dir, d)) 
                       and d.startswith('article_')]
        
        for article_dir in sorted(article_dirs):
            df = load_network_data(network_set, article_dir)
            
            if df is None or len(df) == 0:
                continue
            
            # Check for missing centralities
            missing = [c for c in CENTRALITIES if c not in df.columns]
            if missing:
                continue
            
            # Analyze for each ground truth
            for ground_truth in GROUND_TRUTHS:
                if ground_truth not in df.columns:
                    continue
                
                try:
                    best_high, best_low = selection_function(df, CENTRALITIES, ground_truth)
                    
                    if best_high:
                        analysis_results[network_set][ground_truth]['high_counts'][best_high] += 1
                        analysis_results[network_set][ground_truth]['networks'].append(f"{network_set}/{article_dir}")
                    
                    if best_low:
                        analysis_results[network_set][ground_truth]['low_counts'][best_low] += 1
                    
                    print(f"  {article_dir} - {ground_truth}: HIGH={best_high}, LOW={best_low}")
                    
                except Exception as e:
                    print(f"  Error analyzing {article_dir} - {ground_truth}: {e}")
    
    # Save summary
    save_summary(analysis_results, output_dir, method_name)
    
    return analysis_results


def save_summary(analysis_results, output_dir, method_name):
    """Save summary statistics"""
    summary_path = os.path.join(output_dir, 'summary.txt')
    
    with open(summary_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write(f"HIGH/LOW PERFORMER ANALYSIS - {method_name}\n")
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
                f.write(f"Total networks: {len(gt_data['networks'])}\n\n")
                
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


# ==================== MAIN ====================
if __name__ == "__main__":
    print("="*60)
    print("COMPARING SELECTION METHODS")
    print("="*60)
    
    # Run Cohen's d analysis
    cohens_results = run_analysis(
        find_best_centralities_cohens_d, 
        OUTPUT_DIR_COHENS, 
        "COHEN'S D (EFFECT SIZE)"
    )
    
    # Run ROC-AUC analysis
    auc_results = run_analysis(
        find_best_centralities_roc_auc, 
        OUTPUT_DIR_AUC, 
        "ROC-AUC (CLASSIFICATION)"
    )
    
    print("\n" + "="*60)
    print("✅ COMPARISON COMPLETE!")
    print("="*60)
    print(f"\nCohen's d results: {OUTPUT_DIR_COHENS}")
    print(f"ROC-AUC results: {OUTPUT_DIR_AUC}")
