# Rebuttal Draft and Result Traceability

This document traces the main claims in the submitted paper back to the current script outputs in this repository, then provides reviewer-by-reviewer rebuttal text grounded in those outputs.

## Traceability of Submitted Paper to Script Outputs

### Submitted paper used for trace-back

- Submitted PDF reviewed here:
  - `/Users/davidwickerhf/Downloads/Why_Some_Judgments_Matter_More_Than_Others__Advancing_Network_Centrality_Analysis__ICAIL_2026_ (2).pdf`

### Main provenance mapping

| Submitted item / claim | Source script | Output files | Notes |
| --- | --- | --- | --- |
| Figure 3: high/low performer frequencies across unbalanced, balanced-doctypebranch, balanced-importance subnetworks | `scripts/analysis/01_find_best_high_low.py` | `results/analysis/01_high_low_performers/*.png`, `results/analysis/01_high_low_performers/summary.txt` | This is the source for the six high/low performer bar charts. The submitted narrative sentence at the end of page 6 should be revised for clarity and to align more closely with what the figure shows. |
| Composite methodology in the submitted paper: High-Relevance Priority + threshold grid search | `scripts/analysis/04_test_optimized_threshold_composite.py` | `results/analysis/04_optimized_threshold_composite/combination_summary.csv`, `results/analysis/04_optimized_threshold_composite/detailed_results.json` | Table 5 in the submitted paper matches these optimized thresholds exactly. |
| Table 5 thresholds: `(0.65, 0.70)`, `(0.30, 0.35)`, `(0.35, 0.35)` | `scripts/analysis/04_test_optimized_threshold_composite.py` | `results/analysis/04_optimized_threshold_composite/combination_summary.csv` | Exact match to the submitted paper. |
| Figure 4: composite vs individual performance on balanced networks | `scripts/analysis/08_visualize_balanced_overlay.py` | `results/analysis/08_balanced_overlay_visualizations/balanced_doctypebranch_overlay.png`, `results/analysis/08_balanced_overlay_visualizations/balanced_importance_overlay.png` | These are the balanced overlay visualizations used for the submitted composite figure. |
| Submitted claim that Low-Relevance Priority underperformed by `-31.6%` on average | `scripts/analysis/06_test_low_relevance_priority.py` and `scripts/analysis/07_compare_priority_approaches.py` | `results/analysis/07_priority_comparison/summary_statistics.json` | Exact match: average difference `-31.5833%`. |
| Submitted page 7 composite performance numbers, e.g. `17/24`, `15/24`, `10/16`, `11/16`, `19/26`, `17/26` | `scripts/analysis/04_test_optimized_threshold_composite.py` | `results/analysis/04_optimized_threshold_composite/combination_summary.csv`, `results/analysis/05_network_type_comparison/summary_across_network_types.csv` | These numbers match the submitted text. |
| Paper-faithful threshold method mentioned as an alternative script result set | `scripts/analysis/03_test_paper_composite.py` | `results/analysis/03_paper_composite/combination_summary.csv` | The submitted paper's main optimized-threshold claims do not come from this file set; they come from script 04. |

### Additional traceability notes

- The high/low performer analysis is driven from precomputed centrality tables under:
  - `results/fixed-merged-subarticles-edges/importance-merged-50-cutoff/...`
- The script `scripts/analysis/01_find_best_high_low.py` is parameterized by cutoff, and the repository also contains corresponding precomputed tables for:
  - `importance-merged-100-cutoff`
  - `importance-merged-150-cutoff`
- The composite scripts `03`, `04`, `06`, `07`, and `08` are currently wired to the `50-cutoff` result set.

## Key factual points from the scripts

### High- vs low-relevance definition used in the scripts

The active script logic defines the categories as follows:

- `high relevance` = ground-truth value `1`
- `low relevance` = ground-truth values `2` and `3`

In paper terms:

- `Importance`: `1` is high relevance; `2-3` are low relevance
- `Court Branch / doctypebranch`: `1` is high relevance (`Grand Chamber`); `2-3` are low relevance (`Chamber` / `Committee`)

This is the operative definition in `scripts/analysis/01_find_best_high_low.py`.

### Composite results actually used by the submitted paper

The submitted paper's threshold table and composite performance claims trace to `scripts/analysis/04_test_optimized_threshold_composite.py`, not to the paper-faithful `03` results.

From `results/analysis/04_optimized_threshold_composite/combination_summary.csv`:

- `PageRank+Degree`: thresholds `0.65` (`importance`) and `0.70` (`doctypebranch`)
- `Degree+Eigenvector`: thresholds `0.30` and `0.35`
- `Degree+InDegree`: thresholds `0.35` and `0.35`

From `results/analysis/05_network_type_comparison/summary_across_network_types.csv`:

- `Degree+Eigenvector` wins `45/66` networks for `importance` and `43/66` for `doctypebranch`
- `Degree+InDegree` wins `45/66` networks for both `importance` and `doctypebranch`
- `PageRank+Degree` is clearly weaker overall (`36/66` and `35/66`)

