# Why Degree+InDegree Shows Surprisingly Large Performance Gap

**Question**: Why does Degree+InDegree show a -42.8% performance gap between High-Rel and Low-Rel Priority, when these measures should be highly correlated?

---

## Key Findings

### 1. Correlation is Misleading

From Article 3 network (4,606 judgments):

| Metric | Value |
|--------|-------|
| **Pearson correlation** | 0.97 (very high) |
| **Spearman correlation** | 0.72 (moderate) |
| **Average rank difference** | 725 positions |
| **Top 35% overlap** | 76% |

**Interpretation**: While values are linearly related (Pearson = 0.97), the **rankings differ substantially** (Spearman = 0.72).

### 2. In-Degree = 50% of Degree (Directed Graph Property)

```
InDegree/Degree ratio: 0.50
```

In a directed citation graph:
- **Degree** = In-Degree + Out-Degree
- **In-Degree** ≈ 50% of Degree (on average)

This means In-Degree captures only **half the signal**, leading to:
- Different rank orderings
- Only 76% overlap in top 35%
- **10.6% overlap between top 35% Degree and bottom 35% InDegree**

### 3. Different Ground Truth Correlations

| Ground Truth | Degree | In-Degree | Better |
|--------------|--------|-----------|--------|
| **importance** | 0.467 | 0.453 | Degree (slightly) |
| **doctypebranch** | 0.455 | **0.620** | **In-Degree** |

In-Degree is actually **better** than Degree for doctypebranch prediction! This suggests:
- Degree is more balanced for "importance"
- In-Degree captures formal status (Grand Chamber) better

---

## Why Low-Rel Priority Fails for Degree+InDegree

### High-Relevance Priority (Script 04) - τ=0.35

**Process**:
1. Select top 35% by **Degree** (high-relevance)
2. Fill remaining 65% by **InDegree** (low-relevance)

**Why it works**: Prioritizes comprehensive connectivity (Degree), then refines with incoming citations (InDegree).

### Low-Relevance Priority (Script 06) - τ=0.15 or 0.35

**Process**:
1. Select bottom 15-35% by **InDegree** (least important by low-relevance)
2. Fill remaining 65-85% by **Degree** (high-relevance)

**Why it fails**:
- Bottom InDegree ≠ Bottom Degree (only 10.6% overlap with top Degree!)
- InDegree is **better** at predicting doctypebranch, so deprioritizing low InDegree is more harmful
- Optimal threshold differs (0.15 for doctypebranch vs 0.35 for importance), showing the measures don't align

---

## Mathematical Explanation

### The 76% Overlap Problem

If Degree and InDegree selected the **same** top 35%, then:
- High-Rel Priority (top 35% Degree + rest InDegree)
- Low-Rel Priority (bottom 35% InDegree + rest Degree)

Would be **complementary** strategies with similar performance.

But with only **76% overlap**:
- The 24% disagreement in top rankings creates fundamentally different composite rankings
- High-Rel Priority captures the "right" 35% for importance
- Low-Rel Priority excludes some important cases and includes wrong ones

### Threshold Mismatch

- **High-Rel Priority optimal**: τ = 0.35 for both ground truths
- **Low-Rel Priority optimal**: τ = 0.35 (importance), τ = 0.15 (doctypebranch)

This 2.3x difference for doctypebranch suggests the measures interact very differently when prioritizing high vs low relevance.

---

## Comparison with PageRank+Degree

### Why PageRank+Degree Shows Smaller Gap (-10.8%)

| Metric | Degree vs InDegree | PageRank vs Degree |
|--------|-------------------|-------------------|
| **Spearman correlation** | 0.72 | ~0.60-0.70 |
| **Measures same concept?** | Partial (both degree-based) | No (different algorithms) |
| **Low-Rel optimal threshold** | 0.05-0.35 | 0.05 |

PageRank+Degree shows smaller gap because:
1. **Very low threshold** (0.05): Low-Rel Priority deprioritizes only 5% of cases
2. **Different signals**: PageRank (authority) vs Degree (connectivity) are more independent
3. **Less harmful**: Excluding bottom 5% by Degree is less damaging than excluding 15-35% by InDegree

---

## Implications for Paper

### Key Takeaway

**Even when high and low centrality measures are correlated (0.72 Spearman), the selection logic of High-Rel vs Low-Rel Priority produces dramatically different results.**

The paper's claim that convergence occurs "when the same measure wins for both high and low" should be strengthened:

> "Convergence only occurs when the **exact same measure** (e.g., in-degree for both high and low) is used. Even **highly correlated measures** (e.g., Degree and In-Degree, Spearman ρ=0.72) produce substantially different results (-42.8% performance gap) due to differences in:
> 1. Rank ordering (only 76% overlap in top rankings)
> 2. Ground truth prediction strength
> 3. Optimal threshold values"

### Recommendation

Do NOT use Low-Relevance Priority, even when high and low centralities are correlated. The -31.6% average performance gap demonstrates that High-Relevance Priority is fundamentally superior.

---

## Supporting Data

All analysis based on:
- **Sample network**: Article 3 (4,606 judgments)
- **Full analysis**: 66 sub-networks across 3 combinations
- **Results**: `results/analysis/07_priority_comparison/`
