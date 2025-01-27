# Network Analysis Results Documentation

1. [Overview](#overview)
2. [Key Findings](#key-findings)
   - [Best Centrality Selection](#best-centrality-selection)
   - [Selection Process](#selection-process)
   - [Statistical Analysis of Selected Centralities](#statistical-analysis-of-selected-centralities)
3. [Critical Analysis](#critical-analysis)
   - [Similarity of Centrality Measures](#similarity-of-centrality-measures)
   - [Issues with Ranking Approach](#issues-with-ranking-approach)
   - [Recommendations](#recommendations)
4. [Statistical Relevance](#statistical-relevance)
5. [Mathematical Analysis of Ranking vs. Direct Values](#mathematical-analysis-of-ranking-vs-direct-values)
   - [Goal Definition](#goal-definition)
   - [Current Approach Using Rankings](#current-approach-using-rankings)
   - [Mathematical Arguments](#mathematical-arguments)
   - [Mathematical Proof of Information Loss](#mathematical-proof-of-information-loss)
   - [Recommended Approach](#recommended-approach)
   - [Statistical Benefits of Direct Values](#statistical-benefits-of-direct-values)
6. [Conclusion](#conclusion)

## Overview

This document details the analysis of network centrality measures for the `article_1` network, focusing on the selection of optimal centrality measures and their combination methods.

## Key Findings

### Best Centrality Selection

For both ground truth measures (`importance` and `doctypebranch`), the analysis selected:

- Best High: `in_degree_centrality`
- Best Low: `relative_in_degree_centrality`

### Selection Process

The centralities were chosen based on their Spearman correlation with the ground truth measures.

### Statistical Analysis of Selected Centralities

The descriptive statistics reveal nearly identical distributions for both measures:

```
       in_degree_centrality  relative_in_degree_centrality
count           5938.000000                    5938.000000
mean               0.000187                       0.000187
std                0.000679                       0.000679
min                0.000000                       0.000000
25%                0.000000                       0.000000
50%                0.000000                       0.000000
75%                0.000168                       0.000168
max                0.019033                       0.019030
```

## Critical Analysis

### Similarity of Centrality Measures

The selected centralities (`in_degree_centrality` and `relative_in_degree_centrality`) show remarkably similar distributions. This is not surprising given that relative in-degree centrality is derived from in-degree centrality, essentially normalizing it by the total possible incoming edges.

### Issues with Ranking Approach

#### Current Implementation

The current approach converts centrality values to rankings before combination:

```python
high_ranking = high_values.rank(method='average', ascending=False)
low_ranking = low_values.rank(method='average', ascending=False)
```

This results in identical rankings across all methods:

```
High ranking values:  [3.8015e+03, 1.3135e+03, 8.2150e+02, ...]
Low ranking values:   [3.8015e+03, 1.3135e+03, 8.2150e+02, ...]
Composite values:     [3.8015e+03, 1.3135e+03, 8.2150e+02, ...]
```

#### Statistical Implications

1. **Loss of Information**: Converting to rankings before combination eliminates the subtle differences in the original centrality values (visible in the raw values):

```
High centrality: [0.0, 0.00016844, 0.00033687, ...]
Low centrality:  [0.0, 0.00016841, 0.00033681, ...]
```

2. **Tie Handling**: The use of `method='average'` in ranking means ties are handled identically, further reducing differentiation between measures.

### Recommendations

1. **Direct Value Usage**

   - Consider using centrality values directly instead of rankings
   - This preserves the subtle differences between measures
   - Maintains the original scale and distribution information

2. **Alternative Ranking Methods**

   - If rankings must be used, consider different tie-breaking methods
   - Options include 'first', 'min', or 'max' instead of 'average'

3. **Measure Selection**
   - Given the similarity between the selected measures, consider:
     - Including more diverse centrality measures
     - Using measures that capture different network properties
     - Implementing alternative selection criteria beyond correlation

## Statistical Relevance

The current ranking approach is statistically suboptimal for several reasons:

1. **Information Loss**: Converting to ranks discards valuable information about the magnitude of differences between nodes.

2. **Identical Results**: The current implementation produces identical rankings (correlation 0.42233110999129997 for importance), suggesting the method is not effectively distinguishing between different combination approaches.

3. **Scale Considerations**: The original centrality values operate on different scales but contain meaningful relative differences that are lost in ranking.

## Mathematical Analysis of Ranking vs. Direct Values

### Goal Definition

We aim to create a composite metric `C(v)` for each node `v` that:

1. Uses high-correlation metric `H(v)` for high values
2. Uses low-correlation metric `L(v)` for low values
3. Maximizes correlation with ground truth `G(v)`

### Current Approach Using Rankings

Given:

- Original centrality values: `H(v)` and `L(v)`
- Rankings of these values: `R_H(v)` and `R_L(v)`

#### Implementation Methods

1. **Threshold Method**:

```python
if R_H(v) > threshold:
    C(v) = R_H(v)
else:
    C(v) = R_L(v)
```

2. **Weight Method**:

```python
C(v) = w * R_H(v) + (1-w) * R_L(v)
```

### Mathematical Arguments

#### Arguments For Rankings

1. **Normalization**:

   - Rankings provide uniform scale [1, n]
   - Makes combination mathematically straightforward
   - Eliminates issues with different value ranges

2. **Monotonic Transformation**:
   - For Spearman correlation: `corr(rank(x), G) = corr(x, G)`
   - Preserves ordinal relationships

#### Arguments Against Rankings

1. **Loss of Magnitude Information**:

```
Original values H: [0.001, 0.002, 0.1]
Original values L: [0.001, 0.003, 0.004]
Rankings both become: [3, 2, 1]
```

2. **Tie Handling Issues**:

```python
# With method='average'
[0.001, 0.001, 0.002] → [1.5, 1.5, 3]
```

3. **Scale Distortion**:
   - Small centrality differences → large rank differences
   - Large centrality differences → small rank differences

### Mathematical Proof of Information Loss

Consider this example:

1. **Original Values**:

```
H(v) = [0.1, 0.2, 0.8]
L(v) = [0.15, 0.25, 0.3]
```

2. **Rankings**:

```
R_H(v) = [3, 2, 1]
R_L(v) = [3, 2, 1]
```

3. **Weighted Combination**:
   - With original values: `C(v) = w*H(v) + (1-w)*L(v)`
   - Different weights produce different orderings:

```
w=0.7: [0.115, 0.215, 0.65]
```

4. **Ranked Combination**:
   - `C_rank(v) = w*R_H(v) + (1-w)*R_L(v)`
   - All weights produce same ordering:

```
Any w: [3, 2, 1]
```

### Recommended Approach

Use original centrality values with:

1. **Threshold Method**:

```python
C(v) = {
    H(v)   if H(v) > threshold
    L(v)   otherwise
}
```

2. **Weight Method**:

```python
C(v) = w*H(v) + (1-w)*L(v)
```

### Statistical Benefits of Direct Values

1. **Information Preservation**:

   - Maintains relative differences between nodes
   - Allows for more nuanced combinations
   - Better reflects network structure

2. **Statistical Validity**:
   - Preserves original probability distributions
   - Maintains actual magnitude of differences
   - Enables more meaningful statistical analysis

## Conclusion

This mathematical analysis strongly supports the use of direct centrality values over rankings. The current implementation's identical results across different combination methods (correlation 0.42233110999129997) demonstrates the information loss inherent in the ranking approach. The recommended shift to direct value manipulation would preserve the subtle differences between measures and potentially lead to more meaningful distinctions between combination methods.
