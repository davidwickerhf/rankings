# ECtHR Citation Network Rankings Analysis

This repository is the reproducibility package for the ECtHR citation-network
paper. The active source of truth is the script-based workflow under
`scripts/`. Notebook-era experiments, alternative data exports, deprecated
network families, and superseded results have been moved to `archive/`.

## What This Repository Contains

The repository is organized around the path from source metadata to the paper:

```text
rankings/
├── data/        # Canonical in-repo source data
├── scripts/     # Active executable code
├── networks/    # Active paper-used network family
├── results/     # Fixed centrality bundles and paper-facing outputs
├── docs/        # Manuscript, traceability, reproduction, reflections
└── archive/     # Historical material kept for traceability
```

## Source Of Truth

The active reproducibility path is:

1. `data/METADATA/echr_metadata.csv`
   - Canonical metadata export retained in-repo.
2. `scripts/load/`
   - Processes metadata and extracts citation edges into `results/load/`.
3. `scripts/generate/`
   - Rebuilds `networks/merged-article-edges/`, supporting tables, supporting
     figures, and the per-network centrality bundles.
4. `scripts/analysis/`
   - Produces the paper-facing comparisons, threshold analyses, and figures
     from the centrality-enriched `total_df.csv` tables.

## Main Locations

- `data/METADATA/echr_metadata.csv`
  - Source metadata used to derive citation edges and network partitions.
- `networks/merged-article-edges/`
  - Active network family used to generate the centrality results.
- `results/fixed-merged-subarticles-edges/`
  - Fixed centrality-enriched `total_df.csv` bundles used by the paper-facing
    analysis scripts.
- `results/analysis/`
  - Analysis outputs that support the manuscript claims.
- `results/analysis/00_supporting_tables/network_statistics_updated.csv`
  - Supporting network statistics table.
- `results/analysis/00_supporting_figures/correlation_matrix.png`
  - Supporting correlation matrix figure.
- `docs/paper/paper.tex`
  - Manuscript source.
- `docs/TRACEABILITY.md`
  - Maps paper figures, tables, and claims to scripts and generated files.
- `docs/REPRODUCE.md`
  - Submission-facing reproduction guide.
- `docs/REFLECTIONS.md`
  - Consolidated notes on methodological choices and abandoned directions.

## Active Script Families

- `scripts/load/`
  - Prepares metadata-derived node/edge outputs from the canonical CSV.
- `scripts/generate/`
  - Recreates the active network family and non-paper-facing supporting
    artifacts such as the correlation matrix and statistics table.
- `scripts/analysis/`
  - Generates the paper-facing outputs, including the high/low performer
    counts, composite-threshold comparisons, priority comparisons, and overlay
    figures.

## Quick Start

Activate the environment:

```bash
source venv/bin/activate
```

Run the load-stage scripts if you need to rebuild metadata-derived artifacts:

```bash
venv/bin/python scripts/load/process_metadata.py
venv/bin/python scripts/load/extract_edges.py
```

Run the generation scripts to rebuild supporting artifacts:

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

## Documentation

- `docs/README.md` indexes the active supplementary-facing documents.
- `docs/TRACEABILITY.md` maps paper claims to scripts and outputs.
- `docs/REPRODUCE.md` describes the supported rerun modes and `Makefile`
  targets.
- `scripts/README.md` explains how the active script families fit together.
- `scripts/load/README.md`, `scripts/generate/README.md`, and
  `scripts/analysis/README.md` describe each script and its outputs.
- `results/README.md` describes the active result roots and what they contain.
- `archive/README.md` documents the boundary between active and historical
  material.
