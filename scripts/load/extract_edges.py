from __future__ import annotations

import argparse
import ast
import multiprocessing
import re
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Set, Tuple

import dateparser
import numpy as np
import pandas as pd
from echr_extractor.clean_ref import clean_pattern
from tqdm import tqdm


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "METADATA" / "echr_metadata.csv"
DEFAULT_OUTPUT_DIR = ROOT / "results" / "load" / "edge_extraction"

case_name_cache: Dict[str, Set[str]] = {}


def clear_caches() -> None:
    case_name_cache.clear()
    lookup_casename.cache_clear()


def open_metadata(path_metadata: str | Path) -> pd.DataFrame | bool:
    try:
        return pd.read_csv(path_metadata, low_memory=False)
    except FileNotFoundError:
        print("File not found. Please check the path to the metadata file.")
        return False


def get_casename(ref: str) -> str:
    if "v." in ref:
        slice_at_versus = ref.split("v.")
    elif "c." in ref:
        slice_at_versus = ref.split("c.")
    else:
        return ref.split(",")[0]

    num_commas = slice_at_versus[0].count(",")
    if num_commas > 0:
        return ",".join(ref.split(",", num_commas + 1)[: num_commas + 1])
    return ref.split(",")[0]


def metadata_to_nodesedgeslist(df: pd.DataFrame) -> pd.DataFrame:
    return df


def retrieve_nodes_list(df: pd.DataFrame) -> pd.DataFrame:
    df = metadata_to_nodesedgeslist(df)
    initial_count = len(df)
    null_eclis = df[df["ecli"].isna()]
    df = df.dropna(subset=["ecli"])

    duplicates = df[df["ecli"].duplicated(keep=False)]
    if len(duplicates) > 0:
        print(f"\nWarning: Found {len(duplicates)} rows with duplicate ECLIs")
        print(f"Number of unique duplicate ECLIs: {duplicates['ecli'].nunique()}")
        df = df.drop_duplicates(subset=["ecli"], keep="first")

    df = df.copy()
    col = df.pop("ecli")
    df.insert(0, col.name, col)

    print("\nNode Cleaning Summary:")
    print(f"Initial nodes: {initial_count}")
    print(f"Dropped null ECLIs: {len(null_eclis)}")
    print(f"Dropped duplicate rows: {len(duplicates)}")
    print(f"Final nodes: {len(df)}")
    return df


@lru_cache(maxsize=50000)
def get_year_from_ref(ref_tuple: Tuple[str, ...]) -> int:
    for component in list(ref_tuple):
        if "§" in component:
            continue
        component = re.sub("judgment of ", "", component)
        if dateparser.parse(component) is not None:
            date = dateparser.parse(component)
        elif "ECHR" in component or "CEDH" in component:
            date = re.sub("ECHR |CEDH ", "", component).strip()
            date = re.sub(r"-.*|\s.*", "", date)
            date = dateparser.parse(date)
        else:
            continue
        if date is not None:
            return date.year
    return 0


@lru_cache(maxsize=50000)
def lookup_casename(ref: str, df_dict: Tuple[Tuple, ...]) -> Set[str]:
    name = get_casename(ref)
    uptext = name.upper()

    if "NO." in uptext:
        uptext = uptext.replace("NO.", "No.")
    if "BV" in uptext:
        uptext = uptext.replace("BV", "B.V.")
    if "v." in name:
        uptext = uptext.replace("V.", "v.")
    else:
        uptext = uptext.replace("C.", "c.")

    for pattern in clean_pattern:
        uptext = re.sub(pattern, "", uptext)

    uptext = re.sub(r"\[.*", "", uptext).strip()
    df_dict_list = [dict(zip(("docname", "ecli", "appno"), row)) for row in df_dict]

    return {
        row["ecli"]
        for row in df_dict_list
        if pd.notna(row.get("docname"))
        and pd.notna(row.get("ecli"))
        and f"CASE OF {uptext}" == row["docname"].upper()
    }


