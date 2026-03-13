# Disruption Analysis: Findings and Considerations

## Overview

This document provides an analysis of the **Disruption** centrality measure based on the findings discussed. The analysis explores its unique characteristics, its performance compared to other centrality measures, and its behavior in identifying high- and low-importance judgments within a network.

---

## What is Disruption?

Disruption is a centrality measure that evaluates a node’s disruptiveness within a network. It measures how often a node is cited exclusively versus how often it shares citations with its references. The formula is:

\[
\text{Disruption} = \frac{i - j}{i + j + k}
\]

- **i**: Citations only for the node itself.
- **j**: Citations shared with the node’s references.
- **k**: Citations only for the references.

This measure captures the extent to which a node’s influence is isolated rather than integrated into the broader network.

---

## Key Findings

### 1. **Disruption’s Correlation Behavior**

- **Positive Correlations**: Disruption exhibits positive correlations with ground truths like Importance and Doctypebranch. This means higher Disruption scores align with less important judgments (e.g., ground truth value = 3).
- Unlike most centrality measures (e.g., In-Degree Centrality, PageRank), which correlate negatively with importance (higher centrality for more important judgments), Disruption’s behavior is inverse.

**Implications**:

- Disruption is effective at identifying **low-importance judgments**, where higher scores indicate less relevance in the network.
- It is less effective at predicting high-importance judgments, as its relationship with importance is less direct.

### 2. **Performance in High- and Low-Importance Predictions**

- **Strengths**:
  - Disruption performs well in differentiating less important judgments.
  - Its ability to capture structural disruptiveness makes it a complementary measure to traditional centralities.
- **Weaknesses**:
  - Disruption is rarely selected as the best predictor for high-importance judgments due to weaker correlations compared to other centralities like In-Degree or PageRank.
  - Its unique behavior may limit its application in predicting integrated, highly central nodes.

### 3. **Selection in Best-High and Best-Low Predictions**

In the function used to select the best centralities for predicting high and low ground truth scores, Disruption is treated differently:

- For Disruption, **positive correlations** are minimized (\(1 - \text{correlation}\)).
- For other centralities, **negative correlations** are minimized (\(1 + \text{correlation}\)).

**Findings**:

- While this differentiation is conceptually sound, Disruption is often outperformed by traditional centralities due to:
  - Weaker correlation values compared to measures like In-Degree Centrality.
  - Its strength in identifying low-importance judgments not being sufficiently captured in the selection logic.

---

## Impact of Edge Density on Disruption

The performance and correlation behavior of Disruption are highly sensitive to the **density of edges** in the network. Changes in edge density can significantly alter its effectiveness:

### 1. **Sparse Networks (Fewer Edges)**

- When the network is sparse (e.g., ~28k edges for ~27k nodes):
  - Disruption has a **high negative correlation** with ground truths because nodes with higher Disruption scores are more likely to represent low ground truth values (high importance).
  - Fewer edges mean more isolated nodes, making Disruption values more variable and impactful.

### 2. **Dense Networks (More Edges)**

- When the network becomes dense (e.g., ~230k edges for ~27k nodes):
  - Disruption's correlation weakens and often becomes **positive**, as the additional edges reduce its ability to differentiate nodes.
  - Higher edge density leads to increased shared citations (**j**) and fewer exclusive citations (**i**), diminishing the discriminative power of the Disruption measure.

### 3. **Why Does This Happen?**

- **Loss of Variability**: In dense networks, Disruption scores converge as shared citations dominate, reducing their variability and ability to differentiate between nodes.
- **Shift in Focus**: Disruption shifts from highlighting isolated nodes to reflecting shared influence, which aligns less with the ground truths.
- **Diluted Structural Signals**: Adding edges completes the network but diminishes the structural signals that Disruption relies on, such as isolation and unique influence.

### 4. **Implications**

- Disruption is **more effective in sparse networks**, where structural isolation matters more.
- In dense networks, its utility diminishes, and other measures like In-Degree Centrality or PageRank often outperform it.

---

## Recommendations

1. **Adjust Evaluation Logic**:

   - Consider weighting Disruption’s correlations higher for low-importance predictions (best-low) to better highlight its unique strengths.

   Example adjustment:

   ```python
   if centrality == 'disruption' and high_or_low == 'low':
       errors[centrality] = 1 - corr * 2  # Amplify its importance in low-importance predictions
   else:
       errors[centrality] = 1 - corr
   ```

2. **Threshold Edges for Sparsity**:

   - Remove weaker or less significant edges to restore some sparsity and amplify Disruption’s ability to differentiate nodes.

3. **Normalize Disruption**:

   - Adjust the formula to account for increasing edge density, ensuring its variability and relevance are maintained in denser networks.

4. **Complement with Other Measures**:

   - Combine Disruption with centralities like In-Degree or PageRank to capture both isolated and integrated influence.

5. **Analyze Sparsity Scenarios**:
   - Perform separate analyses on sparse and dense networks to better understand Disruption’s behavior and contributions.

---

## Conclusion

Disruption is a valuable centrality measure with unique strengths in identifying low-importance judgments and highlighting structural disruptiveness in networks. While it correlates positively with ground truths and behaves differently from traditional centralities, its performance is highly sensitive to edge density.

- In sparse networks, Disruption thrives by capturing meaningful structural signals, leading to stronger correlations with ground truths.
- In dense networks, its discriminative power diminishes, and it becomes less effective compared to measures like In-Degree Centrality or PageRank.

By considering these adjustments and recommendations, Disruption can play a more prominent role in network analysis, particularly in scenarios where identifying low-importance nodes is critical.
