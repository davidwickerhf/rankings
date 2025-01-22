Here's a comprehensive README for the `/results` folder:

# Results Directory Documentation

## Directory Structure

```
/results
├── /pre                           # Pre-analysis results with separate importance levels
├── /importance-merged             # Full networks with merged importance levels 1-2
├── /importance-merged-50-cutoff   # Networks with min 50 nodes
├── /importance-merged-100-cutoff  # Networks with min 100 nodes
└── /importance-merged-150-cutoff  # Networks with min 150 nodes
```

## Overview

The results directory contains two main types of analyses:

1. Pre-analysis results with separate importance levels (in `/pre`)
2. Merged importance analysis with various node count cutoffs

For pre-analysis results documentation, see [Pre-Analysis README](pre/README.md).

## Merged Importance Analysis

### Network Types

Each cutoff directory contains three types of networks:

1. **Unbalanced Networks**

   - Original network structure
   - Natural distribution of document types and importance levels
   - No balancing applied

2. **Balanced by Importance**

   - Networks balanced to have even distribution of importance levels
   - Importance levels 1 and 2 merged into a single category
   - Categories: {1-2, 3, 4}

3. **Balanced by Doctype Branch**
   - Networks balanced to have even distribution of document types
   - Document types: GRANDCHAMBER, CHAMBER, COMMITTEE

### Cutoff Variations

The analysis was performed on networks of different sizes:

```3453:3461:rankings.ipynb
    "# Form networks with min 100 nodes\n",
    "importance_merged_100_cutoff_unbalanced = {name: data for name, data in split_unbalanced.items() if len(data['nodes']) >= 100}\n",
    "importance_merged_100_cutoff_balanced_importance = {name: data for name, data in split_balanced_importance.items() if len(data['nodes']) >= 100}\n",
    "importance_merged_100_cutoff_balanced_doctypebranch = {name: data for name, data in split_balanced_doctypebranch.items() if len(data['nodes']) >= 100}\n",
    "\n",
    "# Form networks with min 150 nodes\n",
    "importance_merged_150_cutoff_unbalanced = {name: data for name, data in split_unbalanced.items() if len(data['nodes']) >= 150}\n",
    "importance_merged_150_cutoff_balanced_importance = {name: data for name, data in split_balanced_importance.items() if len(data['nodes']) >= 150}\n",
    "importance_merged_150_cutoff_balanced_doctypebranch = {name: data for name, data in split_balanced_doctypebranch.items() if len(data['nodes']) >= 150}\n",
```

1. **Full Networks** (`/importance-merged`)

   - Complete networks without size restrictions
   - All cases included

2. **50+ Nodes** (`/importance-merged-50-cutoff`)

   - Networks with at least 50 nodes
   - Basic filtering for meaningful analysis

3. **100+ Nodes** (`/importance-merged-100-cutoff`)

   - Medium-sized networks
   - More robust statistical analysis

4. **150+ Nodes** (`/importance-merged-150-cutoff`)
   - Largest networks only
   - Most statistically significant results

### Analysis Results Structure

Each network type contains:

1. **Individual Network Analysis**

   - Separate folders for each article network
   - Centrality measures and rankings
   - Correlation analyses

2. **Comparisons Directory**
   - Cross-network analysis results
   - Performance metrics for centrality measures
   - Example structure:

```2:26:results/importance-merged-150-cutoff/balanced-doctypebranch/comparisons/network_analysis_doctypebranch.json
    "centrality_counts": {
        "high": {
            "disruption": 9,
            "eigenvector_centrality": 4,
            "out_degree_centrality": 2,
            "degree_centrality": 1,
            "pagerank": 1
        },
        "low": {
            "in_degree_centrality": 5,
            "closeness_centrality": 3,
            "disruption": 2,
            "pagerank": 3,
            "harmonic_centrality": 2,
            "core_number": 1,
            "eigenvector_centrality": 1
        },
        "best_overall": {
            "disruption": 9,
            "eigenvector_centrality": 4,
            "out_degree_centrality": 2,
            "degree_centrality": 1,
            "pagerank": 1
        }
    },
```

3. **Composite Rankings**
   Best performing combinations:

```38:64:results/importance-merged-150-cutoff/balanced-doctypebranch/comparisons/network_analysis_doctypebranch.json
        "outperformed_count": 4,
        "best_combinations": [
            {
                "combination": "disruption_pagerank",
                "correlation": 0.2652540242134035,
                "network": "article_3",
                "optimal_weight": 0.61
            },
            {
                "combination": "disruption_closeness_centrality",
                "correlation": 0.3048676007998933,
                "network": "article_2",
                "optimal_weight": 0.01
            },
            {
                "combination": "eigenvector_centrality_harmonic_centrality",
                "correlation": 0.36188842164740187,
                "network": "article_41",
                "optimal_weight": 0.3
            },
            {
                "combination": "eigenvector_centrality_closeness_centrality",
                "correlation": 0.3047382072131279,
                "network": "article_6",
                "optimal_weight": 0.5
            }
        ]
```

## Processing Steps

The analysis follows these steps for each network set:

```677:691:rankings.ipynb
    "## Processing Steps\n",
    "\n",
    "1. Creates output directory if it doesn't exist\n",
    "2. Makes a copy of the input nodes DataFrame\n",
    "3. For each ground truth measure:\n",
    "   - Calculates an inverted version (max value - original value)\n",
    "   - Stores inverted versions with \"_inverted\" suffix\n",
    "4. Cleans data by:\n",
    "   - Dropping rows with missing ECLI identifiers\n",
    "   - Converting doctypebranch to numeric values if present\n",
    "5. Calculates centrality measures specified\n",
    "6. Creates composite rankings using provided functions\n",
    "7. Computes correlations between:\n",
    "   - Individual centrality measures and ground truths\n",
    "   - Composite rankings and ground truths\n",
```

## Key Differences from Pre-Analysis

1. **Importance Level Merging**

   - Pre-analysis: Separate importance levels 1-4
   - Merged analysis: Combined levels 1-2, maintaining 3 and 4

2. **Network Organization**

   - Pre-analysis: Organized by article and balance type
   - Merged analysis: Organized by size cutoff, then balance type

3. **Statistical Significance**
   - Different cutoff thresholds allow for analysis of how network size affects centrality measure performance
   - Larger networks generally provide more reliable statistical insights

## Usage

For detailed information about the analysis process and methodology, refer to the notebook documentation.
