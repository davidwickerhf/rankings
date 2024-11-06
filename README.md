# Rankings Jupyter Notebook Documentation

## Overview

The `rankings.ipynb` notebook analyzes and compares different centrality metrics for a citation network. It loads node and edge data from JSON files, calculates various centrality metrics (like degree, betweenness, closeness, etc.), and compares them against ground truth measures such as importance and document type.

## Project Setup

To set up the project, follow these steps:

1. **Clone the Repository**:
   Clone the repository to your local machine using the following command:

   ```bash
   git clone https://github.com/davidwickerhf/rankings.git
   ```

2. **Navigate to the Project Directory**:
   Change into the project directory:

   ```bash
   cd rankings
   ```

3. **Create a Virtual Environment** (optional but recommended):
   You can create a virtual environment to manage dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

4. **Install Dependencies**:
   Install the required packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

5. **Launch Jupyter Notebook**:
   Start Jupyter Notebook with the following command:

   ```bash
   jupyter notebook
   ```

6. **Open the Rankings Notebook**:
   In the Jupyter interface, open `rankings.ipynb` to begin your analysis.

## Functionality of `rankings.ipynb`

### 1. Data Loading

The notebook begins by loading node and edge data from JSON files. Ensure that your data files are in the correct format and located in the specified directory.

### 2. Data Preprocessing

Preprocessing steps are applied to clean and prepare the data for analysis. This includes:

- Converting document types to numeric values.
- Filtering out rows with uncomputed metric values.

### 3. Centrality Calculation

The notebook calculates various centrality measures using the NetworkX library. Key centrality metrics include:

- Degree Centrality
- Betweenness Centrality
- Closeness Centrality
- Eigenvector Centrality
- PageRank
- Disruption

### 4. Composite Ranking

The notebook creates composite rankings based on the best-performing centrality measures for predicting high and low relevance scores. It includes:

- Error bar plots for centrality measures against ground truth scores.
- Functions to find the best centrality measures and create composite rankings.

### 5. Correlation Analysis

The notebook calculates correlations between individual centrality measures and ground truth scores, as well as between composite rankings and ground truths. It visualizes these correlations using plots.

### 6. Network Analysis

The `analyze_network()` function performs comprehensive network analysis using various centrality measures and composite rankings. It returns an `AnalysisResults` dictionary containing:

- Basic network statistics (nodes, edges, density, etc.)
- Correlation coefficients between rankings and ground truths
- Best performing centrality measures for each ground truth
- Composite ranking results
- The final processed DataFrame with all measures included

### 7. Comparison of Networks

The `compare_networks()` function allows for the comparison of results across different networks. It analyzes:

- Correlation comparisons between centrality measures and ground truth metrics across networks.
- Ranking comparisons to see how centrality measures rank relative to each other in different networks.

### 8. To Do

- [ ] Reach to vishal about the echr-extractor package
  - [ ] Run get_echr() function (this might include Communicated cases) (Should return around 27.000 cases, with some differences)
    - [ ] Extracted appnos column -> identifies the citations in the text, but not every case
  - [ ] Run get_nodes_edges() function
  - [ ] Compare with what I find on the HUDOC website (https://hudoc.echr.coe.int)
- [ ] Create networks for the different articles (check legal_network_analysis.ipynb file?) (Check where we create the subnetworks for the individual articles, a case can be assigned to multiple articles) (check: https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/FDGGDZ) (might require some pre-processing, as the article info in the get_echr() function is raw text)

  - [ ] Select for the articles that have at least 50 cases
  - [ ] Also consider splitting by year (if not included in metadata, ask Vishal to include in extraction process)

- [ ] Data to find

  - [ ] What centrality scores end up high across the rankings of all the networks that we compare
  - [ ] Which ones end up low
  - [ ] Also in combination with the composite rankings
  - [ ] DataFrames with the results of rankings and correlations per subnetwork

- [ ] Ideas
  - Focus on higher ground truth scores, correlate the error bars for the highest ground truth score to the centrality measures (Find the centralities that best correlate to the highest ground truth scores)

## Conclusion

By following the steps outlined above, you can effectively utilize the `rankings.ipynb` notebook to analyze and visualize centrality metrics in citation networks. Feel free to modify the notebook to suit your specific analysis needs.
