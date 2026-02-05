# Analysis Scripts Documentation

This directory contains all analysis scripts for the ECtHR citation network project.

## Core Analysis Scripts

### 1. `analyze_high_low_performers.py`

**Purpose**: Identify which centrality measures perform best for predicting high vs. low relevance judgments.

**Methodology**:
- **High Performer Selection**: Centrality with most negative correlation with ground truth (lower score = higher importance)
- **Low Performer Selection**: Among remaining centralities, select one with highest absolute correlation in low-relevance subset (scores 2-3)
- **Ground Truth Encoding**:
  - Importance: 1=most important, 2=important, 3=less important
  - Doctypebranch: 1=GRANDCHAMBER, 2=CHAMBER, 3=COMMITTEE

**Analysis Scope**:
- Individual sub-networks (article_1, article_2, etc.)
- Three network types: unbalanced, balanced-importance, balanced-doctypebranch
- Both ground truths (importance, doctypebranch)

**Outputs**:
- `results/high_low_analysis_50_cutoff/`
  - `{network_type}_high_performers.png` - High performer bar charts
  - `{network_type}_low_performers.png` - Low performer bar charts
  - `combined_total.png` - Overall frequency chart
  - `summary.txt` - Detailed text summary

**Usage**:
```bash
python analyze_high_low_performers.py [cutoff]
# Default cutoff: 50
```

---

### 2. `analyze_high_low_with_aggregates.py`

**Purpose**: Enhanced analysis including both individual sub-networks AND aggregate mega-networks to justify combination testing.

**Methodology**:
- **Step 1**: Analyze all individual sub-networks (same as script #1)
- **Step 2**: Create aggregate networks by combining all sub-networks of each type
  - Unbalanced aggregate: All 26 article networks combined (27,368 nodes)
  - Balanced-importance aggregate: All 24 balanced networks combined  
  - Balanced-doctypebranch aggregate: All 16 balanced networks combined
- **Step 3**: Count which high+low combinations appear most frequently

**Selection Logic** (matches `rankings.ipynb`):
- For **doctypebranch**: Calculate correlation using only GRANDCHAMBER (1) vs CHAMBER (2) cases
- For **importance**: Use full range (1, 2, 3)
- **Disruption** special handling: Invert correlation sign (positive corr = good for disruption)
- **High**: Centrality with highest correlation score
- **Low**: Centrality with second-highest score (excluding high)

**Outputs**:
- `results/high_low_analysis_with_aggregates/`
  - `combination_analysis.txt` - Frequency counts and justification
  - `combination_frequency.png` - Bar chart (tested combos highlighted in red)

**Usage**:
```bash
python analyze_high_low_with_aggregates.py
```

**Key Finding**: Most common combinations are:
1. Degree + Disruption (25 times)
2. Degree + HitsHub (21 times)
3. Relative-InDegree + HitsHub (11 times)

---

### 3. `test_combinations_with_verification.py`

**Purpose**: Test specific centrality combinations and generate complete verification data.

**Tested Combinations**:
- Degree + Eigenvector
- Degree + PageRank
- Degree + In-Degree

**Methodology**:
1. **Normalization**: Percentile ranking scaled to [1, 1000]
2. **Combination**: Weighted geometric mean `composite = high^w × low^(1-w)`
3. **Optimization**: Grid search over 99 weights (0.01-0.99) per network
4. **Evaluation**: Composite wins only if it beats ALL 13 individual centralities

**Outputs**:
- `results/fixed-merged-subarticles-edges/verification_test/`
  - `{combo}_detailed_correlations.csv` - All centrality correlations per network
  - `{combo}_summary.csv` - Key results only
  - `verification_report.txt` - Human-readable summary
  - `ALL_COMBINATIONS_correlations.csv` - Combined data

**Usage**:
```bash
python test_combinations_with_verification.py
```

---

### 4. `test_global_vs_local_weight.py`

**Purpose**: Validate claim about optimization advantage by testing global vs. local weight approaches.

**Methodology**:
- **LOCAL**: Per-network weight optimization (baseline)
- **GLOBAL**: Single fixed weight (median of optimal weights) for all networks
- Measures reduction in win rate when using global weight

**Results**:
- LOCAL: 43.2% win rate (57/132 networks)
- GLOBAL: 28.0% win rate (37/132 networks)
- Reduction: 14.4 percentage points

**Usage**:
```bash
python test_global_vs_local_weight.py
```

---

## Legacy/Test Scripts

### `test_centrality_combinations.py`
Original combination testing script (superseded by `test_combinations_with_verification.py`).

### `test_centrality_combinations_fixed.py`
Fixed version handling balanced networks correctly.

### `test_new_combinations.py`
Tests three specific combinations (used to discover Degree+Eigenvector as best).

### `compare_selection_methods.py`
Compares different centrality selection approaches.

---

## Understanding the Selection Logic

### Why Correlation-Based?

The scripts use **Spearman correlation** rather than counting wins because:
1. More statistically robust
2. Accounts for strength of relationship, not just ranking
3. Standard practice in network analysis

### Ground Truth Direction

**Lower scores = higher importance**:
- Importance: 1 (most) → 3 (least)
- Doctypebranch: 1 (GrandChamber) → 3 (Committee)

Therefore:
- **Negative correlation** = good predictor (high centrality → low score → high importance)
- **Positive correlation** = bad predictor

### Special Cases

**Disruption Index**:
- Exhibits POSITIVE correlation (higher disruption = less important)
- Correlation sign inverted during selection to ensure consistent ranking

**Doctypebranch Low Selection**:
- Uses only scores 1-2 (GRANDCHAMBER vs CHAMBER)
- Committee cases (3) excluded as they have different patterns

---

## Result File Formats

### CSV Files (verification data)

**Columns**:
- `network_type`: unbalanced | balanced-importance | balanced-doctypebranch
- `network`: article_1, article_2, etc.
- `ground_truth`: importance | doctypebranch
- `n_nodes`: Network size
- `composite_abs_corr`: Composite absolute correlation
- `composite_weight`: Optimized weight parameter
- `winner`: Which measure had highest correlation
- `{centrality}_corr`: Signed correlation for each centrality
- `{centrality}_abs_corr`: Absolute correlation for each centrality

### TXT Files (summaries)

Human-readable summaries with:
- Win counts by network type
- Average correlations when composite wins/loses
- Breakdown by ground truth

---

## Running All Analyses

```bash
# 1. High/low performer analysis
python scripts/analyze_high_low_performers.py

# 2. Enhanced analysis with aggregates  
python scripts/analyze_high_low_with_aggregates.py

# 3. Test combinations with verification
python scripts/test_combinations_with_verification.py

# 4. Validate global weight claim
python scripts/test_global_vs_local_weight.py
```

**Total runtime**: ~5-10 minutes for all scripts

---

## Troubleshooting

### Warnings

**ConstantInputWarning**: Normal for small networks where ground truth has no variance.

**DtypeWarning**: Mixed types in CSV columns (harmless, can ignore).

### Missing Data

If script reports "Directory not found":
- Check that `results/fixed-merged-subarticles-edges/importance-merged-50-cutoff/` exists
- Check that `networks/merged-article-edges/` exists

### Output Location

All scripts output to `results/` subdirectories. Never modify `networks/` or legacy results directories.