def process_batch(batch_data: Tuple[pd.DataFrame, Tuple[Tuple, ...], int]) -> Tuple[List[Dict], List[Dict]]:
    df_batch, df_dict, _batch_size = batch_data
    edges_list = []
    missing_cases = []
    df_dict_list = [dict(zip(("docname", "ecli", "appno"), row)) for row in df_dict]

    for _, item in df_batch.iterrows():
        if pd.isna(item.ecli):
            missing_cases.append(
                {
                    "source_ecli": "NaN",
                    "missing_reference": "Source ECLI is missing",
                    "reference_type": "missing_source",
                }
            )
            continue

        eclis = set()

        if pd.notna(item.extractedappno):
            extracted_appnos = set(item.extractedappno.split(";"))
            matches = [
                row
                for row in df_dict_list
                if pd.notna(row.get("appno")) and row["appno"] in extracted_appnos
            ]

            found_appnos = {row["appno"] for row in matches}
            for appno in extracted_appnos - found_appnos:
                missing_cases.append(
                    {
                        "source_ecli": item.ecli,
                        "missing_reference": f"Application number: {appno}",
                        "reference_type": "extracted_appno",
                    }
                )

            eclis.update(row["ecli"] for row in matches if pd.notna(row.get("ecli")))

        if pd.notna(item.scl):
            ref_list = [ref.strip() for ref in item.scl.split(";")]
            for ref in ref_list:
                app_numbers = set(re.findall(r"[0-9]{3,5}/[0-9]{2}", ref))
                if app_numbers:
                    matches = [
                        row
                        for row in df_dict_list
                        if pd.notna(row.get("appno")) and row["appno"] in app_numbers
                    ]
                    found_apps = {row["appno"] for row in matches}
                    for app in app_numbers - found_apps:
                        missing_cases.append(
                            {
                                "source_ecli": item.ecli,
                                "missing_reference": f"Application number: {app}",
                                "reference_type": "scl_appno",
                            }
                        )

                    eclis.update(row["ecli"] for row in matches if pd.notna(row.get("ecli")))
                else:
                    case_eclis = lookup_casename(ref, df_dict)
                    if not case_eclis:
                        missing_cases.append(
                            {
                                "source_ecli": item.ecli,
                                "missing_reference": ref,
                                "reference_type": "case_name",
                            }
                        )
                    eclis.update(case_eclis)

        valid_refs = [
            ref
            for ref in eclis
            if isinstance(ref, str) and pd.notna(ref) and ref != item.ecli and ref.startswith("ECLI:")
        ]
        edges_list.append({"ecli": item.ecli, "references": valid_refs})

    return edges_list, missing_cases


