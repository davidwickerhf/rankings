from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.shared.network_partition import (
    balance_network_by_parameter,
    collapse_importance_for_paper,
    count_total_edges,
    normalize_edge_references,
    read_table,
    save_as_json,
    split_and_save_networks,
)


DEFAULT_NODES = ROOT / "results" / "load" / "metadata_graph" / "nodes.csv"
DEFAULT_EDGES = ROOT / "results" / "load" / "metadata_graph" / "edges.csv"
DEFAULT_OUTPUT = ROOT / "networks" / "merged-article-edges"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild the paper's merged-article-edge network family from nodes/edges tables."
    )
    parser.add_argument("--nodes", default=str(DEFAULT_NODES), help="CSV or JSON nodes file.")
    parser.add_argument("--edges", default=str(DEFAULT_EDGES), help="CSV or JSON edges file.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT), help="Output directory for the rebuilt networks.")
    parser.add_argument("--min-cases", type=int, default=50, help="Minimum number of cases required for a split article network.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    nodes_df = read_table(args.nodes)
    edges_df = normalize_edge_references(read_table(args.edges))
    output_root = Path(args.output_root)

    all_nodes_df = collapse_importance_for_paper(nodes_df)
    all_edges_df = edges_df.copy()

    print(f"Number of nodes: {len(all_nodes_df)}")
    print(f"Number of edges: {count_total_edges(all_edges_df)}")

    balanced_nodes_importance, balanced_edges_importance = balance_network_by_parameter(
        nodes_df=all_nodes_df,
        edges_df=all_edges_df,
        balance_parameter="importance",
    )
    balanced_nodes_doctypebranch, balanced_edges_doctypebranch = balance_network_by_parameter(
        nodes_df=all_nodes_df,
        edges_df=all_edges_df,
        balance_parameter="doctypebranch",
    )

    save_as_json(all_nodes_df, output_root / "full-unbalanced" / "nodes.json")
    save_as_json(all_edges_df, output_root / "full-unbalanced" / "edges.json")
    save_as_json(balanced_nodes_importance, output_root / "full-balanced-importance" / "nodes.json")
    save_as_json(balanced_edges_importance, output_root / "full-balanced-importance" / "edges.json")
    save_as_json(balanced_nodes_doctypebranch, output_root / "full-balanced-doctypebranch" / "nodes.json")
    save_as_json(balanced_edges_doctypebranch, output_root / "full-balanced-doctypebranch" / "edges.json")

    split_and_save_networks(
        balanced_nodes_importance,
        balanced_edges_importance,
        output_root / "split-balanced-importance",
        min_cases=args.min_cases,
        merge_subarticles=True,
    )
    split_and_save_networks(
        balanced_nodes_doctypebranch,
        balanced_edges_doctypebranch,
        output_root / "split-balanced-doctypebranch",
        min_cases=args.min_cases,
        merge_subarticles=True,
    )
    split_and_save_networks(
        all_nodes_df,
        all_edges_df,
        output_root / "split-unbalanced",
        min_cases=args.min_cases,
        merge_subarticles=True,
    )


if __name__ == "__main__":
    main()
