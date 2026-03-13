# Data Directory

This directory now contains only the canonical in-repo source data used by the
active reproducibility path.

## Source Of Truth

- `data/METADATA/echr_metadata.csv`
  - ECtHR metadata snapshot used to derive citation edges, construct the active
    network family, and ultimately generate the centrality tables consumed by
    the paper-facing scripts.

## How It Is Used

- `scripts/load/` starts from this file to produce metadata-derived node/edge
  outputs under `results/load/`.
- `scripts/generate/00_generate_merged_article_edge_networks.py` relies on the
  processed metadata representation to construct the active subnetwork family
  under `networks/merged-article-edges/`.
- Downstream centrality tables and paper analyses ultimately trace back to this
  metadata source.

## Boundary

- Derived load-stage outputs belong under `results/load/`.
- Active network inputs belong under `networks/`.
- Historical raw exports, intermediate tables, and one-off data products have
  been moved to `archive/data/`.
