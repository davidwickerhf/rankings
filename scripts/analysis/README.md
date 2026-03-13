# Analysis Scripts

This directory contains the paper-facing analysis scripts. They operate on the
centrality-enriched `total_df.csv` tables and produce the outputs that support
the manuscript’s main empirical claims.

## Inputs

These scripts consume the fixed centrality bundles retained under:

- `results/fixed-merged-subarticles-edges/`

In other words, this directory is where the paper arguments are reproduced once
the `total_df.csv` tables already exist.

## Script Map

- `01_find_best_high_low.py`
  - Counts which individual centrality measures perform best for the
    high-relevance end and the low-relevance end of the distribution across the
    article-level subnetworks.
  - Use this to support the paper’s claim that the best individual metric
    depends on which end of relevance is being prioritized.
  - Output: `results/analysis/01_high_low_performers/`
- `03_test_paper_composite.py`
  - Recreates the manuscript’s paper-faithful thresholding approach, where the
    threshold is derived from the observed proportion of high-relevance cases in
    each network.
  - Output: `results/analysis/03_paper_composite/`
- `04_test_optimized_threshold_composite.py`
  - Searches for a universal threshold for each composite/ground-truth pairing
    and evaluates those thresholds across the network collection.
  - Use this to support the stronger composite-performance claims in the paper.
  - Output: `results/analysis/04_optimized_threshold_composite/`
- `05_compare_across_network_types.py`
  - Summarizes the optimized-threshold results across unbalanced,
    balanced-importance, and balanced-doctypebranch network variants.
  - Output: `results/analysis/05_network_type_comparison/`
- `06_test_low_relevance_priority.py`
  - Evaluates the alternative ranking strategy that prioritizes low-relevance
    judgments first.
  - Output: `results/analysis/06_low_relevance_priority/`
- `07_compare_priority_approaches.py`
  - Compares the default high-relevance-priority strategy against the
    low-relevance-priority alternative.
  - Use this to support the conclusion that low-relevance priority is usually
    worse.
  - Output: `results/analysis/07_priority_comparison/`
- `08_visualize_balanced_overlay.py`
  - Produces the overlay visualizations that compare centrality behavior across
    balanced network variants.
  - Output: `results/analysis/08_balanced_overlay_visualizations/`

## Execution Order

```bash
venv/bin/python scripts/analysis/01_find_best_high_low.py
venv/bin/python scripts/analysis/03_test_paper_composite.py
venv/bin/python scripts/analysis/04_test_optimized_threshold_composite.py
venv/bin/python scripts/analysis/05_compare_across_network_types.py
venv/bin/python scripts/analysis/06_test_low_relevance_priority.py
venv/bin/python scripts/analysis/07_compare_priority_approaches.py
venv/bin/python scripts/analysis/08_visualize_balanced_overlay.py
```

## Relationship To The Rest Of The Repo

- `scripts/load/` explains how metadata and citation edges are derived.
- `scripts/generate/` explains how network and centrality-supporting outputs are
  built.
- This directory explains how those centrality bundles are turned into the
  actual paper-facing results.

## Archived Analysis Code

The weighted-geometric composite experiment formerly tracked in
`02_test_composite_measures.py` has been moved to `archive/old_scripts/` because
it is not part of the active paper-traceable execution path.
