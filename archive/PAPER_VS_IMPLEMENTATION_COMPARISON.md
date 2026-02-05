# Paper Description vs. Actual Implementation: Critical Differences

## Summary
The paper describes a **counting-based selection method** with a **fixed Degree+InDegree combination** using a **predetermined threshold**. The actual implementation uses **per-network optimization** with **dynamic centrality selection** and **weight optimization via geometric mean**.

---

## 1. CENTRALITY SELECTION METHOD

### Paper Says:
> "We selected the measures with the highest counts for high-relevance and low-relevance scores **across the three datasets** (unbalanced, balanced by court branch, balanced by importance)."

- **Method**: Count-based selection across all networks
- **Result**: Fixed combination (Degree + In-Degree)
- **Scope**: Global decision based on aggregate performance

### Implementation Does:
**Notebook (`find_best_centralities_updated`):**
```python
# Lines 554-597 in rankings.ipynb
for centrality in centralities:
    corr, _ = stats.spearmanr(df[centrality], df[ground_truth])
    # Select based on correlation, not counts
    high_correlations[centrality] = -corr
    low_correlations[centrality] = corr

best_high = max(high_correlations.items(), key=lambda x: x[1])[0]
best_low = max(low_correlations.items(), key=lambda x: x[1])[0]
```

**Testing Scripts (`test_new_combinations.py`):**
```python
# Lines 20-24
COMBINATIONS_TO_TEST = [
    ('pagerank', 'degree_centrality', 'PageRank+Degree'),
    ('degree_centrality', 'eigenvector_centrality', 'Degree+Eigenvector'),
    ('degree_centrality', 'in_degree_centrality', 'Degree+InDegree'),
]
# MANUALLY SPECIFIED, not selected by counting
```

- **Method**: Correlation-based OR manually specified
- **Result**: Different combinations tested (Degree+Eigenvector won, not Degree+InDegree)
- **Scope**: Per-network optimization

**KEY DIFFERENCE**: Paper describes counting wins across datasets; implementation uses either:
1. Dynamic correlation-based selection per network (notebook)
2. Manual specification of combinations to test (testing scripts)

---

## 2. COMBINATION METHOD

### Paper Says:
> "Two approaches were considered:
> 1. High-Relevance Priority: Top n judgments selected from high-relevance measure, remaining from low-relevance measure
> 2. Low-Relevance Priority: Bottom n judgments selected from low-relevance measure, remaining from high-relevance measure"

> "The threshold between the two rankings was determined dynamically by computing the **proportion of Grand Chamber cases** and the **proportion of Importance=1 judgments**"

- **Method**: Threshold-based switching
- **Threshold**: Predetermined by dataset proportions (e.g., 15% GrandChamber = top 15% use high measure)
- **No optimization**: Threshold fixed by dataset characteristics

### Implementation Does:
**Weighted Geometric Mean (`create_weighted_composite_ranking`):**
```python
# Lines 673-721 in rankings.ipynb
for weight in np.arange(0.01, 1.00, 0.01):
    composite = weighted_combine(high_norm, low_norm, weight)
    corr = spearmanr(composite, df[ground_truth])[0]
    
    if corr > best_corr:
        best_corr = corr
        best_weight = weight
        best_composite = composite
```

**Geometric Mean Formula:**
```python
def weighted_combine(high, low, weight):
    epsilon = 1e-10
    return np.power(high + epsilon, weight) * np.power(low + epsilon, (1-weight))
```

- **Method**: Weighted geometric mean
- **Weight**: Optimized (0.01 to 0.99) to maximize Spearman correlation
- **Optimization**: Grid search over 99 possible weights per network

**Alternative (also in notebook):**
```python
# Lines 723-771: create_threshold_composite_ranking
for threshold_pct in range(1, 100):
    composite = threshold_combine(high_norm, low_norm, threshold_pct)
    corr = spearmanr(composite, df[ground_truth])[0]
    # Optimize threshold, not use dataset proportions
```

