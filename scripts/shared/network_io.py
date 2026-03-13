from __future__ import annotations

import ast
import os
from pathlib import Path

import pandas as pd


def _is_network_dir(directory: Path) -> bool:
    try:
        contents = {entry.name for entry in directory.iterdir()}
    except OSError:
        return False
    return "nodes.json" in contents and "edges.json" in contents


def _parse_references(value):
    if isinstance(value, list):
        return value
    if pd.isna(value):
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = ast.literal_eval(text)
        except (SyntaxError, ValueError):
            parsed = [part.strip() for part in text.strip("[]").split(",") if part.strip()]
        if isinstance(parsed, list):
            return parsed
    return []


def load_networks(path: str | Path, max_networks: int | None = None, min_nodes: int = 0) -> dict[str, dict[str, pd.DataFrame]]:
    """Recursively load network folders that contain `nodes.json` and `edges.json`."""

    root = Path(path).resolve()
    if not root.exists():
        raise ValueError(f"Directory does not exist: {root}")

    loaded: dict[str, dict[str, pd.DataFrame]] = {}

    for current_root, dirnames, _filenames in os.walk(root):
        if max_networks is not None and len(loaded) >= max_networks:
            break

        current = Path(current_root)
        if not _is_network_dir(current):
            continue

        relative_name = current.relative_to(root).as_posix()
        if relative_name == ".":
            relative_name = current.name

        nodes_df = pd.read_json(current / "nodes.json")
        edges_df = pd.read_json(current / "edges.json")
        edges_df = edges_df.copy()
        edges_df["references"] = edges_df["references"].apply(_parse_references)

        required_node_cols = {"ecli", "importance", "doctypebranch"}
        required_edge_cols = {"ecli", "references"}
        if not required_node_cols.issubset(nodes_df.columns):
            continue
        if not required_edge_cols.issubset(edges_df.columns):
            continue
        if len(nodes_df) < min_nodes:
            continue

        loaded[relative_name] = {"nodes": nodes_df, "edges": edges_df}
        dirnames[:] = []

    return loaded


def load_inherited_total_df(results_root: str | Path, network_name: str) -> pd.DataFrame | None:
    path = Path(results_root) / network_name / "total_df.csv"
    if not path.exists():
        return None
    return pd.read_csv(path, low_memory=False)

