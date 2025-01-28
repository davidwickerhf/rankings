## Statistical Analysis of Centrality Measures

### Trend Significance

All centrality measures showed statistically significant trends over time (Mann-Kendall test, 99% confidence, p < 0.01):

#### Increasing Trends:

- core_number (τ = 0.1634)
- degree_centrality (τ = 0.1396)
- hits_hub (τ = 0.1299)
- out_degree_centrality (τ = 0.2677)

#### Decreasing Trends:

- betweenness_centrality (τ = -0.0224)
- closeness_centrality (τ = -0.2001)
- disruption (τ = -0.0415)
- eigenvector_centrality (τ = -0.1967)
- harmonic_centrality (τ = -0.1965)
- hits_authority (τ = -0.1012)
- in_degree_centrality (τ = -0.1122)
- pagerank (τ = -0.1599)
- relative_in_degree_centrality (τ = -0.1122)

### Value Ranges and Normalization

Most centrality measures were normalized to the [0,1] range, with some exceptions:

#### Normalized Measures [0,1]:

- betweenness_centrality (0 to 0.0622)
- degree_centrality (0 to 0.1060)
- in_degree_centrality (0 to 0.1059)
- out_degree_centrality (0 to 0.0077)
- hits_authority (0 to 0.0217)
- hits_hub (0 to 0.0006)
- pagerank (0 to 0.0772)
- relative_in_degree_centrality (0 to 0.1059)

#### Non-normalized Measures:

- core_number (0 to 35.0000)
- harmonic_centrality (0 to 9151.3917)
- disruption (-1 to 1)

#### Partially Normalized:

- closeness_centrality (0 to 0.2843)
- eigenvector_centrality (0 to 0.2205)

### Disruption Index Analysis

The disruption index shows positive correlations with both ground truths (Doctypebranch: 0.1609, Importance: 0.2660), unlike other centrality measures which show negative correlations. This is expected behavior because:

1. Disruption index works inversely to traditional centrality measures:

   - Positive disruption scores indicate more "disruptive" cases (cases that cause subsequent cases to not cite their predecessors)
   - Negative disruption scores indicate more "consolidating" cases (cases that cause subsequent cases to still cite their predecessors)

2. This aligns with the ground truth scoring:
   - Lower importance scores (1,2) represent more significant/foundational cases
   - Higher importance scores (3,4) represent less significant cases

Therefore, the positive correlation validates that more disruptive cases (higher disruption score) tend to be less foundational (higher importance score), while more consolidating cases (lower disruption score) tend to be more foundational (lower importance score).

### Key Findings

1. All centrality measures showed statistically significant trends over time
2. Out_degree_centrality showed the strongest increasing trend (τ = 0.2677)
3. Closeness_centrality showed the strongest decreasing trend (τ = -0.2001)
4. Most measures were normalized to [0,1], with notable exceptions being core_number, harmonic_centrality, and disruption
5. Disruption's positive correlation with ground truths validates its intended behavior as an inverse measure of case significance