**KEY DIFFERENCE**: 
- Paper: Threshold = dataset proportion (fixed, not optimized)
- Implementation: Weight/threshold optimized per network to maximize correlation

---

## 3. SPECIFIC RESULTS CLAIMED

### Paper Says:
> "Specifically, we combined **Degree Centrality** (for high-relevance scores) with **In-Degree Centrality** (for low-relevance scores)."

> "Figure \ref{fig:performers_withcomposite} indicates that the composite measure outperforms all other centrality measures, receiving the highest counts of **14 (Court Branch)** and **16 (Importance)**, followed by **Degree Centrality (n=4)** (Court Branch) and **PageRank (n=6)** (Importance)."

- Fixed combination: Degree + In-Degree
- Claims 14/16 wins

### Implementation Results:

**From `test_new_combinations.py` and verification data:**

| Combination | Overall Win Rate | Best Performance |
|-------------|------------------|------------------|
| **Degree+Eigenvector** | **43.9%** | Balanced-doctypebranch: 50% on BOTH |
| Degree+PageRank | 41.9% | Balanced networks |
| Degree+InDegree | 35.9% | Unbalanced: 50% |
| InDegree+HitsHub* | 19.7% | Worst performer |

*InDegree+HitsHub = dynamic selection from notebook (what paper might be referring to)

**KEY DIFFERENCE**:
- Paper claims: Degree+InDegree is best
- Implementation shows: Degree+Eigenvector performs best (43.9% vs 35.9%)

---

## 4. OPTIMIZATION APPROACH

### Paper Says:
> "The threshold between the two rankings was determined dynamically by computing the proportion of Grand Chamber cases and the proportion of Importance=1 judgments"

- **Type**: Fixed threshold based on dataset
- **No parameter search**
- **Same threshold for all ground truths of same type**

Example:
- If 15% of cases are GrandChamber → top 15% ranked by Degree, rest by InDegree
- If 20% of cases are Importance=1 → top 20% ranked by Degree, rest by InDegree

### Implementation Does:
```python
# Grid search for optimal weight
for weight in np.arange(0.01, 1.00, 0.01):  # 99 different weights
    composite = weighted_combine(high_norm, low_norm, weight)
    corr = spearmanr(composite, df[ground_truth])[0]
    if corr > best_corr:
        best_weight = weight  # Save best weight
```

- **Type**: Optimization via grid search
- **Parameter**: Weight (0.01 to 0.99) optimized per network
- **Adaptive**: Different optimal weights for different networks

**Example from verification data:**
- article_10: weight = 0.55
- article_38: weight = 0.74
- article_39: weight = 0.01
- Weights vary from 0.01 to 0.99 depending on network!

**KEY DIFFERENCE**: 
- Paper: Threshold = dataset proportion (no search)
- Implementation: Weight optimized per network via 99-step grid search

---

## 5. NORMALIZATION

### Paper Says:
> "For each centrality measure, we **ranked the judgments** from highest to lowest based on their centrality scores"

- Simple ranking (1, 2, 3, ...)
- Likely ordinal ranks

### Implementation Does:
```python
def normalize_centrality(values):
    ranks = pd.Series(index=non_zero.index)
    ranks.loc[non_zero.index] = non_zero.rank(pct=True, ascending=False)
    ranks = ranks * 999 + 1  # Scale to [1, 1000]
    ranks = ranks.reindex(values.index, fill_value=1000)
    return ranks
```

- **Percentile ranking** (0-1 scale)
- **Scaled to [1, 1000]**
- Zeros assigned 1000 (lowest importance)

**KEY DIFFERENCE**: Implementation uses percentile-based continuous ranking [1-1000], not simple ordinal ranks

---

## 6. SELECTION OF LOW-RELEVANCE CENTRALITY

### Paper Says:
> "measures that performed well at identifying low-relevance judgments"

- Implies: Good at predicting Importance=3 or COMMITTEE cases

