from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

from scripts.shared.constants import CORRELATION_MATRIX_ORDER, GROUND_TRUTHS, PAPER_CENTRALITIES


def plot_error_bar(total_df: pd.DataFrame, centrality: str, ground_truth: str, output_path: str | Path) -> None:
    data = total_df[[ground_truth, centrality]].copy()
    data = data[data[centrality] != -2]
    grouped = data.groupby(ground_truth)[centrality].agg(["mean", "std"]).reset_index()

    plt.figure(figsize=(10, 6))
    plt.errorbar(
        grouped["mean"],
        grouped[ground_truth],
        xerr=grouped["std"],
        fmt="o",
        capsize=5,
        capthick=1,
        elinewidth=1,
        markersize=8,
    )
    plt.title(f"{centrality} vs. Average {ground_truth}", fontsize=16)
    plt.xlabel(centrality.replace("_", " ").title(), fontsize=16)
    plt.ylabel(ground_truth.replace("_", " ").title(), fontsize=16)
    plt.yticks(grouped[ground_truth], fontsize=16)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(Path(output_path) / f"{centrality}_{ground_truth}_error_bars.png", bbox_inches="tight", dpi=300)
    plt.close()


def calculate_ground_truth_correlations(total_df: pd.DataFrame, centralities: list[str] | None = None) -> dict[str, list[dict[str, float | str]]]:
    measures = centralities or PAPER_CENTRALITIES
    results: dict[str, list[dict[str, float | str]]] = {}
    for ground_truth in GROUND_TRUTHS:
        rows = []
        for centrality in measures:
            corr, p_value = stats.spearmanr(total_df[centrality], total_df[ground_truth], nan_policy="omit")
            rows.append(
                {
                    "centrality": centrality,
                    "correlation": float(corr),
                    "abs_correlation": float(abs(corr)),
                    "p_value": float(p_value),
                }
            )
        rows.sort(key=lambda row: row["abs_correlation"], reverse=True)
        results[ground_truth] = rows
    return results


def save_ground_truth_correlations(total_df: pd.DataFrame, output_dir: str | Path, centralities: list[str] | None = None) -> dict[str, list[dict[str, float | str]]]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    correlations = calculate_ground_truth_correlations(total_df, centralities=centralities)
    for ground_truth, rows in correlations.items():
        pd.DataFrame(rows).to_csv(output / f"correlations_{ground_truth}.csv", index=False)
    return correlations


def plot_correlation_bars(correlations: dict[str, list[dict[str, float | str]]], output_file: str | Path) -> None:
    measures = [row["centrality"] for row in correlations[GROUND_TRUTHS[0]]]
    x = np.arange(len(measures))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 8))
    for index, ground_truth in enumerate(GROUND_TRUTHS):
        values = [next(row["correlation"] for row in correlations[ground_truth] if row["centrality"] == measure) for measure in measures]
        ax.bar(x + (index - 0.5) * width, values, width, label=ground_truth)

    ax.set_xticks(x)
    ax.set_xticklabels(measures, rotation=45, ha="right")
    ax.set_ylabel("Spearman correlation")
    ax.set_title("Centrality vs ground truth correlations")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()


def calculate_pvalue_matrix(total_df: pd.DataFrame, measures: list[str]) -> pd.DataFrame:
    matrix = np.zeros((len(measures), len(measures)))
    for i, measure1 in enumerate(measures):
        for j, measure2 in enumerate(measures):
            _, p_value = stats.spearmanr(total_df[measure1], total_df[measure2], nan_policy="omit")
            matrix[i, j] = p_value
    return pd.DataFrame(matrix, index=measures, columns=measures)


def save_correlation_matrix(total_df: pd.DataFrame, output_file: str | Path) -> dict[str, float]:
    measures = [measure for measure in CORRELATION_MATRIX_ORDER if measure in total_df.columns]
    corr_matrix = total_df[measures].corr(method="spearman")
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix.loc[measures, measures], annot=True, cmap="RdBu", vmin=-1, vmax=1, center=0, fmt=".2f")
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    ground_truth_corr, ground_truth_p = stats.spearmanr(total_df["importance"], total_df["doctypebranch"], nan_policy="omit")
    return {"ground_truth_correlation": float(ground_truth_corr), "ground_truth_p_value": float(ground_truth_p)}


def save_analysis_results(
    total_df: pd.DataFrame,
    output_dir: str | Path,
    network_stats: dict,
    failed_centralities: list[str],
    centralities: list[str] | None = None,
) -> None:
    correlations = save_ground_truth_correlations(total_df, output_dir, centralities=centralities)
    plot_correlation_bars(correlations, Path(output_dir) / "correlations_plot.png")

    result = {
        "failed_centralities": failed_centralities,
        "network_stats": network_stats,
        "ground_truth_analysis": correlations,
    }
    with open(Path(output_dir) / "analysis_results.json", "w") as handle:
        json.dump(result, handle, indent=2)
