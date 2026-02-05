# Repository Organization Summary

## What Was Done

### 1. File Organization

**Archived** (moved to `archive/`):
- All `PAPER_*.md` files (old methodology documentation)
- `*_RESULTS.md` and `*_SUMMARY.md` files (interim analysis documents)
- `VERIFICATION_DATA_GUIDE.md`
- `PROPOSED_PAPER_METHODOLOGY.md`

**Organized into `scripts/`**:
- All `.py` analysis scripts
- Created comprehensive `scripts/README.md` with methodology documentation

**Organized into `docs/`**:
- `AGENTS.md` - Agent rules
- `COMPOSITE.md` - Composite methodology
- `DISRUPTION.md` - Disruption index docs
- `STATISTICAL-ANALYSIS.md` - Statistical methods

**Results Cleanup**:
- Archived old test results to `results/archive/`
- Kept only current results:
  - `fixed-merged-subarticles-edges/` - Main centrality calculations
  - `high_low_analysis_50_cutoff/` - High/low analysis
  - `high_low_analysis_with_aggregates/` - Aggregate analysis

### 2. Documentation Created

**Main README** (`README.md`):
- Clean repository structure overview
- Quick start guide
- Key results summary

**Scripts README** (`scripts/README.md`):
- Complete methodology documentation for all scripts
- Detailed selection logic explanation
- Usage examples
- Troubleshooting guide

## Current Structure

```
rankings/
├── README.md                          # Main documentation
├── rankings.ipynb                     # Jupyter notebook
├── scripts/                          # All analysis scripts
│   ├── README.md                     # Detailed script documentation
│   ├── analyze_high_low_performers.py
│   ├── analyze_high_low_with_aggregates.py
│   ├── test_combinations_with_verification.py
│   ├── test_global_vs_local_weight.py
│   └── [legacy scripts...]
├── docs/                             # Documentation
│   ├── AGENTS.md
│   ├── COMPOSITE.md
│   ├── DISRUPTION.md
│   └── STATISTICAL-ANALYSIS.md
├── results/                          # Analysis results
│   ├── fixed-merged-subarticles-edges/
│   │   ├── importance-merged-50-cutoff/
│   │   └── verification_test/
│   ├── high_low_analysis_50_cutoff/
│   ├── high_low_analysis_with_aggregates/
│   └── archive/                      # Old results
├── networks/                         # Network data (DO NOT TOUCH)
│   └── merged-article-edges/
├── archive/                          # Archived documentation
│   └── [old .md files]
└── README.old.md                     # Original README backup
```

## Protected Directories (DO NOT MODIFY)

These contain original data and should never be changed:
- `networks/merged-article-edges/`
- `results/merged-subarticles-edges/`
- `results/pre/`

## Key Scripts

### Primary Analysis
1. **`analyze_high_low_performers.py`** - Per-network high/low analysis
2. **`analyze_high_low_with_aggregates.py`** - Includes aggregate mega-networks
3. **`test_combinations_with_verification.py`** - Test 3 combinations with verification

### Validation
4. **`test_global_vs_local_weight.py`** - Validate optimization claim

### Legacy (kept for reference)
- `test_centrality_combinations*.py`
- `test_new_combinations.py`
- `compare_selection_methods.py`

## Quick Reference

### Run All Analyses
```bash
cd /Users/davidwickerhf/Projects/work/maastricht/rankings

python scripts/analyze_high_low_performers.py
python scripts/analyze_high_low_with_aggregates.py
python scripts/test_combinations_with_verification.py
python scripts/test_global_vs_local_weight.py
```

### View Results
- **Verification data**: `results/fixed-merged-subarticles-edges/verification_test/`
- **High/low analysis**: `results/high_low_analysis_50_cutoff/`
- **Aggregate analysis**: `results/high_low_analysis_with_aggregates/`

### Documentation
- **Script docs**: `scripts/README.md`
- **Main docs**: `README.md`
- **Methodology**: `docs/`

## Next Steps for Paper

Based on current analysis, the most methodologically sound approach is:

### Option A: Use Data-Driven Combinations
Test the combinations that **actually appear** in the analysis:
1. Degree + Disruption (appears 25 times)
2. Degree + HitsHub (appears 21 times)
3. Relative-InDegree + HitsHub (appears 11 times)

**Justification**: "We tested the three most frequent combinations identified through systematic analysis of individual and aggregate networks."

### Option B: Keep Current Combinations with Different Justification
Keep testing Degree+Eigenvector, Degree+PageRank, Degree+InDegree but justify differently:

**Justification**: "We selected three combinations representing diverse theoretical approaches: Eigenvector (network position), PageRank (iterative importance), and In-Degree (citation count), all paired with Degree centrality which emerged as a frequent high performer."

**Recommendation**: Option A is more honest and methodologically sound. Option B requires acknowledging the combinations were theoretically motivated rather than empirically selected.

## Clean Repository Achieved ✅

- All scripts properly organized and documented
- Results standardized with clear output formatting  
- Legacy files archived
- Protected directories clearly marked
- Comprehensive documentation in place
