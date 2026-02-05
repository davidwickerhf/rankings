# Analysis Pipeline

This folder contains the complete analysis pipeline for identifying optimal centrality measures and testing composite measures for predicting precedent value in ECtHR case law.

## Pipeline Overview

The analysis follows a sequential process:

1. **Find Best High/Low Performers** → Identify which individual centralities work best
2. **Test Composite Measures** → Combine high/low performers and evaluate performance

---

## Scripts

### `01_find_best_high_low.py`

**Purpose**: Systematically identify which centrality measures best predict high-relevance vs. low-relevance judgments across sub-networks.

**Methodology**:
- **HIGH Performer Selection**: 
  - Calculate Spearman correlation on FULL dataset (all ground truth scores: 1, 2, 3)
  - Select centrality with most NEGATIVE correlation
  - Rationale: Higher centrality → lower score → higher importance
  
- **LOW Performer Selection**:
  - Filter to only LOW relevance cases (scores 2 and 3)
  - Calculate Spearman correlation for each centrality on this subset
  - Select centrality with highest ABSOLUTE correlation
  - Rationale: Best at distinguishing within low-relevance subset

**Networks Analyzed**:
- Unbalanced (26 sub-networks)
- Balanced-importance (24 sub-networks)
- Balanced-doctypebranch (16 sub-networks)
- Total: 66 networks × 2 ground truths = 132 analyses

**Output Location**: `results/high_low_analysis_50_cutoff/`

**Output Files**:
- `{network_type}_high_performers.png` - Bar charts showing frequency of selection (3 files)
- `{network_type}_low_performers.png` - Bar charts showing frequency of selection (3 files)
- `combined_total.png` - Overall frequency across all network types
- `summary.txt` - Detailed counts by network type and ground truth

**Usage**:
```bash
python scripts/analysis/01_find_best_high_low.py
```

**Key Results** (from paper):
- **Best HIGH performers**: Degree, PageRank (frequency varies by network type)
- **Best LOW performers**: Degree, In-Degree, Eigenvector (frequency varies by network type)

---

### `02_test_composite_measures.py`

**Purpose**: Test three composite centrality measures that combine high-relevance and low-relevance performers using weighted geometric mean optimization.

**Composite Combinations Tested**:
1. **PageRank (high) + Degree (low)**
   - PageRank dominant for high-relevance in importance-balanced networks
   - Degree effective for low-relevance identification

2. **Degree (high) + Eigenvector (low)**
   - Degree leading high performer in multiple configurations
   - Eigenvector competitive for low-relevance cases

3. **Degree (high) + In-Degree (low)**
   - Degree top performer in balanced-doctypebranch networks
   - In-Degree frequently selected for low-relevance

**Methodology**:
1. **Normalization**: Convert centralities to percentile ranks [1-1000]
2. **Combination**: Use weighted geometric mean:
   ```
   composite = high^w × low^(1-w)
   ```
3. **Optimization**: Test weights w ∈ [0.01, 0.99] in 0.01 increments
4. **Selection**: Choose weight that maximizes Spearman correlation with ground truth
5. **Evaluation**: Compare composite against all 13 individual centralities
6. **Winner Determination**: Composite "wins" if it has highest correlation

**Output Location**: `results/fixed-merged-subarticles-edges/new_combinations_test/`

**Output Files**:
- `comparison_{network_type}_{ground_truth}.png` - Side-by-side comparison of all 3 composites (18 files total)
- `combination_summary.csv` - Win rates for each composite across all configurations
- `detailed_results.json` - Network-by-network results including optimal weights

**Usage**:
```bash
python scripts/analysis/02_test_composite_measures.py
```

**Expected Results**:
- Composite measures should outperform individual centralities
- Win rates vary by network type and ground truth
- Optimal weights adapt to each network's characteristics

---

### `03_test_paper_composite.py`

**Purpose**: Test composite measure using the exact threshold-based methodology described in the paper (lines 545-558).

