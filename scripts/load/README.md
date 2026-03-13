# Load Scripts

This directory contains the active metadata-ingestion and citation-extraction
entry points. These scripts are the earliest stage of the reproducibility path:
they start from the canonical metadata export and produce the derived material
from which network inputs can be assembled.

## Canonical Input

- `data/METADATA/echr_metadata.csv`
  - The retained in-repo metadata snapshot for the ECtHR cases used by this
    project.

## Scripts

- `process_metadata.py`
  - Parses and reshapes the canonical metadata export into node/edge-oriented
    CSV and JSON outputs.
  - Use this when you want a metadata-derived graph representation of the full
    source dataset.
  - Default output: `results/load/metadata_graph/`
- `extract_edges.py`
  - Extracts citation references more explicitly, exports nodes/edges tables,
    and records unresolved references for inspection.
  - Use this when you want a traceable edge-construction output and missing
    citation diagnostics.
  - Default output: `results/load/edge_extraction/`

## Usage

```bash
venv/bin/python scripts/load/process_metadata.py
venv/bin/python scripts/load/extract_edges.py
```

## Notes

- These scripts document how the raw metadata can be turned into graph-shaped
  data products, even though the paper-facing analyses now run from fixed
  network and centrality bundles already retained in the repository.
- Older load-stage scripts, diagnostics, and exploratory outputs have been
  moved to `archive/load/`.