def retrieve_edges_list(df: pd.DataFrame, df_unfiltered: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    num_cores = multiprocessing.cpu_count()
    batch_size = max(100, len(df) // max(num_cores * 4, 1))

    df_dict = tuple(tuple(row) for row in df_unfiltered[["docname", "ecli", "appno"]].itertuples(index=False))
    batches = [(df[i : i + batch_size], df_dict, batch_size) for i in range(0, len(df), batch_size)]

    edges_list = []
    all_missing_cases = []
    processed_rows = 0

    with tqdm(total=len(df), desc="Processing edges") as pbar:
        with ProcessPoolExecutor(max_workers=num_cores) as executor:
            for batch_edges, batch_missing in executor.map(process_batch, batches):
                edges_list.extend(batch_edges)
                all_missing_cases.extend(batch_missing)
                processed_rows += len(batch_edges)
                pbar.update(len(batch_edges))

    all_missing_cases = [dict(t) for t in {tuple(d.items()) for d in all_missing_cases}]
    missing_df = pd.DataFrame(all_missing_cases)
    missing_targets = missing_df["missing_reference"].nunique() if not missing_df.empty else 0

    print("\nReference Extraction Summary:")
    print(f"Total nodes processed: {processed_rows}")
    print(f"Total edges found: {sum(len(d['references']) for d in edges_list)}")
    print(f"Total failed edges: {len(all_missing_cases)}")
    print(f"Total missing targets: {missing_targets}")

    return pd.DataFrame(edges_list), missing_df


def echr_nodes_edges(metadata_path: str | Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    print("\n--- COLLECTING METADATA ---\n")
    data = open_metadata(metadata_path)
    if data is False:
        raise FileNotFoundError(f"Could not open metadata file: {metadata_path}")

    print("\n--- EXTRACTING NODES LIST ---\n")
    nodes = retrieve_nodes_list(data)
    print(f"Number of nodes: {len(nodes)}")

    print("\n--- EXTRACTING EDGES LIST ---\n")
    edges, missing_df = retrieve_edges_list(nodes, data)
    print(f"\nExtracted {len(edges)} edges")
    print(f"Found {len(missing_df)} missing references")
    return nodes, edges, missing_df


def count_total_edges(edges_df: pd.DataFrame) -> Tuple[int, dict]:
    stats = {
        "total_edges": 0,
        "total_source_nodes": len(edges_df),
        "nodes_with_refs": 0,
        "max_refs_per_node": 0,
        "refs_distribution": [],
        "suspicious_nodes": [],
    }

    for _, row in edges_df.iterrows():
        refs = row["references"]
        if isinstance(refs, str):
            try:
                refs_list = ast.literal_eval(refs)
            except (SyntaxError, ValueError):
                continue
        else:
            refs_list = refs

        valid_refs = [
            ref
            for ref in refs_list
            if isinstance(ref, str) and not pd.isna(ref) and ref.startswith("ECLI:")
        ]
        num_refs = len(valid_refs)
        if num_refs > 0:
            stats["nodes_with_refs"] += 1
            stats["total_edges"] += num_refs
            stats["refs_distribution"].append(num_refs)
            stats["max_refs_per_node"] = max(stats["max_refs_per_node"], num_refs)
            if num_refs > 100:
                stats["suspicious_nodes"].append({"ecli": row["ecli"], "ref_count": num_refs})

    if stats["refs_distribution"]:
        stats["avg_refs_per_node"] = sum(stats["refs_distribution"]) / len(stats["refs_distribution"])
        stats["median_refs_per_node"] = np.median(stats["refs_distribution"])

    print("\nEdge Analysis:")
    print(f"Total source nodes: {stats['total_source_nodes']}")
    print(f"Nodes with references: {stats['nodes_with_refs']}")
    print(f"Total edges: {stats['total_edges']}")
    print(f"Average refs per node: {stats.get('avg_refs_per_node', 0):.2f}")
    print(f"Median refs per node: {stats.get('median_refs_per_node', 0):.2f}")
    print(f"Max refs per node: {stats['max_refs_per_node']}")
    if stats["suspicious_nodes"]:
        print("\nSuspicious Nodes (>100 references):")
        for node in stats["suspicious_nodes"]:
            print(f"ECLI: {node['ecli']}, References: {node['ref_count']}")
    return stats["total_edges"], stats


def count_application_numbers(metadata_file: str | Path) -> None:
    df = pd.read_csv(metadata_file, low_memory=False)
    print(f"Total rows in metadata: {len(df)}")

    has_appno = df["extractedappno"].notna()
    print(f"Rows with application numbers: {has_appno.sum()}")

    total_appnos = 0
    unique_appnos = set()
    for appno in df[has_appno]["extractedappno"]:
        if isinstance(appno, str):
            appnos = appno.split(";")
            total_appnos += len(appnos)
            unique_appnos.update(appnos)

    print(f"Total application numbers: {total_appnos}")
    print(f"Unique application numbers: {len(unique_appnos)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve citation references from the canonical metadata CSV and export nodes/edges plus missing-reference diagnostics."
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to the canonical metadata CSV.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where nodes.csv, edges.csv, and missing_cases.csv are written.",
    )
    parser.add_argument(
        "--skip-appno-summary",
        action="store_true",
        help="Skip the application-number summary before extraction.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    clear_caches()
    if not args.skip_appno_summary:
        count_application_numbers(input_path)

    nodes, edges, missing = echr_nodes_edges(input_path)
    print(f"Number of nodes: {len(nodes)}")
    print(f"Number of edge rows: {len(edges)}")
    count_total_edges(edges)

    nodes.to_csv(output_dir / "nodes.csv", index=False)
    edges.to_csv(output_dir / "edges.csv", index=False)
    missing.to_csv(output_dir / "missing_cases.csv", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
