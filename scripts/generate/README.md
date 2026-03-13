# Generate Scripts

These scripts produce the intermediate and supporting artifacts that connect the
metadata-derived network inputs to the paper-facing analyses. They are not the
final comparative analyses themselves; they create the network families, tables,
and figures that those analyses depend on.

## Scripts

- `00_generate_merged_article_edge_networks.py`
  - Rebuilds `networks/merged-article-edges/`.
  - This script is the script-based replacement for the network-separation
    notebook logic used to create the active article-level subnetworks and
    their balanced variants.
- `01_generate_network_statistics.py`
  - Writes `results/analysis/00_supporting_tables/network_statistics_updated.csv`.
  - This produces the descriptive table of network sizes and structures used as
    supporting context in the manuscript.
- `02_build_centrality_results.py`
  - Builds the per-network centrality bundles, including `total_df.csv`,
    `analysis_results.json`, and supporting plots.
  - This is the main script that reconstructs the centrality-ready tables later
    consumed by the paper-facing analyses.
- `03_generate_correlation_matrix.py`
  - Writes `results/analysis/00_supporting_figures/correlation_matrix.png`.
  - This captures the overall relationships among the centrality measures in a
    representative `total_df.csv`.

## Typical Usage

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

## Notes

- The active paper analyses do not run directly from these scripts. They run
  from the centrality-enriched `total_df.csv` bundles created here or preserved
  under `results/fixed-merged-subarticles-edges/`.
- Notebook-era versions of this logic are preserved under `archive/notebooks/`.
