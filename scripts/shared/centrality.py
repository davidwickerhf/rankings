from __future__ import annotations

from datetime import datetime

import networkx as nx
import numpy as np
import pandas as pd

from scripts.shared.constants import CENTRALITY_COLUMNS, GROUND_TRUTHS


def categorise_total_branch_numerically(branches: pd.Series) -> pd.Series:
    mapping = {"GRANDCHAMBER": 1, "CHAMBER": 2, "COMMITTEE": 3}
    if pd.api.types.is_numeric_dtype(branches):
        return branches
    if branches.dtype == "object" and all(str(x).strip() in {"1", "2", "3"} for x in branches.dropna()):
        return branches.astype(int)
    return branches.astype(str).str.upper().map(mapping)


def build_graph(nodes_df: pd.DataFrame, edges_df: pd.DataFrame, ground_truths: list[str] | None = None) -> nx.DiGraph:
    truths = ground_truths or GROUND_TRUTHS
    graph = nx.DiGraph()

    valid_nodes = set(nodes_df["ecli"].dropna())
    for _, row in nodes_df.iterrows():
        node_attrs = {truth: row[truth] for truth in truths if truth in row}
        if "judgementdate" in row:
            node_attrs["judgementdate"] = row["judgementdate"]
        graph.add_node(row["ecli"], **node_attrs)

    for _, row in edges_df.iterrows():
        source = row["ecli"]
        if source not in valid_nodes:
            continue
        for target in row["references"]:
            if target and target in valid_nodes:
                graph.add_edge(source, target)

    graph.remove_edges_from(nx.selfloop_edges(graph))
    return graph


def calculate_disruptions(graph: nx.DiGraph) -> dict[str, float]:
    disruptions: dict[str, float] = {}
    for node in graph.nodes:
        i = 0
        j = 0
        k = 0

        for in_node in graph.predecessors(node):
            for out_node in graph.successors(node):
                if graph.has_edge(in_node, out_node):
                    j += 1
                    break

        i = graph.in_degree(node) - j

        for out_node in graph.successors(node):
            for in_out_node in graph.predecessors(out_node):
                if in_out_node != node and not graph.has_edge(in_out_node, node):
                    k += 1

        denominator = i + j + k
        disruptions[node] = 0.0 if denominator == 0 else (i - j) / denominator
    return disruptions


def calculate_relative_in_degree_centrality(graph: nx.DiGraph) -> dict[str, float]:
    node_dates: dict[str, datetime] = {}
    for node in graph.nodes():
        node_data = graph.nodes[node]
        judgementdate = node_data.get("judgementdate")
        if judgementdate:
            try:
                node_dates[node] = datetime.strptime(str(judgementdate).split()[0], "%Y-%m-%d")
                continue
            except ValueError:
                pass
        ecli_parts = str(node).split(":")
        if len(ecli_parts) >= 4 and ecli_parts[3].isdigit():
            node_dates[node] = datetime(int(ecli_parts[3]), 1, 1)
        else:
            node_dates[node] = datetime(1959, 1, 1)

    sorted_nodes = sorted(node_dates.items(), key=lambda item: item[1])
    node_positions = {node: index for index, (node, _) in enumerate(sorted_nodes)}

    relative_in_degree: dict[str, float] = {}
    for node, _date in sorted_nodes:
        in_degree = graph.in_degree(node)
        max_possible = len(sorted_nodes) - node_positions[node] - 1
        relative_in_degree[node] = in_degree / max_possible if max_possible > 0 else 0.0
    return relative_in_degree


