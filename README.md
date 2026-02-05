# ECtHR Citation Network Rankings Analysis

Analysis of centrality measures in European Court of Human Rights (ECtHR) citation networks.

## Repository Structure

```
rankings/
├── scripts/              # Analysis scripts (documented in scripts/README.md)
├── docs/                 # Documentation  
├── results/             # Analysis results
│   ├── fixed-merged-subarticles-edges/    # Main centrality calculations
│   ├── high_low_analysis_50_cutoff/       # High/low performer analysis  
│   └── high_low_analysis_with_aggregates/ # Aggregate network analysis
├── networks/            # Network data (DO NOT MODIFY)
├── archive/             # Archived files
└── rankings.ipynb       # Main Jupyter notebook
```

## Quick Start

### Run Analysis

```bash
# Analyze high/low performers
python scripts/analyze_high_low_performers.py

# Test centrality combinations with verification
python scripts/test_combinations_with_verification.py

# Enhanced analysis with aggregates
python scripts/analyze_high_low_with_aggregates.py
```

### Key Results

**Location**: `results/fixed-merged-subarticles-edges/verification_test/`

**Best Combination**: Degree + Eigenvector (43.2% win rate, 57/132 networks)

## Documentation

- **`scripts/README.md`** - Complete script documentation
- **`docs/`** - Methodology documentation
- **`results/high_low_analysis_with_aggregates/combination_analysis.txt`** - Combination justification

## Data Directories (DO NOT MODIFY)

- `networks/merged-article-edges/` - Network data
- `results/merged-subarticles-edges/` - Legacy results
- `results/pre/` - Pre-processing results
