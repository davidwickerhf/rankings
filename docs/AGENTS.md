# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a research project analyzing citation networks from the European Court of Human Rights (ECHR). It calculates and compares various centrality measures (degree, betweenness, closeness, PageRank, disruption, etc.) against ground truth metrics (case importance and document type) to identify which centrality measures best predict case significance.

## Environment Setup

### Virtual Environment
The project uses a Python virtual environment at `venv/`:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Dependencies Installation
```bash
pip install -r requirements.txt
```

Key dependencies include:
- `networkx`: Network analysis and centrality calculations
- `pandas`, `numpy`: Data manipulation
- `matplotlib`, `seaborn`: Visualization
- `scipy`: Statistical analysis (Spearman correlations)
- `echr_extractor`: Custom ECHR data extraction library
- `jupyter`: Running analysis notebooks

## Data Pipeline

### 1. Load ECHR Metadata
Extract nodes and edges from ECHR metadata CSV:
```bash
python load/load.py --input_path data/METADATA/echr_metadata.csv --save_path data/ECHR --metadata
```

This creates `nodes.json` and `edges.json` in the specified save path.

### 2. Process Data
Convert CSV metadata to JSON format with proper edge list structure:
```bash
python load/process.py
```

Input: `data/METADATA/echr_metadata.csv`  
Output: `data/METADATA/nodes.json`, `data/METADATA/edges.json`

### 3. Generate Edges
The `load/edges.py` module extracts citation relationships:
- Parses case references from the `scl` column
- Matches references using application numbers and case names
- Handles missing references and tracks unmatched citations
- Uses parallel processing for large datasets

### 4. Launch Analysis
Start Jupyter Notebook to run analysis:
```bash
jupyter notebook
```

Open `rankings.ipynb` for centrality analysis or `comparison.ipynb` for network comparisons.

## Core Architecture

### Data Structure
- **Nodes**: Cases with metadata (ECLI, importance, doctypebranch, dates)
- **Edges**: Citation relationships between cases (directed graph)
- **Networks**: Organized in `networks/` directory by filtering criteria

### Ground Truth Metrics
The analysis evaluates centrality measures against two ground truths:

**Importance Scores** (1-4):
- 1 = Highest significance (e.g., landmark judgments)
- 2 = High significance
- 3 = Medium significance
- 4 = Low significance (e.g., inadmissibility decisions)

**Doctypebranch** (1-3):
- 1 = GRANDCHAMBER (most significant)
- 2 = CHAMBER
- 3 = COMMITTEE (least significant)

### Centrality Measures
The following centrality measures are calculated and compared:
- `in_degree_centrality`: Number of incoming citations (normalized)
- `out_degree_centrality`: Number of outgoing citations (normalized)
- `degree_centrality`: Total degree (normalized)
- `betweenness_centrality`: Bridge between other nodes
- `closeness_centrality`: Average distance to all other nodes
- `harmonic_centrality`: Harmonic mean of distances
- `eigenvector_centrality`: Influence based on neighbors' importance
- `pagerank`: Google PageRank algorithm
- `hits_authority`: HITS authority score
- `hits_hub`: HITS hub score
- `core_number`: K-core decomposition
- `disruption`: Disruptiveness index (see DISRUPTION.md)
- `relative_in_degree_centrality`: Custom normalized in-degree

### Composite Rankings
Two methods combine centrality measures (see COMPOSITE.md):

**Weighted Geometric Mean**:
- Combines high-importance and low-importance predictors
- Optimizes weight parameter to maximize correlation with ground truth
- Formula: `composite = high^w * low^(1-w)`

**Threshold Combination**:
- Uses high-importance measure above a percentile threshold
- Falls back to low-importance measure below threshold
- Optimizes threshold parameter

### Analysis Functions