**Composite Combinations Tested**:
1. **PageRank (high) + Degree (low)**
2. **Degree (high) + Eigenvector (low)**
3. **Degree (high) + In-Degree (low)**

**Methodology** (Paper's Approach):
1. Rank all judgments by high-relevance centrality (descending: rank 1 = highest centrality)
2. Rank all judgments by low-relevance centrality (descending)
3. Calculate dynamic threshold based on proportion of high-relevance ground truth:
   - For **doctypebranch**: proportion of Grand Chamber cases (doctypebranch=1)
   - For **importance**: proportion of Importance=1 judgments
4. Create composite ranking:
   - **Top n% judgments**: Use ranking from high-relevance centrality
   - **Remaining judgments**: Use ranking from low-relevance centrality (shifted by n)
5. Evaluate composite ranking against all individual centralities

**Key Difference from Script 02**:
- **Script 02**: Uses **weighted geometric mean** with optimization (w ∈ [0.01, 0.99])
- **Script 03**: Uses **threshold-based ranking split** as written in paper
- Different methodologies, different results

**Output Location**: `results/analysis/03_paper_composite/`

**Output Files**:
- `combination_summary.csv` - Win rates for each combination
- `detailed_results.json` - Network-by-network results with thresholds
- `comparison_{network_type}_{ground_truth}.png` - Visual comparisons (6 files)

**Usage**:
```bash
python scripts/analysis/03_test_paper_composite.py
```

**Key Results**:
- **Degree+Eigenvector**: Best performer (50-75% win rate)
- **Degree+InDegree**: Strong performer (46-75% win rate)
- **PageRank+Degree**: Weaker performance (8-38% win rate)
- Highest win rates in balanced-doctypebranch networks

---

### `04_optimized_threshold_composite.py`

**Purpose**: Test composite measure using HIGH-RELEVANCE PRIORITY with optimized universal threshold via grid search.

**Composite Combinations Tested**:
1. **PageRank (high) + Degree (low)**
2. **Degree (high) + Eigenvector (low)**
3. **Degree (high) + In-Degree (low)**

**Methodology** (Optimized Universal Threshold):
1. Rank all judgments by high-relevance centrality (descending)
2. Rank all judgments by low-relevance centrality (descending)
3. Grid search optimal threshold τ ∈ [0.05, 0.95] in 0.05 increments:
   - For each network: evaluate all thresholds
   - Calculate total wins across all networks for each threshold
   - Select threshold that maximizes aggregate wins
4. Create composite ranking:
   - **Top τ% judgments**: Use ranking from high-relevance centrality (ranks 1 to k)
   - **Remaining judgments**: Use ranking from low-relevance centrality (ranks k+1 to N)
5. Evaluate composite ranking against all 13 individual centralities

**Key Difference from Script 03**:
- **Script 03**: Uses **ground-truth proportion** as threshold (requires knowing answer)
- **Script 04**: Uses **optimized universal threshold** found via grid search (data-driven)
- Script 04 significantly outperforms Script 03

**Output Location**: `results/analysis/04_optimized_threshold_composite/`

**Output Files**:
- `combination_summary.csv` - Win rates for each combination
- `detailed_results.json` - Network-by-network results with optimal thresholds
- `comparison_{network_type}_{ground_truth}.png` - Visual comparisons (6 files)

**Usage**:
```bash
python scripts/analysis/04_optimized_threshold_composite.py
```

**Key Results**:
- **Best Combination**: Degree+Eigenvector (56-75% win rate)
- **Optimal Thresholds**: importance=0.30-0.65, doctypebranch=0.35-0.70
- **Key Insight**: Universal optimized threshold outperforms network-specific ground-truth proportion

---

### `05_visualize_threshold_composite.py`

**Purpose**: Generate comprehensive visualizations for script 04 results.

**Visualizations Created**:
1. Win rate comparison bar charts for all combinations
2. Threshold optimization curves showing how win rate varies with threshold
3. Network-by-network performance summaries

**Output Location**: `results/analysis/04_optimized_threshold_composite/visualizations/`

**Usage**:
```bash
python scripts/analysis/05_visualize_threshold_composite.py
```

---

### `06_test_low_relevance_priority.py`

**Purpose**: Test composite measure using LOW-RELEVANCE PRIORITY approach (alternative mentioned in paper lines 553-554).

**Composite Combinations Tested**:
1. **PageRank (high) + Degree (low)**
2. **Degree (high) + Eigenvector (low)**
3. **Degree (high) + In-Degree (low)**

**Methodology** (Low-Relevance Priority):
1. Rank all judgments by low-relevance centrality (descending)
2. Rank all judgments by high-relevance centrality (descending)
3. Use optimal thresholds from script 04 (for direct comparison)
4. Create composite ranking:
   - **Bottom τ% judgments** (lowest low-centrality): Assign ranks N-k+1 to N
   - **Remaining judgments**: Use ranking from high-relevance centrality (ranks 1 to N-k)
5. Evaluate composite ranking against all 13 individual centralities

**Key Difference from Script 04**:
- **Script 04 (High-Rel Priority)**: Prioritizes TOP n% from HIGH centrality, fills rest with LOW centrality
- **Script 06 (Low-Rel Priority)**: Prioritizes BOTTOM n% from LOW centrality, fills rest with HIGH centrality

**Why These Approaches Are Mathematically Different**:
The two approaches select **different subsets** of judgments when high ≠ low centrality:
- **Script 04 with τ=0.30**: Selects top 30% by HIGH centrality (most important)
- **Script 06 with τ=0.30**: Selects bottom 30% by LOW centrality (least important)

Example with PageRank (high) + Degree (low):
- Script 04 prioritizes judgments with {highest PageRank}
- Script 06 deprioritizes judgments with {lowest Degree}
- These are **NOT complementary sets** unless PageRank ≡ Degree

Even if script 06 optimized its own threshold τ', it would still differ from script 04 because the selection logic is fundamentally different. Only when high = low centrality (same measure) would the approaches converge.

**Implementation Details**: 
- Script 06 independently optimizes thresholds using the same grid search method as script 04
- Despite optimization, Low-Rel Priority still performs much worse (avg -31.6% difference)
- **Key finding**: Low-Rel Priority only wins in 1/18 cases even with optimal thresholds

**Output Location**: `results/analysis/06_low_relevance_priority/`

**Output Files**:
- `combination_summary.csv` - Win rates for Low-Relevance Priority approach
- `detailed_results.json` - Network-by-network results

**Usage**:
```bash
python scripts/analysis/06_test_low_relevance_priority.py
```

**Key Results** (with independent threshold optimization):
- **Optimal thresholds found**: 
  - PageRank+Degree: importance=0.05, doctypebranch=0.05
  - Degree+Eigenvector: importance=0.35, doctypebranch=0.15
  - Degree+InDegree: importance=0.35, doctypebranch=0.15
- **Performance**: 6-63% win rate (best: PageRank+Degree balanced-importance importance 62.5%)
- **Conclusion**: Even with optimized thresholds, Low-Rel Priority is dramatically inferior to High-Rel Priority
- **Recommendation**: Do NOT use Low-Relevance Priority; paper's claim about convergence was misleading

---

### `07_compare_priority_approaches.py`

**Purpose**: Empirically compare High-Relevance Priority (script 04) vs Low-Relevance Priority (script 06).

**Analysis Components**:
1. **Comparison table**: Side-by-side win rates for both approaches
2. **Summary statistics**: Overall and by-combination/network-type breakdowns
3. **Bar chart visualization**: Win rate comparison across all configurations
4. **Heatmap visualization**: Performance difference showing where each approach excels

**Output Location**: `results/analysis/07_priority_comparison/`

**Output Files**:
- `priority_comparison.csv` - Detailed comparison table
- `summary_statistics.json` - Aggregate statistics
- `win_rate_comparison.png` - Bar chart comparing both approaches
- `difference_heatmap.png` - Heatmap showing performance differences

**Usage**:
```bash
python scripts/analysis/07_compare_priority_approaches.py
```

**Key Findings** (with Low-Rel independently optimized):
- **High-Rel better**: 17/18 cases (94.4%)
- **Low-Rel better**: 1/18 cases (5.6%) - PageRank+Degree balanced-importance importance only
- **Average difference**: -31.58% (negative = High-Rel better)
- **By combination**:
  - PageRank+Degree: -10.8% (Low-Rel competitive in one case)
  - Degree+Eigenvector: -41.1% (High-Rel dominates)
  - Degree+InDegree: -42.8% (High-Rel dominates)
- **Conclusion**: High-Relevance Priority is vastly superior across nearly all configurations
- **Paper Recommendation**: Remove or rewrite Low-Relevance Priority discussion (lines 553-554)

---

## Analysis Workflow

### Step 1: Identify Best Individual Centralities

Run the high/low performer analysis to empirically determine which centralities excel at identifying high-relevance vs. low-relevance cases:

```bash
python scripts/analysis/01_find_best_high_low.py
```

**Review outputs in**: `results/high_low_analysis_50_cutoff/`

**Key questions to answer**:
- Which centralities appear most frequently as high performers?
- Which centralities appear most frequently as low performers?
- Do results differ across network types (unbalanced, balanced-importance, balanced-doctypebranch)?
- Do results differ across ground truths (importance, doctypebranch)?

### Step 2: Test Composite Measures

Based on Step 1 results, test composite combinations that integrate the best high and low performers:

```bash
python scripts/analysis/02_test_composite_measures.py
```

**Review outputs in**: `results/fixed-merged-subarticles-edges/new_combinations_test/`

**Key questions to answer**:
- Do composites outperform individual centralities?
- Which composite combination performs best?
- Are win rates consistent across network types?
- What are the typical optimal weights?

---

## Data Requirements

Both scripts require:
- **Centrality data**: `results/fixed-merged-subarticles-edges/importance-merged-50-cutoff/`
- **Balanced network definitions**: `networks/merged-article-edges/`
- **Minimum network size**: 50 nodes (configurable in Step 1)

---

## Configuration

### Script 1 Configuration (`01_find_best_high_low.py`)

```python
CUTOFF = 50  # Minimum network size (can pass as CLI arg)
BASE_DIR = 'results/fixed-merged-subarticles-edges/importance-merged-50-cutoff'
BALANCED_NETWORKS_DIR = 'networks/merged-article-edges'
OUTPUT_DIR = 'results/high_low_analysis_50_cutoff'
```

### Script 2 Configuration (`02_test_composite_measures.py`)

```python
COMBINATIONS_TO_TEST = [
    ('pagerank', 'degree_centrality', 'PageRank+Degree'),
    ('degree_centrality', 'eigenvector_centrality', 'Degree+Eigenvector'),
    ('degree_centrality', 'in_degree_centrality', 'Degree+InDegree'),
]

BASE_DIR = 'results/fixed-merged-subarticles-edges/importance-merged-50-cutoff'
OUTPUT_DIR = 'results/fixed-merged-subarticles-edges/new_combinations_test'
```

---

## Notes

- **Simple Methodology**: Both scripts use the straightforward correlation-based approach (not the enhanced filtering method)
- **Ground Truths**: 1 = most important/GRANDCHAMBER, 2 = important/CHAMBER, 3 = less important/COMMITTEE
- **Network Types**: Unbalanced (all nodes), Balanced (undersampled by importance or doctypebranch)
- **Sub-networks**: Each article (Article 3, Article 8, etc.) creates a separate sub-network

---

## For Paper

**Key Findings to Report**:
1. From Step 1: Frequency counts showing which centralities dominate for high vs. low relevance
2. From Step 2: Win rates showing composite measures outperform individual centralities
3. Optimal weight distributions showing how high/low signals are balanced

**Methodology to Cite**:
- Simple correlation-based selection (Step 1)
- Weighted geometric mean with grid search optimization (Step 2)
- Evaluation across 66 sub-networks × 2 ground truths = 132 test cases per composite
