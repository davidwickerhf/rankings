# Networks Directory

This directory contains all network data structures and processed network files for the ECHR centrality analysis.

## Recent Updates (December 2024)

- **Network Processing**: Completed processing of all article-specific networks
- **Balancing Implementation**: Applied importance and doctype branch balancing across all networks
- **Edge Refactoring**: Standardized edge format for consistent analysis
- **Network Validation**: Quality checks and validation of network structures

## Data Files

To perform the analysis in the `rankings.ipynb` notebook, you need to upload your node and edge data files into this folder. Ensure that the files are in JSON format and follow the required structure for proper loading and processing in the notebook.

- **Node Data**: This file should contain information about the nodes in the network, including attributes such as ID, type, and any other relevant metadata.
- **Edge Data**: This file should represent the connections between nodes, including attributes such as source, target, and weight (if applicable).

Make sure to verify the format of your data files before running the analysis to avoid any errors during data loading.