### Low-Relevance Priority result actually used by the submitted paper

From `results/analysis/07_priority_comparison/summary_statistics.json`:

- `high_rel_better = 17`
- `low_rel_better = 1`
- `ties = 0`
- `avg_difference = -31.583333333333332`

This supports the submitted statement that Low-Relevance Priority underperformed on average by roughly `-31.6%`.

## Rebuttal Draft

## Reviewer 1

### Comment

The balancing strategy and threshold optimization introduce some methodological arbitrariness.

### Response

We agree that the balancing and thresholding choices are modeling choices, and we will make that clearer in the revision. Our aim is not to claim that there is a uniquely correct balancing strategy or a uniquely correct threshold. Rather, the contribution is to show that conclusions about centrality performance are sensitive to class imbalance and to whether one evaluates the high-relevance or low-relevance end of the distribution separately.

To make this more explicit, we will revise the methods and limitations sections to state that:

- balancing is used as an evaluation device to test how class imbalance affects which centrality measures appear strongest;
- the threshold parameter in the composite ranking is selected by grid search over `tau in [0.05, 0.95]` in steps of `0.05`;
- the optimized threshold should be interpreted as an empirically selected ranking parameter, not as a claim that one universal threshold is theoretically mandated.

This clarification is consistent with the active analysis pipeline. The submitted threshold table traces directly to `scripts/analysis/04_test_optimized_threshold_composite.py` and `results/analysis/04_optimized_threshold_composite/combination_summary.csv`.

### Comment

The supplementary material should have been made available to reviewers, since there are many ways to do this anonymously.

### Response

We agree. The supplementary material should have been available during review. We will provide an anonymized supplement containing the scripts and generated result files used for the submitted paper, including:

- `scripts/analysis/01_find_best_high_low.py`
- `scripts/analysis/04_test_optimized_threshold_composite.py`
- `scripts/analysis/06_test_low_relevance_priority.py`
- `scripts/analysis/07_compare_priority_approaches.py`
- `scripts/analysis/08_visualize_balanced_overlay.py`
- `results/analysis/01_high_low_performers/`
- `results/analysis/04_optimized_threshold_composite/`
- `results/analysis/07_priority_comparison/`
- `results/analysis/08_balanced_overlay_visualizations/`

The repository can be shared in anonymized form for inspection.

### Comment

The paper is generally clear, well motivated, and easy to follow, though some parts could be tightened and the practical implications of the work could be discussed more directly.

### Response

We appreciate this comment and agree that the paper can state the practical implications more directly. In the revision, we will tighten the discussion and conclusion to emphasize the main actionable takeaway:

- when the data are highly imbalanced, the apparent "best" centrality measure can change once the imbalance is addressed;
- no single individual centrality dominates all settings;
- composite ranking strategies that combine complementary signals can outperform any single metric across a much larger number of subnetworks.

This is supported by the script outputs used in the submitted paper. In particular, the optimized-threshold results in `results/analysis/05_network_type_comparison/summary_across_network_types.csv` show that `Degree+Eigenvector` and `Degree+InDegree` each win `45/66` subnetworks for at least one ground truth, which is substantially stronger than any single metric.

## Reviewer 2

### Comment

The main limitation as clearly acknowledged in the end of the paper is that the proposed composite measure is computed based on a threshold derived from the distribution in the ground truths therefore it is not a proper centrality measure computable from the citation network alone. This limits the practical significance of the study.

### Response

We agree with this limitation and will make it more explicit. We will revise the paper to clarify that the composite should be understood as an evaluation-driven ranking strategy rather than as a pure standalone centrality measure computable from citation structure alone.

At the same time, we would like to clarify what the empirical contribution is. The main contribution is not only the proposal of a composite ranking, but also the demonstration that:

- class imbalance materially affects conclusions about which centrality measures appear strongest;
- performance differs between the high-relevance and low-relevance ends of the distribution;
- combining complementary signals improves ranking performance substantially.

The submitted paper's optimized-threshold results are grounded in `scripts/analysis/04_test_optimized_threshold_composite.py` and saved in `results/analysis/04_optimized_threshold_composite/combination_summary.csv`. These outputs show that the composite combinations outperform individual measures across a much larger number of subnetworks than any single centrality alone.

We will also strengthen the future-work discussion by explicitly stating that estimating such thresholds from network structure alone is an important next step.

### Comment

Please check the text at the end of page 6: "Figure 3 shows similar patterns for the balanced and unbalanced datasets ..."

### Response

We agree that this sentence should be revised. Figure 3 is generated from the high/low performer analysis in `scripts/analysis/01_find_best_high_low.py`, with exported outputs in `results/analysis/01_high_low_performers/*.png`. The current sentence is too compressed and does not clearly explain what the figure encodes.

In the revision, we will:

