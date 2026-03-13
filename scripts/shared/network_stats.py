from __future__ import annotations

import networkx as nx
import pandas as pd
from pathlib import Path

try:
    from tabulate import tabulate
except ImportError:  # pragma: no cover - optional pretty-print dependency
    tabulate = None

from scripts.shared.centrality import categorise_total_branch_numerically


def analyze_network_stats(nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> dict:
    nodes = nodes_df.copy()
    nodes["year"] = pd.to_numeric(nodes["ecli"].astype(str).str.extract(r":(\d{4}):")[0], errors="coerce")
    if "doctypebranch" in nodes.columns:
        nodes["doctypebranch"] = categorise_total_branch_numerically(nodes["doctypebranch"])
        nodes = nodes.dropna(subset=["doctypebranch"])
    nodes["importance"] = pd.to_numeric(nodes["importance"], errors="coerce")
    nodes = nodes.dropna(subset=["ecli"])

    graph = nx.DiGraph()
    valid_nodes = set(nodes["ecli"].values)
    for _, row in nodes.iterrows():
        graph.add_node(
            row["ecli"],
            importance=row.get("importance"),
            doctypebranch=row.get("doctypebranch"),
            year=row.get("year"),
        )

    edge_count = 0
    for _, row in edges_df.iterrows():
        source = row["ecli"]
        if source not in valid_nodes:
            continue
        for target in row["references"]:
            if target and target in valid_nodes:
                graph.add_edge(source, target)
                edge_count += 1

    graph.remove_edges_from(nx.selfloop_edges(graph))

    connected_nodes = sum(1 for node in graph.nodes() if graph.degree(node) > 0)
    components = [component for component in nx.weakly_connected_components(graph) if len(component) >= 2]

    judgement_dates = pd.to_datetime(nodes["judgementdate"].astype(str).str.split(" ").str[0], format="%d/%m/%Y", errors="coerce")
    pre_1998 = nodes[judgement_dates < pd.to_datetime("01/11/1998", format="%d/%m/%Y")]
    post_1998 = nodes[judgement_dates >= pd.to_datetime("01/11/1998", format="%d/%m/%Y")]

    return {
        "total_initial_nodes": len(nodes),
        "total_valid_nodes": len(valid_nodes),
        "nodes_removed": len(nodes) - len(valid_nodes),
        "total_edges": edge_count,
        "connected_nodes": connected_nodes,
        "non_connected_nodes": len(valid_nodes) - connected_nodes,
        "num_components": len(components),
        "biggest_component_size": len(max(components, key=len)) if components else 0,
        "density": nx.density(graph),
        "doctypebranch_dist": nodes["doctypebranch"].value_counts().to_dict() if "doctypebranch" in nodes.columns else {},
        "importance_dist": nodes["importance"].value_counts().to_dict(),
        "importance_dist_pre_1998": pre_1998["importance"].value_counts().to_dict(),
        "importance_dist_post_1998": post_1998["importance"].value_counts().to_dict(),
    }


def create_network_summary(networks: dict[str, dict[str, pd.DataFrame]], output_path: str | Path) -> pd.DataFrame:
    rows = []
    for network_name, data in networks.items():
        stats = analyze_network_stats(data["nodes"], data["edges"])
        rows.append(
            [
                network_name,
                stats["total_initial_nodes"],
                stats["total_valid_nodes"],
                stats["nodes_removed"],
                stats["total_edges"],
                stats["connected_nodes"],
                stats["non_connected_nodes"],
                stats["num_components"],
                stats["biggest_component_size"],
                f"{stats['density']:.8f}",
                ", ".join(f"{k}: {v}" for k, v in stats["doctypebranch_dist"].items()),
                ", ".join(f"{k}: {v}" for k, v in stats["importance_dist"].items()),
                ", ".join(f"{k}: {v}" for k, v in stats["importance_dist_pre_1998"].items()),
                ", ".join(f"{k}: {v}" for k, v in stats["importance_dist_post_1998"].items()),
            ]
        )

    headers = [
        "Network",
        "Initial Nodes",
        "Valid Nodes",
        "Removed Nodes",
        "Total Edges",
        "Connected Nodes",
        "Non-Connected Nodes",
        "Connected Components",
        "Biggest Component Size",
        "Density",
        "Doctypebranch Distribution",
        "Importance Distribution",
        "Importance Pre-1998",
        "Importance Post-1998",
    ]

    rows.sort(key=lambda row: row[2], reverse=True)
    if tabulate is not None:
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        print(pd.DataFrame(rows, columns=headers).to_string(index=False))

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    dataframe = pd.DataFrame(rows, columns=headers)
    dataframe.to_csv(output, index=False)
    return dataframe