def calculate_centrality_measures(graph: nx.DiGraph) -> tuple[dict[str, dict[str, float]], list[str]]:
    measures = {
        "degree_centrality": nx.degree_centrality(graph),
        "in_degree_centrality": nx.in_degree_centrality(graph),
        "out_degree_centrality": nx.out_degree_centrality(graph),
        "relative_in_degree_centrality": calculate_relative_in_degree_centrality(graph),
        "core_number": nx.core_number(graph),
        "betweenness_centrality": nx.betweenness_centrality(graph),
        "closeness_centrality": nx.closeness_centrality(graph),
        "harmonic_centrality": nx.harmonic_centrality(graph),
    }

    failed: list[str] = []

    undirected = graph.to_undirected()
    try:
        measures["current_flow_betweenness"] = nx.current_flow_betweenness_centrality(undirected)
    except Exception:
        measures["current_flow_betweenness"] = {node: 0.0 for node in graph.nodes()}
        failed.append("current_flow_betweenness")

    try:
        measures["current_flow_closeness"] = nx.current_flow_closeness_centrality(undirected)
    except Exception:
        measures["current_flow_closeness"] = {node: 0.0 for node in graph.nodes()}
        failed.append("current_flow_closeness")

    try:
        measures["eigenvector_centrality"] = nx.eigenvector_centrality(graph, max_iter=1000, tol=1e-6)
    except Exception:
        measures["eigenvector_centrality"] = {node: 0.0 for node in graph.nodes()}
        failed.append("eigenvector_centrality")

    try:
        measures["pagerank"] = nx.pagerank(graph, alpha=0.95, tol=1e-9, max_iter=10000)
    except nx.PowerIterationFailedConvergence:
        try:
            measures["pagerank"] = nx.pagerank(graph, alpha=0.95, tol=1e-9, max_iter=100000)
        except Exception:
            measures["pagerank"] = {node: 0.0 for node in graph.nodes()}
            failed.append("pagerank")
    except Exception:
        measures["pagerank"] = {node: 0.0 for node in graph.nodes()}
        failed.append("pagerank")

    try:
        hubs, authorities = nx.hits(graph, max_iter=100, tol=1e-8)
        measures["hits_hub"] = hubs
        measures["hits_authority"] = authorities
        measures["hits_combined"] = {node: hubs[node] + authorities[node] for node in graph.nodes()}
    except Exception:
        measures["hits_hub"] = {node: 0.0 for node in graph.nodes()}
        measures["hits_authority"] = {node: 0.0 for node in graph.nodes()}
        measures["hits_combined"] = {node: 0.0 for node in graph.nodes()}
        failed.extend(["hits_hub", "hits_authority", "hits_combined"])

    try:
        basal_nodes = [node for node in graph.nodes() if graph.in_degree(node) == 0]
        if not basal_nodes:
            raise ValueError("No basal nodes found")
        measures["trophic_level"] = nx.trophic_levels(graph)
    except Exception:
        measures["trophic_level"] = {node: 0.0 for node in graph.nodes()}
        failed.append("trophic_level")

    try:
        measures["disruption"] = calculate_disruptions(graph)
        values = list(measures["disruption"].values())
        if not all(-1 <= value <= 1 for value in values if not np.isnan(value)):
            raise ValueError("Disruption values outside [-1, 1]")
    except Exception:
        measures["disruption"] = {node: 0.0 for node in graph.nodes()}
        failed.append("disruption")

    return measures, failed


def assemble_total_df(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    inherited_centralities: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, nx.DiGraph, list[str]]:
    """Return the centrality-enriched dataframe used by downstream analysis scripts."""

    nodes = nodes_df.copy()
    if "doctypebranch" in nodes.columns:
        nodes["doctypebranch"] = categorise_total_branch_numerically(nodes["doctypebranch"])
    if "importance" in nodes.columns:
        nodes["importance"] = pd.to_numeric(nodes["importance"], errors="coerce")

    graph = build_graph(nodes, edges_df)
    total_df = nodes.copy()

    if inherited_centralities is not None and not inherited_centralities.empty:
        available = ["ecli"] + [column for column in CENTRALITY_COLUMNS if column in inherited_centralities.columns]
        total_df = pd.merge(total_df, inherited_centralities[available], on="ecli", how="left")
        failed: list[str] = []
    else:
        measures, failed = calculate_centrality_measures(graph)
        centrality_df = pd.DataFrame(measures)
        centrality_df["ecli"] = list(graph.nodes())
        total_df = pd.merge(total_df, centrality_df, on="ecli", how="left")

    if "judgementdate" in total_df.columns:
        total_df["year"] = pd.to_datetime(total_df["judgementdate"], errors="coerce", dayfirst=True).dt.year
    elif "ecli" in total_df.columns:
        total_df["year"] = total_df["ecli"].astype(str).str.extract(r":(\d{4}):")[0].astype(float)

    return total_df, graph, failed