- explicitly define what "high relevance" and "low relevance" mean;
- clarify that Figure 3 reports frequency counts over subnetworks, with separate bars for the two ground truths within each dataset variant;
- remove the current compressed phrasing based on "2 out of 3", which is not the clearest or most robust description of the figure.

In other words, we agree with the reviewer that the current wording is not sufficiently precise, and we will rewrite it to describe the figure more transparently.

### Comment

If Degree centrality has among the highest counts for both low-relevance judgments and high-relevance judgments as stated above, wouldn't it vanish the need for a composite measure?

### Response

No. Degree is indeed one of the most consistently strong individual measures, and we will clarify that in the revision. However, Degree appearing frequently does not eliminate the need for a composite, because it is not uniformly best across all network types and both ground truths.

This is precisely what the composite evaluation shows. The optimized-threshold results used in the submitted paper indicate:

- `Degree+Eigenvector` wins `45/66` subnetworks for `importance` and `43/66` for `doctypebranch`;
- `Degree+InDegree` wins `45/66` subnetworks for both ground truths;
- `PageRank+Degree` is weaker overall but still competitive in some settings.

These values come directly from `results/analysis/05_network_type_comparison/summary_across_network_types.csv`.

We will therefore revise the text to make the distinction clearer:

- Degree is a strong backbone measure;
- but composite rankings improve performance by incorporating complementary information captured by other measures such as Eigenvector or In-Degree.

### Comment

Since the distinction between high- and low-relevance judgments is central to the paper's contribution, the authors should explicitly define how each category maps onto the ground truth values.

### Response

We agree and will add an explicit definition in the methods section.

The active script logic uses:

- `high relevance = value 1`
- `low relevance = values 2 and 3`

Operationally, this means:

- `Importance`: high relevance = `1`; low relevance = `2-3`
- `Court Branch / doctypebranch`: high relevance = `Grand Chamber (1)`; low relevance = `Chamber / Committee (2-3)`

This is the operative definition in `scripts/analysis/01_find_best_high_low.py`, which is the source of the Figure 3 high/low performer analysis. We agree that this should be stated explicitly in the paper rather than left implicit.

### Comment

Wrong caption in Figure 2: "Bars with two shades of green ..." is for Figure 3.

### Response

Thank you. We agree and will correct the caption/reference in the revised manuscript.

## Reviewer 3

### Comment

There are several similar articles that were not mentioned, and it is not clear how this paper differs from and advances the field in relation to these other works.

### Response

We agree that the paper needs to position its contribution more sharply relative to prior legal citation-network work. We will revise the introduction and related-work sections to make the contribution explicit.

The paper's contribution is not simply another comparison of centrality measures. Rather, it makes three more specific contributions:

1. It shows that class imbalance materially changes which centrality measures appear strongest when evaluated against legal ground truths.
2. It evaluates performance separately at the high-relevance and low-relevance ends of the distribution, instead of relying only on a single overall correlation.
3. It tests composite ranking strategies built from complementary high- and low-relevance signals and shows that these outperform individual measures across many more subnetworks.

These contributions are directly reflected in the repository's active analysis pipeline:

- high/low separation: `scripts/analysis/01_find_best_high_low.py`
- optimized composite evaluation: `scripts/analysis/04_test_optimized_threshold_composite.py`
- alternative priority comparison: `scripts/analysis/06_test_low_relevance_priority.py` and `scripts/analysis/07_compare_priority_approaches.py`

We will also expand the related-work section to discuss more explicitly how this paper differs from prior centrality-comparison studies in legal citation networks.

### Comment

It may be worthwhile to apply these techniques to a new dataset and provide better insight into how these dynamics work.

### Response

We agree. Applying the framework to additional jurisdictions and citation networks is an important next step and would help assess external validity.

In the current paper, our claims are intended to be empirical and domain-specific to the ECtHR setting. We will revise the discussion to make that scope clearer and to identify cross-jurisdiction validation as a key direction for future work.

## Suggested manuscript revisions based on the reviews

The following changes are the most important ones to make before finalizing the rebuttal and revision:

1. Add an explicit high-relevance / low-relevance definition in the methods section.
2. Rewrite the page 6 Figure 3 discussion so that it describes the figure directly and does not rely on the current compressed phrasing.
3. Correct the Figure 2 caption issue.
4. Tighten the contribution statement in the introduction, related work, and conclusion.
5. State more explicitly that the composite is a ranking strategy requiring empirically selected thresholds, not a pure standalone centrality measure.
6. Provide anonymized supplementary materials containing the scripts and result files actually used in the submitted paper.

## Short version for the rebuttal cover note

We thank the reviewers for their constructive comments. The main changes we will make in revision are:

- clarify the paper's contribution relative to prior centrality-comparison work;
- explicitly define the high-relevance and low-relevance categories used throughout the analysis;
- revise the Figure 3 discussion and correct the Figure 2 caption issue;
- state more clearly that the composite is an empirically optimized ranking strategy rather than a standalone centrality measure;
- provide anonymized supplementary materials containing the scripts and generated result files underlying the submitted paper.
