# Composite Ranking Calculations

This document explains the mathematical foundations and implementation of two composite ranking approaches: weighted geometric mean and threshold-based combination.

## Table of Contents

1. [Normalization](#normalization)
2. [Weighted Geometric Mean](#weighted-geometric-mean)
3. [Threshold Combination](#threshold-combination)
4. [Implementation](#implementation)

## Normalization

Before combining centrality measures, we normalize them to ensure fair comparison:

```python
def normalize_centrality(values):
    """
    Normalize centrality values while preserving relative differences using percentile ranking.

    Args:
        values: pd.Series of centrality values

    Returns:
        pd.Series of normalized values in range [1, 1000]
    """
    non_zero = values[values != 0]
    if len(non_zero) == 0:
        return values

    # Create percentile ranks (0-1 scale)
    ranks = pd.Series(index=non_zero.index)
    ranks.loc[non_zero.index] = non_zero.rank(pct=True, ascending=False)

    # Scale to 1-1000 range
    ranks = ranks * 999 + 1

    # Fill zeros with lowest importance (1000)
    ranks = ranks.reindex(values.index, fill_value=1000)
    return ranks
```

### Mathematical Properties

1. **Range Preservation**: Output is bounded [1, 1000]
2. **Order Preservation**: If x₁ > x₂ then rank(x₁) < rank(x₂)
3. **Zero Handling**: All zero values map to 1000 (lowest importance)

## Weighted Geometric Mean

The weighted geometric mean combines two normalized centrality measures:

```python
def weighted_combine(high, low, weight):
    """
    Combine normalized values using weighted geometric mean.

    Args:
        high: pd.Series of normalized high-importance centrality
        low: pd.Series of normalized low-importance centrality
        weight: Weight for high-importance measure [0,1]

    Returns:
        pd.Series of combined scores
    """
    epsilon = 1e-10  # Avoid zero values
    return np.power(high + epsilon, weight) * np.power(low + epsilon, (1-weight))
```

### Mathematical Foundation

For centrality values h and l with weight w:

composite = h^w \* l^(1-w)

Properties:

1. **Monotonicity**: Increases with both input measures
2. **Bounded**: Output ∈ [1, 1000] when inputs ∈ [1, 1000]
3. **Weight Balance**: w=0.5 gives equal influence to both measures

## Threshold Combination

The threshold approach uses the high-importance measure above a percentile threshold:

```python
def threshold_combine(high, low, threshold_pct):
    """
    Combine using threshold on normalized values.

    Args:
        high: pd.Series of normalized high-importance centrality
        low: pd.Series of normalized low-importance centrality
        threshold_pct: Percentile threshold [0,100]

    Returns:
        pd.Series of combined scores
    """
    if len(high[high != 0]) == 0:
        return low

    threshold = np.percentile(high[high != 0], 100 - threshold_pct)

    result = high.copy()
    mask = high <= threshold
    result[mask] = low[mask]

    return result
```

### Mathematical Properties

1. **Discontinuity**: Sharp transition at threshold
2. **Range Preservation**: Output ∈ [min(high,low), max(high,low)]
3. **Selective Combination**: Uses high values only above threshold

## Implementation

The full implementation includes optimization to find best parameters:

```python
def create_weighted_composite_ranking(df, high_centrality, low_centrality, ground_truth):
    """
    Create composite using weighted combination of normalized centrality values.

    Args:
        df: DataFrame with centrality measures
        high_centrality: Column name of high-importance measure
        low_centrality: Column name of low-importance measure
        ground_truth: Column name of ground truth values

    Returns:
        (best_composite, best_weight): Optimal composite ranking and weight
    """
    # Input validation
    assert high_centrality in df.columns
    assert low_centrality in df.columns

    # Get and normalize values
    high_values = df[high_centrality]
    low_values = df[low_centrality]

    high_norm = normalize_centrality(high_values)
    low_norm = normalize_centrality(low_values)

    # Find optimal weight
    best_weight = None
    best_corr = float('-inf')
    best_composite = None

    for weight in np.arange(0.01, 1.00, 0.01):
        composite = weighted_combine(high_norm, low_norm, weight)
        corr = spearmanr(composite, df[ground_truth])[0]

        if corr > best_corr:
            best_corr = corr
            best_weight = weight
            best_composite = composite

    # Validate results
    assert best_composite.nunique() > 1
    assert not np.isnan(best_corr)

    return best_composite, best_weight

def create_threshold_composite_ranking(df, high_centrality, low_centrality, ground_truth):
    """
    Create composite using threshold on normalized centrality values.

    Args:
        df: DataFrame with centrality measures
        high_centrality: Column name of high-importance measure
        low_centrality: Column name of low-importance measure
        ground_truth: Column name of ground truth values

    Returns:
        (best_composite, best_threshold): Optimal composite ranking and threshold
    """
    # Input validation
    assert high_centrality in df.columns
    assert low_centrality in df.columns

    # Get and normalize values
    high_values = df[high_centrality]
    low_values = df[low_centrality]

    high_norm = normalize_centrality(high_values)
    low_norm = normalize_centrality(low_values)

    # Find optimal threshold
    best_threshold = None
    best_corr = float('-inf')
    best_composite = None

    for threshold_pct in range(1, 100):
        composite = threshold_combine(high_norm, low_norm, threshold_pct)
        corr = spearmanr(composite, df[ground_truth])[0]

        if corr > best_corr:
            best_corr = corr
            best_threshold = threshold_pct
            best_composite = pd.Series(composite)

    # Validate results
    assert best_composite.nunique() > 1
    assert not np.isnan(best_corr)

    return best_composite, best_threshold
```

Both approaches:

1. Normalize input measures to [1,1000] range
2. Optimize parameters by maximizing Spearman correlation with ground truth
3. Return optimal composite ranking and parameters
4. Include validation checks for ranking variation and correlation

The weighted geometric mean provides smooth combination while the threshold approach allows for selective use of measures based on their values.
