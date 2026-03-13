# Scripts

This directory contains the active, script-based implementation of the project.
The scripts are organized by their role in the reproducibility story rather than
by notebook history.

## Layout

- `scripts/load/`
  - Entry points that begin from `data/METADATA/echr_metadata.csv`.
  - These scripts clean metadata, derive node/edge tables, and record explicit
    citation extraction outputs under `results/load/`.
- `scripts/generate/`
  - Entry points that rebuild intermediate and supporting artifacts needed by
    the study.
  - This includes the active `merged-article-edges` network family, the
    network statistics table, the centrality result bundles, and the
    correlation matrix figure.
- `scripts/analysis/`
  - Entry points for the paper-facing analyses.
  - These scripts consume the centrality-enriched `total_df.csv` tables and
    write the performer summaries, composite-threshold evaluations, priority
    comparisons, and overlay figures cited in the paper.
- `scripts/shared/`
  - Shared Python modules used by the script entry points.
  - This code is intentionally thin and exists to avoid duplicating network
    loading, centrality, partitioning, statistics, and output-format logic.

## How The Script Families Fit Together

The scripts support two related goals:

1. Reconstruct how the centrality-ready data products were built.
2. Regenerate the analyses and figures that support the paper text.

In practice:

1. `scripts/load/` starts from the canonical metadata export.
2. `scripts/generate/` turns that material into network inputs and supporting
   outputs.
3. `scripts/analysis/` turns the centrality tables into the paper-facing
   claims.

## Recommended Execution Order

Rebuild metadata-derived artifacts when needed:

```bash
venv/bin/python scripts/load/process_metadata.py
venv/bin/python scripts/load/extract_edges.py
```

Rebuild the active network family and supporting artifacts:

```bash
venv/bin/python scripts/generate/00_generate_merged_article_edge_networks.py
venv/bin/python scripts/generate/01_generate_network_statistics.py
venv/bin/python scripts/generate/02_build_centrality_results.py \
  --network-dir networks/merged-article-edges/split-unbalanced \
  --output-dir results/rebuilt/split-unbalanced \
  --min-nodes 50
venv/bin/python scripts/generate/03_generate_correlation_matrix.py \
  --input results/fixed-merged-subarticles-edges/importance-merged/unbalanced/total_df.csv \
  --output results/analysis/00_supporting_figures/correlation_matrix.png
```

Run the paper-facing analyses:

```bash
venv/bin/python scripts/analysis/01_find_best_high_low.py
venv/bin/python scripts/analysis/03_test_paper_composite.py
venv/bin/python scripts/analysis/04_test_optimized_threshold_composite.py
venv/bin/python scripts/analysis/05_compare_across_network_types.py
venv/bin/python scripts/analysis/06_test_low_relevance_priority.py
venv/bin/python scripts/analysis/07_compare_priority_approaches.py
venv/bin/python scripts/analysis/08_visualize_balanced_overlay.py
```

## Active Vs Archived

- Active source-of-truth code lives under `scripts/`.
- Notebook-era implementations now live under `archive/notebooks/`.
- Superseded standalone scripts live under `archive/old_scripts/`.
- Historical load-stage diagnostics live under `archive/load/`.

See the per-directory READMEs for script-level details.
