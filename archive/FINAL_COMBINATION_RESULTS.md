# FINAL Centrality Combination Results (CORRECTED)

## ✅ **Data Verified Safe**

The corrected analysis properly handles balanced networks by:
1. Loading the full unbalanced network with all centrality scores
2. Reading `nodes.json` from `networks/merged-article-edges/split-balanced-*/article_X/`
3. Filtering unbalanced centralities to only the ECLIs in the balanced network
4. Calculating composite and correlations on the filtered subset

---

## 🏆 **WINNER: Degree + PageRank**

### **Overall Performance (All Networks)**

| Combination | Balanced-Importance | Balanced-Doctypebranch | Unbalanced | **AVERAGE** |
|-------------|---------------------|------------------------|------------|-------------|
| **Degree + PageRank** | **41.7%** 🥇 | **43.8%** 🥇 | **40.4%** 🥈 | **41.9%** 🥇 |
| Degree + InDegree | 31.3% | 34.4% | **42.3%** 🥇 | 35.9% |
| InDegree + HitsHub | 14.6% | 15.6% | 28.8% | 19.7% |

---

## Detailed Results

### **1. UNBALANCED Networks (26 networks)**

| Combination | Importance Wins | Importance % | Doctypebranch Wins | Doctypebranch % | Average |
|-------------|-----------------|--------------|-------------------|-----------------|---------|
| **Degree + InDegree** | 13/26 | **50.0%** 🥇 | 9/26 | 34.6% | **42.3%** |
| **Degree + PageRank** | 12/26 | 46.2% | 9/26 | 34.6% | 40.4% |
| InDegree + HitsHub | 9/26 | 34.6% | 6/26 | 23.1% | 28.8% |

**Winner for Unbalanced**: **Degree + InDegree** (50% importance win rate)

---

### **2. BALANCED-IMPORTANCE Networks (24 networks)**

| Combination | Importance Wins | Importance % | Doctypebranch Wins | Doctypebranch % | Average |
|-------------|-----------------|--------------|-------------------|-----------------|---------|
| **Degree + PageRank** | 9/24 | **37.5%** 🥇 | 11/24 | **45.8%** 🥇 | **41.7%** |
| Degree + InDegree | 6/24 | 25.0% | 9/24 | 37.5% | 31.3% |
| InDegree + HitsHub | 3/24 | 12.5% | 4/24 | 16.7% | 14.6% |

**Winner for Balanced-Importance**: **Degree + PageRank** (41.7% average)

---

### **3. BALANCED-DOCTYPEBRANCH Networks (16 networks)**

| Combination | Importance Wins | Importance % | Doctypebranch Wins | Doctypebranch % | Average |
|-------------|-----------------|--------------|-------------------|-----------------|---------|
| **Degree + PageRank** | 8/16 | **50.0%** 🥇 | 6/16 | 37.5% | **43.8%** |
| Degree + InDegree | 6/16 | 37.5% | 5/16 | 31.2% | 34.4% |
| InDegree + HitsHub | 3/16 | 18.8% | 2/16 | 12.5% | 15.6% |

**Winner for Balanced-Doctypebranch**: **Degree + PageRank** (50% importance, 43.8% average)

---

## Key Insights

### **1. Degree + PageRank Wins Overall** 🏆
- **Best average performance**: 41.9% across all network types
- **Dominates balanced networks**: 41.7% (balanced-importance), 43.8% (balanced-doctypebranch)
- **Consistent performance**: Never drops below 34.6% in any category

### **2. Network Type Affects Performance**
- **Unbalanced**: Degree+InDegree wins (50% for importance)
- **Balanced**: Degree+PageRank wins (41-44% average)
- **Why?** Balancing changes class distribution, making PageRank's recursive importance signal more valuable

### **3. InDegree + HitsHub Consistently Underperforms**
- Only 14-20% win rate across all configurations
- **HitsHub is a weak signal** for low-importance cases
- Your notebook's dynamic selection often picked this sub-optimal combination

---

## Recommendation for Your Paper

### **Best Choice: Degree + PageRank**

**Rationale:**
1. **Highest overall performance** (41.9% average)
2. **Wins decisively in balanced scenarios** (where composite measures matter most)
3. **Theoretically sound**:
   - **Degree**: Overall connectivity (hub cases)
   - **PageRank**: Recursive importance (authority cascade)
   - **Combination**: Balances local connectivity with global authority

### **Paper Text Suggestion:**

```latex
We developed a composite measure combining Degree Centrality with PageRank 
to capture both local network integration and recursive citation authority. 
This combination was selected through empirical testing across 66 sub-networks 
(26 unbalanced, 24 balanced-by-importance, 16 balanced-by-doctypebranch), 
where it achieved an average win rate of 41.9%, outperforming alternative 
combinations including Degree+InDegree (35.9%) and InDegree+HitsHub (19.7%).

The composite measure proved particularly effective in balanced network scenarios, 
achieving 41.7-43.8% win rates, compared to 40.4% in unbalanced networks. This 
suggests that combining local connectivity (Degree) with global authority 
(PageRank) provides robust performance across varying class distributions.
```

---

## Alternative: Network-Specific Selection

If you want to keep different combinations for different network types:

```latex
Our analysis revealed that optimal centrality combinations depend on network 
characteristics. For unbalanced networks (natural class distribution), 
Degree+InDegree achieved the highest performance (50% win rate for importance). 
However, in balanced networks (equalized class sizes), Degree+PageRank 
outperformed all alternatives (42-44% win rate). This suggests that balancing 
fundamentally changes which centrality signals are most predictive.
```

---

## Files Generated

All results saved to: `results/fixed-merged-subarticles-edges/composite_manual_test_corrected/`

**Graphs** (6 PNG files):
- `comparison_unbalanced_importance.png` / `comparison_unbalanced_doctypebranch.png`
- `comparison_balanced-importance_importance.png` / `comparison_balanced-importance_doctypebranch.png`
- `comparison_balanced-doctypebranch_importance.png` / `comparison_balanced-doctypebranch_doctypebranch.png`

**Data**:
- `combination_summary.csv` - Win rates per combination/network/ground truth
- `detailed_results.json` - Per-network results with correlations and weights

---

## Next Steps

### Option A: Use Degree + PageRank (Recommended)
1. Update paper text to reference Degree + PageRank composite
2. Use these corrected graphs as Figure 7
3. Report 41.9% average win rate

### Option B: Use Network-Specific Combinations
1. Degree + InDegree for unbalanced networks (50% for importance)
2. Degree + PageRank for balanced networks (42-44% average)
3. Explain in paper that optimal combination varies by network type

### Option C: Verify Against Notebook Results
Would you like me to:
- Check what combinations your notebook actually selected per network?
- Compare notebook results to these manual test results?
- Identify discrepancies?

**My recommendation: Go with Option A (Degree + PageRank) for simplicity and best overall performance.**
