from __future__ import annotations

import argparse
import ast
import json
import sys
from datetime import datetime
from pathlib import Path

import echr_extractor.echr as echr
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "METADATA" / "echr_metadata.csv"
DEFAULT_OUTPUT_DIR = ROOT / "results" / "load" / "metadata_graph"


def print_log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)
    sys.stdout.flush()


def _parse_references(value):
    if isinstance(value, list):
        return value
    if pd.isna(value):
        return []
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return []
        if isinstance(parsed, list):
            return parsed
    return []


def process_data(input_file: Path, output_dir: Path) -> bool:
    print_log("Starting metadata processing")
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_file, low_memory=False)
    print_log(f"Loaded {len(df)} metadata rows from {input_file}")

    missing_eclis = df["ecli"].isna().sum() if "ecli" in df.columns else 0
    duplicate_count = len(df) - df["ecli"].nunique() if "ecli" in df.columns else 0
    print_log(f"Rows with missing ECLI: {missing_eclis}")
    print_log(f"Duplicate ECLI rows: {duplicate_count}")

    try:
        nodes, edges = echr.get_nodes_edges(df=df, save_file="n")
        print_log(f"Generated {len(nodes)} nodes and {len(edges)} edge rows")

        nodes.to_csv(output_dir / "nodes.csv", index=False)
        edges.to_csv(output_dir / "edges.csv", index=False)

        edges_json = [
            {
                "ecli": row["ecli"],
                "references": _parse_references(row["references"]),
            }
            for _, row in edges.iterrows()
        ]

        with open(output_dir / "nodes.json", "w", encoding="utf-8") as handle:
            json.dump(nodes.to_dict(orient="records"), handle, indent=2, ensure_ascii=False)

        with open(output_dir / "edges.json", "w", encoding="utf-8") as handle:
            json.dump(edges_json, handle, indent=2, ensure_ascii=False)

        print_log(f"Saved processed metadata bundle to {output_dir}")
    except Exception as exc:
        import traceback

        print_log(f"Error processing metadata: {exc}")
        print_log(traceback.format_exc())
        return False

    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert the canonical ECtHR metadata CSV into nodes/edges CSV and JSON bundles."
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to the canonical metadata CSV.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where nodes/edges CSV and JSON files are written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    success = process_data(Path(args.input), Path(args.output_dir))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
