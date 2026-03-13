# Archive

This directory contains material kept for traceability but excluded from the
active reproducibility path.

## Contents

- `notebooks/`
  - Legacy notebooks preserved so the notebook-era workflow can still be
    inspected.
- `old_scripts/`
  - Superseded standalone scripts that are not part of the maintained
    script-first workflow.
- `old_results/`
  - Historical summaries retained for comparison.
- `data/`
  - Raw exports, intermediate CSVs, and one-off data byproducts removed from
    the active data contract.
- `networks/`
  - Older network families superseded by `networks/merged-article-edges/`.
- `results/`
  - Result families that are no longer part of the paper-traceable path.
- `docs/`
  - Older repository summaries and notes that were consolidated elsewhere.
- `load/`
  - Legacy load-stage scripts and diagnostics that were superseded by
    `scripts/load/`.

## Source-Of-Truth Boundary

For supplementary-material reproduction, use:

- `scripts/load/` for metadata ingestion and citation extraction
- `scripts/generate/` for network construction and supporting artifacts
- `scripts/analysis/` for paper-facing analyses

Everything under `archive/` should be treated as historical context only.
