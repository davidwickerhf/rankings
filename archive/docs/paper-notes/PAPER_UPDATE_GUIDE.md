# Paper Update Guide - Low-Relevance Priority Removal

This document provides the complete replacement text for updating the paper to reflect script 04 methodology (optimized universal threshold with High-Relevance Priority only).

---

## Section 1: Optimizing Centrality (Lines 543-586)

### What to Replace
- **Current**: Lines 543-586 (entire "Optimizing Centrality" subsection)
- **Delete entirely**: Lines 556-558 (Low-Relevance Priority convergence claim)

### New Text
See: `PAPER_REWRITE_OPTIMIZING_CENTRALITY.tex`

**Key Changes**:
1. ✅ Introduces three combinations tested (PageRank+Degree, Degree+Eigenvector, Degree+InDegree) with justification
2. ✅ Describes both High-Rel and Low-Rel Priority approaches
3. ✅ Dismisses Low-Rel Priority as empirically inferior (-31.6% performance gap)
4. ✅ Explains grid search optimization for threshold τ ∈ [0.05, 0.95]
5. ✅ Lists optimal thresholds found for each combination
6. ✅ Reports win rates for all three combinations
7. ✅ Highlights Degree+Eigenvector as best performer (73.1% win rate)

**Figure Needed**:
- **Figure reference**: `\ref{fig:composite_performance}` 
- **Source files**: `results/analysis/04_optimized_threshold_composite/comparison_*.png`
- **Content**: Horizontal bar charts showing win rates for all three combinations across network types and ground truths
- **Suggested caption**: "Performance comparison of composite measures across network types. Win rate represents the proportion of networks where each composite measure outperformed all 13 individual centrality measures. Degree + Eigenvector demonstrated the strongest overall performance."

---

## Section 2: Discussion (Lines 589-596)

### What to Replace
- **Current**: Lines 589-596 (first two paragraphs of Discussion)

### New Text
See: `PAPER_REWRITE_DISCUSSION.tex`

**Key Changes**:
1. ✅ Updates to reflect three combinations tested (not just Degree+InDegree)
2. ✅ Lists all low-relevance performers (Degree, Eigenvector, In-Degree)
3. ✅ Reports Degree+Eigenvector as best performer with specific win rates
4. ✅ Emphasizes data-driven threshold optimization
5. ✅ Highlights generalizability across balanced/unbalanced datasets

---

## Section 3: Figure Updates

### Current Figure to Remove or Update
- **Figure \ref{fig:performers_withcomposite}** (lines 562-584)
- **Issue**: Shows only Degree+InDegree composite, not all three combinations

### Replacement Options

#### Option A: Update Existing Figure
Keep Figure \ref{fig:performers_withcomposite} but:
- Update caption to clarify it shows only ONE example (Degree+InDegree)
- Add reference to comprehensive comparison in new figure

#### Option B: Replace with Comprehensive Figure
Create new figure showing all three combinations:
- **Layout**: 3×2 grid (3 combinations × 2 ground truths)
- **Source**: `results/analysis/04_optimized_threshold_composite/comparison_*.png`
- **Each subplot**: Horizontal bar chart with composite (red) vs individual centralities (teal)

---

## Section 4: Conclusion (Lines 610-616)

### Current Text (Line 613)
> "Composite measures combining the strengths of the best-performing measures outperformed all other centrality measures tested."

### Suggested Enhancement
> "Composite measures combining the strengths of high-relevance and low-relevance optimized centralities substantially outperformed all individual measures. The Degree + Eigenvector combination achieved win rates up to 73.1%, compared to 15-20% for individual centralities, demonstrating the value of leveraging complementary signals."

---

## Section 5: Limitations (Lines 599-607)

### Add New Paragraph (After line 603)

**Insert**:
> The composite measures tested require optimal thresholds that were determined empirically through grid search across 66 sub-networks. While these thresholds (τ = 0.30-0.70) demonstrated robust performance across network types and ground truths, their generalizability to other legal domains or citation networks requires further validation. Additionally, the High-Relevance Priority approach consistently outperformed Low-Relevance Priority (average difference: -31.6%), suggesting an inherent asymmetry in how high-relevance and low-relevance signals combine. This finding has implications for composite measure design in other precedent-based citation networks.

---

## Section 6: Abstract Updates

### If Current Abstract Mentions
- ❌ "Low-Relevance Priority"
- ❌ "Both approaches converge"
- ❌ "In-degree for both high and low"

### Update To
- ✅ "High-Relevance Priority composite measures"
- ✅ "Degree + Eigenvector achieved 73.1% win rate"
- ✅ "Three combinations systematically evaluated"

---

## Complete Checklist

### Text Updates
- [ ] Replace lines 543-586 with new Optimizing Centrality section
- [ ] Replace lines 589-596 with new Discussion paragraphs
- [ ] Update line 613 in Conclusion with specific performance numbers
- [ ] Add new paragraph to Limitations section
- [ ] Review Abstract for Low-Rel Priority mentions (remove if present)

### Figure Updates
- [ ] Create/add Figure \ref{fig:composite_performance} showing all three combinations
- [ ] Update Figure \ref{fig:performers_withcomposite} caption or replace figure
- [ ] Verify all figure references point to correct files

### Data/Results Updates
- [ ] Ensure all reported win rates match script 04 results
- [ ] Verify optimal thresholds: PageRank+Degree (0.65, 0.70), Degree+Eigenvector (0.30, 0.35), Degree+InDegree (0.35, 0.35)
- [ ] Confirm Degree+Eigenvector as best performer (73.1% max win rate)

### Supplementary Materials
- [ ] Include script 04 detailed results in repository
- [ ] Include comparison with Low-Rel Priority (script 06-07 results) if desired
- [ ] Document optimal thresholds and their derivation

---

## Supporting Documentation

All analysis files available in:
- `results/analysis/04_optimized_threshold_composite/` - High-Rel Priority results (USE THIS)
- `results/analysis/06_low_relevance_priority/` - Low-Rel Priority results (for reference)
- `results/analysis/07_priority_comparison/` - Direct comparison
- `results/analysis/PROFESSOR_QUESTION_SUMMARY.md` - Executive summary for professor
- `results/analysis/DEGREE_INDEGREE_ANALYSIS.md` - Why correlation ≠ convergence

---

## Notes on Style

The rewritten text maintains the paper's existing style:
- ✅ Formal academic tone
- ✅ Precise technical descriptions with mathematical notation
- ✅ Clear enumeration of methods and findings
- ✅ Balanced discussion of results without over-claiming
- ✅ Acknowledges limitations and future work

**Word Count**: New Optimizing Centrality section is ~750 words (original ~300), accounting for comprehensive methodology description.