### Implementation Does:
**For doctypebranch:**
```python
# Lines 557-571 in rankings.ipynb
# Filter for just GRANDCHAMBER and CHAMBER cases
mask = df[ground_truth].isin([1, 2])  # EXCLUDES COMMITTEE (3)!
corr, _ = stats.spearmanr(df[centrality][mask], df[ground_truth][mask])
```

- **Only uses GRANDCHAMBER (1) vs CHAMBER (2)**
- **Ignores COMMITTEE (3) entirely** when selecting low-relevance centrality
- Comment in code: "# TODO For COURTBRANCH: When selecting the optimal metric for the lower class (less importance) we weight it against the middle class."

**For importance:**
```python
# Uses full range [1, 2, 3]
corr, _ = stats.spearmanr(df[centrality], df[ground_truth])
```

**KEY DIFFERENCE**: 
- Paper: Low-relevance means good at finding least important cases (3)
- Implementation (doctypebranch): Low-relevance selected based on CHAMBER (2) cases, not COMMITTEE (3)

---

## WHAT NEEDS TO BE FIXED IN THE PAPER

### Critical Issues:

1. **Selection Method** (Lines around "selected the measures with the highest counts"):
   ```
   WRONG: "selected the measures with the highest counts for high-relevance and 
           low-relevance scores across the three datasets"
   
   RIGHT: "For each network, we identified the centrality measures with the 
           strongest Spearman correlation with ground truth scores. The measure 
           with the highest absolute correlation was selected for high-relevance 
           prediction, and the second-highest for low-relevance prediction."
   ```

2. **Combination Method** (Entire threshold section):
   ```
   WRONG: "The threshold between the two rankings was determined dynamically by 
           computing the proportion of Grand Chamber cases and the proportion of 
           Importance=1 judgments"
   
   RIGHT: "We combined the normalized centrality values using a weighted geometric 
           mean: composite = high^w × low^(1-w), where the weight parameter w was 
           optimized (via grid search from 0.01 to 0.99) to maximize Spearman 
           correlation with ground truth scores for each network."
   ```

3. **Specific Combination** (Lines around "Degree Centrality... In-Degree Centrality"):
   ```
   WRONG: "Specifically, we combined Degree Centrality (for high-relevance scores) 
           with In-Degree Centrality (for low-relevance scores)."
   
   RIGHT: "We tested multiple combinations and found that Degree Centrality 
           (high-relevance) combined with Eigenvector Centrality (low-relevance) 
           achieved the best overall performance (43.9% win rate across 132 
           network-ground truth pairs)."
   ```

4. **Low-Relevance Selection for Doctypebranch** (Add clarification):
   ```
   ADD: "For doctypebranch ground truth, low-relevance centrality selection was 
         based on distinguishing GRANDCHAMBER (1) from CHAMBER (2) cases, excluding 
         COMMITTEE (3) cases from the selection process."
   ```

5. **Results Claims** (Lines around "highest counts of 14... and 16"):
   ```
   WRONG: "receiving the highest counts of 14 (Court Branch) and 16 (Importance)"
   
   RIGHT: "The composite measure achieved the highest correlation in 57 out of 132 
           network-ground truth combinations (43.2%), outperforming any single 
           centrality measure."
   ```

### Methodological Transparency Issue:

The paper describes a **simple, predetermined approach** but the implementation uses **sophisticated per-network optimization**. This is a significant methodological discrepancy that affects:

- **Reproducibility**: Readers cannot reproduce results from paper description
- **Validity**: Claims about "dynamic threshold based on dataset proportions" are false
- **Comparison**: The optimization gives composite an unfair advantage vs. individual centralities (it's optimized per network, they're not)

### Recommendation:

Either:
1. **Fix the paper** to accurately describe the weighted geometric mean with grid-search optimization
2. **Re-run analysis** using the method described in the paper (threshold based on dataset proportions)

The current state is misleading and would likely fail peer review if reviewers try to reproduce the results.
