Here's a comprehensive README documentation for the results in the /pre folder:

# Pre-Analysis Results Documentation

## Overview

The `/pre` folder contains analysis results from running centrality metrics and composite rankings on different subsets of the ECHR citation network. The results are organized hierarchically based on network balancing strategies and article groupings.

## Folder Structure

```
/pre
├── /balanced-doctypebranch    # Networks balanced by document type
├── /balanced-importance       # Networks balanced by importance
├── /full                     # Complete network analysis
│   ├── /full-balanced-doctypebranch
│   ├── /full-balanced-importance
│   └── /full-unbalanced
└── /unbalanced              # Unbalanced network analyses by article
```

## Network Types

### 1. Balanced Networks

- **Doctypebranch-balanced**: Networks where document types (GRANDCHAMBER, CHAMBER, COMMITTEE) are evenly distributed
- **Importance-balanced**: Networks where importance scores are evenly distributed

### 2. Unbalanced Networks

- Original networks without any balancing applied
- Preserves natural distribution of document types and importance scores

## Analysis Results Structure

Each network analysis produces a JSON file (`analysis_results.json`) containing:

1. **Centrality Rankings**

   - Individual rankings for each centrality measure
   - Values normalized between 0-1
   - Higher values indicate greater centrality

2. **Composite Rankings**

   - Combined rankings using weighted combinations of centrality measures
   - Two types of ground truths:
     - `importance`: Case importance (1-4 scale)
     - `doctypebranch`: Document type branch (GRANDCHAMBER=1, CHAMBER=2, COMMITTEE=3)

3. **Weight Parameters**
   - `weight_composite_ranking_param`: Optimal weight found for combining centrality measures
   - Found in each ground truth section (see example in code reference below)

```303:305:results/pre/unbalanced/article_13/analysis_results.json

```

4. **Performance Metrics**
   - Correlation coefficients between rankings and ground truths
   - Best performing centrality measures for each ground truth
   - Distribution statistics of classes (importance levels and document types)

## How to Read the Results

1. **Network Size**
   - Larger numbers in rankings indicate bigger networks
   - Networks were filtered to have minimum 50 cases (as shown in process logs):

```448:466:load/process.ipynb
      "Created network for Article 3+8 with 594 nodes\n",
      "Skipping Article 43 - only 12 cases (minimum: 50)\n",
      "Skipping Article 18+5-3 - only 0 cases (minimum: 50)\n",
      "Skipping Article 14+11 - only 0 cases (minimum: 50)\n",
      "Skipping Article 13+P1-3 - only 0 cases (minimum: 50)\n",
      "Skipping Article 35-4 - only 35 cases (minimum: 50)\n",
      "Skipping Article 7+6 - only 0 cases (minimum: 50)\n",
      "Created network for Article 38 with 594 nodes\n",
      "Skipping Article 2+P6-1 - only 0 cases (minimum: 50)\n",
      "Skipping Article P7-4-1 - only 2 cases (minimum: 50)\n",
      "Skipping Article 35+8-1 - only 0 cases (minimum: 50)\n",
      "Skipping Article 13+P4-2-1 - only 0 cases (minimum: 50)\n",
      "Skipping Article 8+9 - only 0 cases (minimum: 50)\n",
      "Skipping Article 6+3 - only 0 cases (minimum: 50)\n",
      "Skipping Article 6-1+6-3-a - only 0 cases (minimum: 50)\n",
      "Created network for Article 46-2 with 313 nodes\n",
      "Skipping Article 18+6 - only 0 cases (minimum: 50)\n",
      "Skipping Article 5+5-2 - only 0 cases (minimum: 50)\n",
      "Skipping Article 13+34 - only 0 cases (minimum: 50)\n",
```

2. **Ranking Values**

   - Values represent relative positions in the network
   - Higher values generally indicate more central/important nodes
   - Normalized to maintain comparability across networks

3. **Document Type Mapping**
   The `doctypebranch` values are mapped numerically as shown in the utils:

```96:100:rankings.ipynb
    "    mapping = {\n",
    "        \"GRANDCHAMBER\": 1,\n",
    "        \"CHAMBER\": 2,\n",
    "        \"COMMITTEE\": 3,\n",
    "    }\n",
```

## Key Metrics to Look For

1. **Weight Parameters**
   - Values closer to 1 indicate stronger reliance on centrality measures
   - Values closer to 0 suggest more emphasis on other factors
   - Example from Article 13 network:

```304:305:results/pre/unbalanced/article_13/analysis_results.json

```

2. **Class Distribution**
   - Shows balance/imbalance of importance levels and document types
   - Example from Article 13:

```8072:8082:results/pre/unbalanced/article_13/analysis_results.json
    "class_distribution": {
        "total_cases": 3991,
        "class_counts": {
            "importance": {
                "4": 2917,
                "3": 694,
                "2": 205,
                "1": 175
            },
            "doctypebranch": {
                "2": 2528,
```

## How Results Were Obtained

The analysis process followed these steps (as documented in the main README):

```677:691:README.md

```

## Using the Results

1. **Comparing Networks**

   - Compare weight parameters across different networks
   - Look at class distributions to understand network composition
   - Examine best performing centrality measures for consistency

2. **Evaluating Performance**

   - Check correlation coefficients between rankings and ground truths
   - Compare composite ranking performance against individual centrality measures
   - Look at class distribution to understand potential biases

3. **Finding Best Performers**
   - Each network analysis includes a "best_centralities" section
   - Shows top performing measures for both high and low predictions
   - Useful for understanding which metrics work best in different contexts

## Additional Resources

For more detailed information about the analysis process and methodology, refer to the main project documentation.
