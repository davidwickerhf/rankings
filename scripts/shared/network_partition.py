from __future__ import annotations

import ast
import json
from pathlib import Path

import pandas as pd


def read_table(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(source, low_memory=False)
    if suffix == ".json":
        return pd.read_json(source)
    raise ValueError(f"Unsupported file format: {source}")


def normalize_edge_references(edges_df: pd.DataFrame) -> pd.DataFrame:
    edges = edges_df.copy()

    def parse_references(value):
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

    edges["references"] = edges["references"].apply(parse_references)
    return edges


def save_as_json(df: pd.DataFrame, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with open(destination, "w", encoding="utf-8") as handle:
        json.dump(df.to_dict(orient="records"), handle, indent=2, ensure_ascii=False)


def get_unique_articles(df: pd.DataFrame) -> set[str]:
    all_articles: set[str] = set()
    filtered = df[df["article"].notna()]
    for articles_str in filtered["article"]:
        articles = {article.strip() for article in str(articles_str).split(";") if article.strip()}
        all_articles.update(articles)
    return all_articles


def get_unique_articles_merged(df: pd.DataFrame) -> set[str]:
    all_articles: set[str] = set()
    filtered = df[df["article"].notna()]
    for articles_str in filtered["article"]:
        parts = [item.strip() for chunk in str(articles_str).split(";") for item in chunk.split("+")]
        articles = {article.strip() for article in parts if article.strip()}
        main_articles = {article.split("-")[0] for article in articles}
        all_articles.update(main_articles)
    return all_articles


def filter_by_article(nodes_df: pd.DataFrame, edges_df: pd.DataFrame, article: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    pattern = f"(?:^|;|\\+){article}(?:-|$|;|\\+)"
    filtered_nodes = nodes_df[nodes_df["article"].str.contains(pattern, na=False, regex=True)]
    valid_eclis = set(filtered_nodes["ecli"].values)
    filtered_edges = edges_df[edges_df["ecli"].isin(valid_eclis)].copy()
    filtered_edges["references"] = filtered_edges["references"].apply(
        lambda refs: [ref for ref in refs if ref in valid_eclis]
    )
    return filtered_nodes, filtered_edges


def count_total_edges(edges_df: pd.DataFrame) -> int:
    total = 0
    for _, row in edges_df.iterrows():
        refs = row["references"]
        if isinstance(refs, list):
            total += len([ref for ref in refs if isinstance(ref, str) and ref.startswith("ECLI:")])
    return total


def balance_network_by_parameter(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    balance_parameter: str,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    class_sizes = nodes_df[balance_parameter].value_counts()
    min_size = class_sizes.min()

    balanced_nodes = pd.DataFrame()
    for class_value in class_sizes.index:
        class_nodes = nodes_df[nodes_df[balance_parameter] == class_value]
        sampled_nodes = class_nodes.sample(n=min_size, random_state=random_state)
        balanced_nodes = pd.concat([balanced_nodes, sampled_nodes], ignore_index=False)

    valid_eclis = set(balanced_nodes["ecli"].values)
    balanced_edges = edges_df[edges_df["ecli"].isin(valid_eclis)].copy()
    balanced_edges["references"] = balanced_edges["references"].apply(
        lambda refs: [ref for ref in refs if ref in valid_eclis]
    )
    return balanced_nodes.reset_index(drop=True), balanced_edges.reset_index(drop=True)


def split_and_save_networks(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    output_root: str | Path,
    min_cases: int = 50,
    merge_subarticles: bool = True,
) -> None:
    output_root = Path(output_root)
    unique_articles = get_unique_articles_merged(nodes_df) if merge_subarticles else get_unique_articles(nodes_df)
    for article in sorted(unique_articles):
        article_nodes, article_edges = filter_by_article(nodes_df, edges_df, article)
        if len(article_nodes) < min_cases:
            continue
        article_dir = output_root / f"article_{article.replace('/', '_')}"
        save_as_json(article_nodes, article_dir / "nodes.json")
        save_as_json(article_edges, article_dir / "edges.json")


def collapse_importance_for_paper(nodes_df: pd.DataFrame) -> pd.DataFrame:
    nodes = nodes_df.copy()
    if "importance" in nodes.columns:
        nodes["importance"] = nodes["importance"].replace({1: 1, 2: 1, 3: 2, 4: 3})
    return nodes
