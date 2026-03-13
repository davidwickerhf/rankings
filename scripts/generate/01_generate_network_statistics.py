import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.shared.network_io import load_networks
from scripts.shared.network_stats import create_network_summary


DEFAULT_NETWORK_DIRS = [
    "networks/merged-article-edges/full-balanced-importance",
    "networks/merged-article-edges/full-unbalanced",
    "networks/merged-article-edges/full-balanced-doctypebranch",
    "networks/merged-article-edges/split-balanced-importance",
    "networks/merged-article-edges/split-balanced-doctypebranch",
    "networks/merged-article-edges/split-unbalanced",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the network statistics table used by the paper.")
    parser.add_argument("--network-dir", action="append", dest="network_dirs", help="Network directory to include. Can be passed multiple times.")
    parser.add_argument(
        "--output",
        default="results/analysis/00_supporting_tables/network_statistics_updated.csv",
        help="CSV output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    directories = args.network_dirs or DEFAULT_NETWORK_DIRS

    networks = {}
    for directory in directories:
        loaded = load_networks(directory, min_nodes=0)
        prefix = directory.split("/")[-1]
        networks.update({f"{prefix}-{name}": data for name, data in loaded.items()})

    create_network_summary(networks, args.output)


if __name__ == "__main__":
    main()
