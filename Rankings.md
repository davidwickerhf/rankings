# Network Analysis Results Documentation

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

## Conclusion

The current ranking-based approach is demonstrably problematic, producing identical results across different combination methods. Working with raw centrality values would preserve more information and potentially lead to more meaningful distinctions between combination methods. This is particularly important given that our selected centrality measures (in-degree and relative in-degree) are inherently related and produce similar distributions.
