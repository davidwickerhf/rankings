import argparse
import sys
import networkx as nx
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.shared.centrality import assemble_total_df
from scripts.shared.constants import GROUND_TRUTHS, PAPER_CENTRALITIES
from scripts.shared.network_io import load_inherited_total_df, load_networks
from scripts.shared.paper_outputs import plot_error_bar, save_analysis_results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build centrality-enriched dataframes and per-network plots from nodes/edges JSON files.")
    parser.add_argument("--network-dir", required=True, help="Root directory containing network folders.")
    parser.add_argument("--output-dir", required=True, help="Directory where per-network outputs are written.")
    parser.add_argument("--inherit-from", help="Optional results root containing existing total_df.csv files to inherit centralities from.")
    parser.add_argument("--min-nodes", type=int, default=0, help="Skip networks with fewer than this many nodes.")
    parser.add_argument("--max-networks", type=int, help="Optional cap on number of networks to process.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    networks = load_networks(args.network_dir, max_networks=args.max_networks, min_nodes=args.min_nodes)
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    for network_name, data in networks.items():
        print(f"Processing {network_name}")
        inherited = None
        if args.inherit_from:
            inherited = load_inherited_total_df(args.inherit_from, network_name)

        total_df, graph, failed = assemble_total_df(data["nodes"], data["edges"], inherited_centralities=inherited)
        network_output = output_root / network_name
        network_output.mkdir(parents=True, exist_ok=True)
        total_df.to_csv(network_output / "total_df.csv", index=False)

        network_stats = {
            "num_nodes": int(len(data["nodes"])),
            "num_edges": int(sum(len(refs) for refs in data["edges"]["references"])),
            "density": float(nx.density(graph)),
            "average_degree": float(sum(dict(graph.degree()).values()) / graph.number_of_nodes()) if graph.number_of_nodes() else 0.0,
        }

        for ground_truth in GROUND_TRUTHS:
            for centrality in PAPER_CENTRALITIES:
                if centrality in total_df.columns:
                    plot_error_bar(total_df, centrality, ground_truth, network_output)

        save_analysis_results(total_df, network_output, network_stats, failed, centralities=PAPER_CENTRALITIES)


if __name__ == "__main__":
    main()
