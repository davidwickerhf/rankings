# Networks Directory

This directory contains the active network inputs consumed by the reproducible
centrality workflow.

## Active Network Family

- `merged-article-edges/`
  - Article-level subnetworks built from the merged-importance representation
    and explicit citation edges.
  - This is the network family used to generate the centrality-ready result
    bundles that feed the paper-facing analyses.

Generation entry point:

```bash
venv/bin/python scripts/generate/00_generate_merged_article_edge_networks.py
```

## Per-Network Structure

Each network directory contains:

- `nodes.json`
  - Case metadata keyed by ECLI, including the ground-truth fields used by the
    downstream analyses.
- `edges.json`
  - Directed citation links among the cases in that network.

Representative centrality-build command:

```bash
venv/bin/python scripts/generate/02_build_centrality_results.py \
  --network-dir networks/merged-article-edges/split-unbalanced \
  --output-dir results/rebuilt/split-unbalanced
```

## Notes

- The balanced and unbalanced variants under `merged-article-edges/` are fixed
  inputs to the centrality calculations.
- Older network families have been moved to `archive/networks/`.
- The original notebook provenance for this active family is preserved in
  `archive/notebooks/load/process.ipynb`, but the script above is now the
  maintained entry point.
