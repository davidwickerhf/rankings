import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.shared.paper_outputs import save_correlation_matrix


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the paper correlation matrix from a total_df.csv file.")
    parser.add_argument(
        "--input",
        default="results/fixed-merged-subarticles-edges/importance-merged/unbalanced/total_df.csv",
        help="Path to the total_df.csv file used for the paper correlation matrix.",
    )
    parser.add_argument(
        "--output",
        default="results/analysis/00_supporting_figures/correlation_matrix.png",
        help="Output image path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    total_df = pd.read_csv(args.input, low_memory=False)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    stats = save_correlation_matrix(total_df, output)
    print(stats)


if __name__ == "__main__":
    main()
