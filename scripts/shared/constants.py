"""Constants shared across the analysis pipeline."""

GROUND_TRUTHS = ["importance", "doctypebranch"]

CENTRALITY_COLUMNS = [
    "degree_centrality",
    "in_degree_centrality",
    "out_degree_centrality",
    "relative_in_degree_centrality",
    "core_number",
    "betweenness_centrality",
    "closeness_centrality",
    "harmonic_centrality",
    "current_flow_betweenness",
    "current_flow_closeness",
    "eigenvector_centrality",
    "pagerank",
    "hits_hub",
    "hits_authority",
    "hits_combined",
    "trophic_level",
    "disruption",
]

PAPER_CENTRALITIES = [
    "degree_centrality",
    "in_degree_centrality",
    "out_degree_centrality",
    "betweenness_centrality",
    "closeness_centrality",
    "core_number",
    "relative_in_degree_centrality",
    "eigenvector_centrality",
    "pagerank",
    "hits_hub",
    "hits_authority",
    "harmonic_centrality",
    "disruption",
]

CORRELATION_MATRIX_ORDER = [
    "importance",
    "doctypebranch",
    "disruption",
    "hits_hub",
    "out_degree_centrality",
    "betweenness_centrality",
    "core_number",
    "degree_centrality",
    "hits_authority",
    "in_degree_centrality",
    "relative_in_degree_centrality",
    "pagerank",
    "eigenvector_centrality",
    "harmonic_centrality",
    "closeness_centrality",
]

