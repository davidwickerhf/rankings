# AGENTS.md

This file provides guidance to repository agents working on this project.

## Project Overview

This repository analyzes ECtHR citation networks to evaluate how well centrality
measures align with legal relevance proxies such as `importance` and
`doctypebranch`.

## Environment

Use the project virtual environment:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Active Pipeline

The repository is script-first. The active execution path is:

1. `scripts/load/`
   - Input: `data/METADATA/echr_metadata.csv`
   - Output: derived load artifacts under `results/load/`
2. `scripts/generate/00_generate_merged_article_edge_networks.py`
   - Rebuilds the active `networks/merged-article-edges/` family from processed
     nodes/edges tables
3. `scripts/generate/01_generate_network_statistics.py`, `scripts/generate/02_build_centrality_results.py`, and `scripts/generate/03_generate_correlation_matrix.py`
   - Builds `total_df.csv`, per-network plots, `analysis_results.json`,
      `results/analysis/00_supporting_tables/network_statistics_updated.csv`, and
      `results/analysis/00_supporting_figures/correlation_matrix.png`
4. `scripts/analysis/`
   - Produces the paper-facing summaries, composite comparisons, and figures

Representative commands:

```bash
venv/bin/python scripts/load/process_metadata.py
venv/bin/python scripts/load/extract_edges.py
venv/bin/python scripts/generate/00_generate_merged_article_edge_networks.py
venv/bin/python scripts/generate/01_generate_network_statistics.py
venv/bin/python scripts/generate/02_build_centrality_results.py \
  --network-dir networks/merged-article-edges/split-unbalanced \
  --output-dir results/rebuilt/split-unbalanced \
  --min-nodes 50
venv/bin/python scripts/generate/03_generate_correlation_matrix.py
venv/bin/python scripts/analysis/04_test_optimized_threshold_composite.py
```

## Data Contract

- Canonical source data:
  - `data/METADATA/echr_metadata.csv`
- Fixed network inputs:
  - `networks/`
- Paper-facing results:
  - `results/fixed-merged-subarticles-edges/`
  - `results/analysis/`

Historical raw exports, intermediate CSVs, notebooks, and exploratory scripts
have been moved under `archive/`.

## Centrality Measures

The active pipeline works with:

- `degree_centrality`
- `in_degree_centrality`
- `out_degree_centrality`
- `relative_in_degree_centrality`
- `betweenness_centrality`
- `closeness_centrality`
- `harmonic_centrality`
- `eigenvector_centrality`
- `pagerank`
- `hits_hub`
- `hits_authority`
- `core_number`
- `disruption`

## Ground Truths

- `importance`
  - Lower score means higher relevance.
- `doctypebranch`
  - `1 = GRANDCHAMBER`, `2 = CHAMBER`, `3 = COMMITTEE`

The paper-facing analyses treat value `1` as high relevance and values `2-3` as
low relevance when splitting performance by end of the distribution.

## Validation

No formal automated test suite exists. Validate changes by:

1. Running the relevant `scripts/load/`, `scripts/generate/`, or
   `scripts/analysis/` entrypoints.
2. Checking that expected result files are produced in the documented output
   directories.
3. Verifying that centrality columns are populated and correlation outputs do
   not degenerate to all-NaN values.