**`analyze_network(nodes_path, edges_path, ground_truths)`**:
- Loads network from JSON files
- Calculates all centrality measures
- Finds best predictors for high/low importance
- Creates composite rankings
- Returns `AnalysisResults` TypedDict with:
  - `network_stats`: Basic network metrics (nodes, edges, density)
  - `correlations`: Spearman correlations between centralities and ground truths
  - `best_centralities`: Best predictors for high/low values
  - `composite_rankings`: Composite ranking scores
  - `dataframe`: Complete DataFrame with all measures

**`compare_networks(network_results)`**:
- Compares results across multiple networks
- Analyzes correlation patterns
- Evaluates ranking consistency
- Identifies which centralities perform best across datasets

## Key Implementation Details

### Disruption Index
The disruption measure has unique properties (see DISRUPTION.md):
- Shows **positive correlations** with ground truths (unlike other centralities)
- More effective in **sparse networks** vs. dense networks
- In selection logic, positive correlations are minimized using `1 - correlation`
- Performance degrades as edge density increases due to reduced variability

### Data Preprocessing
The `prep_data()` function:
- Filters out rows with uncomputed metric values (< -1)
- Converts doctypebranch strings to numeric values
- Selects required columns for analysis

### Normalization
The `normalize_centrality()` function:
- Uses percentile ranking (0-1 scale)
- Scales to 1-1000 range (lower = more important)
- Handles zero values by assigning lowest importance (1000)
- Preserves order while ensuring fair comparison

## Missing References Analysis

The `load/edges.ipynb` notebook analyzes missing case references:
- 207,038 total missing references from 18,131 source documents
- Types: Application numbers (130k), case names (40k), SCL numbers (36k)
- Output: `data/METADATA/missing_cases.csv`

## Testing & Validation

**No formal test suite exists.** To validate changes:
1. Run the data pipeline (load.py → process.py)
2. Execute `rankings.ipynb` cells sequentially
3. Check that centrality calculations produce valid ranges:
   - Most measures in [0, 1]
   - Disruption in [-1, 1]
   - Core number in [0, max_k]
4. Verify Spearman correlations are computed without NaN values
5. Ensure composite rankings have variance (not all identical values)

## File Organization

**Analysis Notebooks**:
- `rankings.ipynb`: Main centrality analysis and comparison
- `comparison.ipynb`: Multi-network comparison
- `metadata.ipynb`: Metadata exploration
- `load/edges.ipynb`: Edge extraction and missing reference analysis
- `load/download.ipynb`: Data download scripts
- `load/process.ipynb`: Data processing exploration

**Documentation**:
- `COMPOSITE.md`: Mathematical foundations of composite ranking methods
- `DISRUPTION.md`: Analysis of disruption measure behavior
- `STATISTICAL-ANALYSIS.md`: Statistical significance of centrality trends

**Data Processing Scripts**:
- `load/load.py`: Extract nodes/edges from metadata CSV
- `load/edges.py`: Parse citation references (parallel processing)
- `load/process.py`: Convert CSV to JSON format

**Results**:
- `results/`: Output directory for analysis results
- `network_statistics_updated.csv`: Network statistics across datasets
- `correlation_matrix.png`: Visualization of correlations

## Important Considerations

### Disruption Measure Behavior
When working with the disruption centrality:
- It correlates **positively** with importance scores (opposite of other measures)
- Its effectiveness depends on network density
- Selection logic treats it differently: `1 - correlation` vs. `1 + correlation`
- Consider edge density when interpreting results

### Data Quality
- Some cases have missing ECLI identifiers (dropped during preprocessing)
- Duplicate ECLIs exist in raw data (first occurrence kept)
- Not all references can be matched (tracked in missing_cases.csv)
- Rows with NaN doctypebranch are filtered out

### Performance
- Large datasets benefit from parallel processing in `edges.py`
- Centrality calculations can be slow for dense networks (>100k edges)
- LRU caching is used for repeated lookups in edge extraction

## Version Control

When committing changes, include co-author line:
```
Co-Authored-By: Warp <agent@warp.dev>
```
