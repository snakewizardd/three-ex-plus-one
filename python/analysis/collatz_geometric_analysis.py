from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import diptest
import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.stats import gaussian_kde
from sklearn.mixture import GaussianMixture
from tqdm import tqdm

PYTHON_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from functions.collatz import (
    collatz_2adic_profile,
    collatz_peak,
    collatz_stopping_time,
    collatz_values,
    two_adic_valuation,
)

matplotlib.use("Agg")
from matplotlib import pyplot as plt


sns.set_theme(style="whitegrid")
warnings.filterwarnings(
    "ignore",
    message="Could not find the number of physical cores",
)

SAMPLE_DATA_COLUMNS = [
    "original_number",
    "stopping_time",
    "peak_value",
    "peak_iteration",
    "trajectory",
    "two_adic_profile",
]


@dataclass(frozen=True)
class CachedAnalysis:
    original_number: int
    stopping_time: int
    peak_value: int
    peak_iteration: int
    trajectory_json: str
    two_adic_profile_json: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rigorous Collatz stopping-time equivalence class geometric analysis."
    )
    parser.add_argument("--seed", type=int, default=1993)
    parser.add_argument("--sample-a-count", type=int, default=10_000)
    parser.add_argument("--sample-b-count", type=int, default=100_000)
    parser.add_argument("--random-max", type=int, default=1_000_000)
    parser.add_argument("--sample-c-max", type=int, default=10_000)
    parser.add_argument("--top-classes", type=int, default=30)
    parser.add_argument("--interpolation-points", type=int, default=100)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--output-root", default="output")
    return parser.parse_args()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def json_list(values: list[int] | tuple[int, ...]) -> str:
    return json.dumps([int(value) for value in values], separators=(",", ":"))


def analyze_number(number: int, cache: dict[int, CachedAnalysis]) -> CachedAnalysis:
    number = int(number)
    if number in cache:
        return cache[number]

    trajectory = collatz_values(number)
    stopping_time = collatz_stopping_time(number)
    peak_value, peak_iteration = collatz_peak(number)
    two_adic_profile = collatz_2adic_profile(number)
    result = CachedAnalysis(
        original_number=number,
        stopping_time=stopping_time,
        peak_value=int(peak_value),
        peak_iteration=int(peak_iteration),
        trajectory_json=json_list(trajectory),
        two_adic_profile_json=json_list(two_adic_profile),
    )
    cache[number] = result
    return result


def random_odd_sample(count: int, max_value: int, rng: np.random.Generator) -> np.ndarray:
    odd_values = np.arange(1, max_value + 1, 2, dtype=np.int64)
    if count > odd_values.size:
        raise ValueError(
            f"Requested {count} odd integers, but only {odd_values.size} exist up to {max_value}."
        )
    return rng.choice(odd_values, size=count, replace=False)


def exhaustive_odd_sample(max_value: int) -> np.ndarray:
    return np.arange(1, max_value + 1, 2, dtype=np.int64)


def build_sample_dataframe(
    sample_name: str,
    numbers: np.ndarray,
    cache: dict[int, CachedAnalysis],
) -> pd.DataFrame:
    records: list[dict[str, int | str]] = []
    for number in tqdm(numbers.tolist(), desc=f"Analyzing {sample_name}", unit="n"):
        result = analyze_number(int(number), cache)
        records.append(
            {
                "original_number": result.original_number,
                "stopping_time": result.stopping_time,
                "peak_value": result.peak_value,
                "peak_iteration": result.peak_iteration,
                "trajectory": result.trajectory_json,
                "two_adic_profile": result.two_adic_profile_json,
            }
        )

    return pd.DataFrame.from_records(records, columns=SAMPLE_DATA_COLUMNS)


def sample_summary(sample_name: str, df: pd.DataFrame) -> dict[str, int | float | str]:
    return {
        "sample_name": sample_name,
        "member_count": int(len(df)),
        "original_min": int(df["original_number"].min()),
        "original_max": int(df["original_number"].max()),
        "stopping_time_min": int(df["stopping_time"].min()),
        "stopping_time_max": int(df["stopping_time"].max()),
        "stopping_time_mean": float(df["stopping_time"].mean()),
        "stopping_time_median": float(df["stopping_time"].median()),
        "stopping_time_std": float(df["stopping_time"].std(ddof=1)) if len(df) > 1 else 0.0,
        "peak_value_mean": float(df["peak_value"].mean()),
        "peak_value_median": float(df["peak_value"].median()),
        "peak_iteration_mean": float(df["peak_iteration"].mean()),
    }


def safe_pearsonr(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    if x.size < 2 or y.size < 2:
        return math.nan, math.nan
    if np.all(x == x[0]) or np.all(y == y[0]):
        return math.nan, math.nan
    result = stats.pearsonr(x, y)
    return float(result.statistic), float(result.pvalue)


def count_kde_modes(values: np.ndarray) -> int:
    if values.size < 5 or np.unique(values).size < 3:
        return 1
    if float(np.std(values)) == 0.0:
        return 1

    grid = np.linspace(float(values.min()), float(values.max()), 512)
    kde = gaussian_kde(values)
    density = kde(grid)
    peaks = np.where((density[1:-1] > density[:-2]) & (density[1:-1] > density[2:]))[0]
    return int(max(1, peaks.size))


def safe_diptest(values: np.ndarray) -> tuple[float, float]:
    if values.size < 4 or np.unique(values).size < 2:
        return math.nan, math.nan
    dip_stat, pvalue = diptest.diptest(values.astype(float))
    return float(dip_stat), float(pvalue)


def safe_spacing_chisquare(spacings: np.ndarray) -> tuple[float, float]:
    if spacings.size == 0:
        return math.nan, math.nan
    _, counts = np.unique(spacings, return_counts=True)
    if counts.size < 2:
        return math.nan, math.nan
    chi_result = stats.chisquare(counts)
    return float(chi_result.statistic), float(chi_result.pvalue)


def seed_two_adic_signature_mod4(number: int) -> int:
    return two_adic_valuation((3 * int(number)) + 1) % 4


def mode_or_nan(values: pd.Series | np.ndarray) -> float:
    if len(values) == 0:
        return math.nan
    series = pd.Series(values)
    modes = series.mode()
    if modes.empty:
        return math.nan
    return float(modes.iloc[0])


def compute_class_statistics(sample_name: str, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    class_records: list[dict[str, int | float | bool | str]] = []
    spacing_records: list[dict[str, int | float | str]] = []

    for stopping_time, class_df in tqdm(
        df.groupby("stopping_time", sort=True),
        desc=f"Class stats {sample_name}",
        unit="class",
    ):
        peak_values = class_df["peak_value"].to_numpy(dtype=float)
        peak_iterations = class_df["peak_iteration"].to_numpy(dtype=float)
        pearson_r, pearson_p = safe_pearsonr(peak_iterations, peak_values)

        sorted_peak_iterations = np.sort(peak_iterations.astype(int))
        spacings = np.diff(sorted_peak_iterations)
        spacing_chi2, spacing_chi2_p = safe_spacing_chisquare(spacings)
        dip_stat, dip_pvalue = safe_diptest(peak_iterations)
        kde_modes = count_kde_modes(peak_iterations)
        stratified = bool((not math.isnan(dip_pvalue) and dip_pvalue < 0.05) or kde_modes > 1)

        class_records.append(
            {
                "sample_name": sample_name,
                "stopping_time": int(stopping_time),
                "member_count": int(len(class_df)),
                "peak_value_mean": float(np.mean(peak_values)),
                "peak_value_median": float(np.median(peak_values)),
                "peak_value_std": float(np.std(peak_values, ddof=1)) if len(peak_values) > 1 else 0.0,
                "peak_iteration_mean": float(np.mean(peak_iterations)),
                "peak_iteration_median": float(np.median(peak_iterations)),
                "peak_iteration_std": float(np.std(peak_iterations, ddof=1))
                if len(peak_iterations) > 1
                else 0.0,
                "pearson_r": pearson_r,
                "pearson_pvalue": pearson_p,
                "inter_peak_spacing_mean": float(np.mean(spacings)) if spacings.size else math.nan,
                "inter_peak_spacing_median": float(np.median(spacings))
                if spacings.size
                else math.nan,
                "inter_peak_spacing_std": float(np.std(spacings, ddof=1))
                if spacings.size > 1
                else math.nan,
                "inter_peak_spacing_multiple_of_3_fraction": float(
                    np.mean(spacings % 3 == 0)
                )
                if spacings.size
                else math.nan,
                "inter_peak_spacing_chi2_stat": spacing_chi2,
                "inter_peak_spacing_chi2_pvalue": spacing_chi2_p,
                "dip_statistic": dip_stat,
                "dip_pvalue": dip_pvalue,
                "kde_mode_count": int(kde_modes),
                "stratified": stratified,
            }
        )

        for spacing in spacings.tolist():
            spacing_records.append(
                {
                    "sample_name": sample_name,
                    "stopping_time": int(stopping_time),
                    "spacing": int(spacing),
                    "is_multiple_of_3": bool((int(spacing) % 3) == 0),
                }
            )

    return (
        pd.DataFrame.from_records(class_records).sort_values(
            ["member_count", "stopping_time"], ascending=[False, True], kind="stable"
        ),
        pd.DataFrame.from_records(spacing_records),
    )


def parse_json_column(series: pd.Series) -> list[list[int]]:
    return [json.loads(value) for value in series.tolist()]


def interpolate_trajectory(values: list[int], output_points: int) -> np.ndarray:
    source_x = np.arange(len(values), dtype=float)
    target_x = np.linspace(0, len(values) - 1, output_points)
    return np.interp(target_x, source_x, np.asarray(values, dtype=float))


def is_power_of_two(value: int) -> bool:
    return value > 0 and (value & (value - 1)) == 0


def write_markdown_table(df: pd.DataFrame, float_columns: set[str] | None = None) -> str:
    float_columns = float_columns or set()
    headers = df.columns.tolist()
    lines = [
        "|" + "|".join(headers) + "|",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in df.itertuples(index=False):
        values: list[str] = []
        for header, value in zip(headers, row):
            if pd.isna(value):
                values.append("NA")
            elif header in float_columns:
                values.append(f"{float(value):.6g}")
            else:
                values.append(str(value))
        lines.append("|" + "|".join(values) + "|")
    return "\n".join(lines)


def plot_sample_stopping_time_distributions(
    sample_distributions: pd.DataFrame,
    output_path: Path,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    for sample_name, group_df in sample_distributions.groupby("sample_name", sort=False):
        ax.plot(
            group_df["stopping_time"],
            group_df["count"],
            marker="o",
            linewidth=1.2,
            markersize=3,
            label=sample_name,
        )
    ax.set_title("Stopping-time distributions by sample")
    ax.set_xlabel("Stopping time k")
    ax.set_ylabel("Count")
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def classify_subfamilies(class_df: pd.DataFrame, stratified: bool) -> tuple[np.ndarray, pd.DataFrame]:
    if not stratified or len(class_df) < 4 or class_df["peak_iteration"].nunique() < 2:
        labels = np.array(["A"] * len(class_df))
        summary = pd.DataFrame(
            [
                {
                    "subfamily": "A",
                    "member_count": int(len(class_df)),
                    "mean_peak_iteration": float(class_df["peak_iteration"].mean()),
                    "mean_peak_value": float(class_df["peak_value"].mean()),
                    "modal_seed_two_adic_signature_mod4": mode_or_nan(
                        [seed_two_adic_signature_mod4(value) for value in class_df["original_number"]]
                    ),
                }
            ]
        )
        return labels, summary

    gmm = GaussianMixture(n_components=2, random_state=1993, n_init=10)
    peak_iteration_matrix = class_df["peak_iteration"].to_numpy(dtype=float).reshape(-1, 1)
    raw_labels = gmm.fit_predict(peak_iteration_matrix)
    component_order = np.argsort(gmm.means_.ravel())
    label_map = {int(component_order[0]): "A", int(component_order[1]): "B"}
    labels = np.array([label_map[int(label)] for label in raw_labels])

    summary_records: list[dict[str, float | int | str]] = []
    for subfamily in ["A", "B"]:
        subset = class_df.loc[labels == subfamily]
        summary_records.append(
            {
                "subfamily": subfamily,
                "member_count": int(len(subset)),
                "mean_peak_iteration": float(subset["peak_iteration"].mean()),
                "mean_peak_value": float(subset["peak_value"].mean()),
                "modal_seed_two_adic_signature_mod4": mode_or_nan(
                    [seed_two_adic_signature_mod4(value) for value in subset["original_number"]]
                ),
            }
        )

    return labels, pd.DataFrame.from_records(summary_records)


def build_class_trajectory_df(
    class_df: pd.DataFrame,
    subfamily_labels: np.ndarray,
) -> tuple[pd.DataFrame, list[list[int]], list[list[int]]]:
    trajectory_lists = parse_json_column(class_df["trajectory"])
    two_adic_lists = parse_json_column(class_df["two_adic_profile"])

    records: list[dict[str, int | str]] = []
    for row, subfamily_label, trajectory, two_adic_profile in zip(
        class_df.itertuples(index=False),
        subfamily_labels.tolist(),
        trajectory_lists,
        two_adic_lists,
    ):
        for iteration_index, (value, valuation) in enumerate(zip(trajectory, two_adic_profile)):
            records.append(
                {
                    "original_number": int(row.original_number),
                    "stopping_time": int(row.stopping_time),
                    "peak_value": int(row.peak_value),
                    "peak_iteration": int(row.peak_iteration),
                    "subfamily": subfamily_label,
                    "iteration_index": int(iteration_index),
                    "value": int(value),
                    "state": "EVEN" if int(value) % 2 == 0 else "ODD",
                    "two_adic_valuation": int(valuation),
                }
            )

    trajectory_df = pd.DataFrame.from_records(records)
    return trajectory_df, trajectory_lists, two_adic_lists


def plot_full_overlay(
    trajectory_df: pd.DataFrame,
    stopping_time: int,
    member_count: int,
    output_path: Path,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = plt.cm.turbo(np.linspace(0, 1, max(member_count, 1)))
    for color, (_, member_df) in zip(
        colors,
        trajectory_df.groupby("original_number", sort=False),
    ):
        ax.plot(
            member_df["iteration_index"],
            member_df["value"],
            color=color,
            alpha=0.25,
            linewidth=0.8,
        )
    ax.set_title(f"Stopping Time Class k={stopping_time} — n={member_count} members")
    ax.set_xlabel("Iteration index")
    ax.set_ylabel("Value")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_zoomed_overlay(
    trajectory_df: pd.DataFrame,
    stopping_time: int,
    member_count: int,
    max_peak_value: int,
    output_path: Path,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 8))
    for _, member_df in trajectory_df.groupby("original_number", sort=False):
        ax.plot(
            member_df["iteration_index"],
            member_df["value"],
            color="black",
            alpha=0.2,
            linewidth=0.8,
        )

    ax.set_xlim(0, max(1, int(math.ceil(0.6 * stopping_time))))
    ax.set_ylim(0, max(1, int(math.ceil(0.3 * max_peak_value))))
    ax.set_title(f"Stopping Time Class k={stopping_time} — zoomed geometry")
    ax.set_xlabel("Iteration index")
    ax.set_ylabel("Value")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_peak_scatter(
    class_df: pd.DataFrame,
    stopping_time: int,
    output_path: Path,
    dpi: int,
) -> tuple[float, float]:
    plot_df = class_df.copy()
    plot_df["seed_two_adic_signature_mod4"] = plot_df["original_number"].map(
        seed_two_adic_signature_mod4
    )
    pearson_r, pearson_p = safe_pearsonr(
        plot_df["peak_iteration"].to_numpy(dtype=float),
        plot_df["peak_value"].to_numpy(dtype=float),
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    palette = sns.color_palette("viridis", n_colors=max(plot_df["seed_two_adic_signature_mod4"].nunique(), 1))
    sns.scatterplot(
        data=plot_df,
        x="peak_iteration",
        y="peak_value",
        hue="seed_two_adic_signature_mod4",
        palette=palette,
        alpha=0.7,
        s=25,
        ax=ax,
    )

    if plot_df["peak_iteration"].nunique() > 1 and plot_df["peak_value"].nunique() > 1:
        fit = np.polyfit(
            plot_df["peak_iteration"].to_numpy(dtype=float),
            plot_df["peak_value"].to_numpy(dtype=float),
            deg=1,
        )
        x_values = np.linspace(
            plot_df["peak_iteration"].min(),
            plot_df["peak_iteration"].max(),
            200,
        )
        ax.plot(x_values, fit[0] * x_values + fit[1], color="black", linewidth=1.5)

    ax.set_title(f"Peak scatter for stopping-time class k={stopping_time}")
    ax.set_xlabel("Peak iteration")
    ax.set_ylabel("Peak value")
    ax.text(
        0.02,
        0.98,
        f"Pearson r = {pearson_r:.4f}\np = {pearson_p:.4g}",
        transform=ax.transAxes,
        ha="left",
        va="top",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)
    return pearson_r, pearson_p


def plot_heatmap(
    class_df: pd.DataFrame,
    trajectories: list[list[int]],
    subfamily_labels: np.ndarray,
    stopping_time: int,
    output_path: Path,
    output_points: int,
    dpi: int,
) -> pd.DataFrame:
    interpolated_rows = np.vstack(
        [interpolate_trajectory(values, output_points) for values in trajectories]
    )
    heatmap_df = pd.DataFrame(interpolated_rows, columns=[f"p_{index:03d}" for index in range(output_points)])
    heatmap_df.insert(0, "subfamily", subfamily_labels.tolist())
    heatmap_df.insert(0, "original_number", class_df["original_number"].tolist())
    heatmap_df = heatmap_df.sort_values(
        ["subfamily", "original_number"], kind="stable"
    ).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        np.log10(heatmap_df.filter(like="p_").to_numpy(dtype=float) + 1.0),
        cmap="magma",
        ax=ax,
        cbar_kws={"label": "log10(value + 1)"},
    )
    ax.set_title(f"Interpolated trajectory heatmap for k={stopping_time}")
    ax.set_xlabel("Normalized trajectory position")
    ax.set_ylabel("Trajectory member")
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)
    return heatmap_df


def plot_two_adic_overlay(
    trajectory_df: pd.DataFrame,
    stopping_time: int,
    stratified: bool,
    output_path: Path,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 8))
    color_map = {"A": "#1b9e77", "B": "#d95f02"}
    for _, member_df in trajectory_df.groupby("original_number", sort=False):
        subfamily = member_df["subfamily"].iloc[0]
        color = color_map.get(subfamily, "#444444") if stratified else "#444444"
        ax.plot(
            member_df["iteration_index"],
            member_df["two_adic_valuation"],
            color=color,
            alpha=0.25,
            linewidth=0.8,
        )
    ax.set_title(f"2-adic valuation profiles for k={stopping_time}")
    ax.set_xlabel("Iteration index")
    ax.set_ylabel("v2(value)")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_peak_spacing(
    spacings: np.ndarray,
    stopping_time: int,
    output_path: Path,
    dpi: int,
) -> tuple[float, float]:
    chi2_stat, chi2_p = safe_spacing_chisquare(spacings)

    fig, ax = plt.subplots(figsize=(10, 7))
    if spacings.size:
        sns.histplot(spacings, bins=min(30, max(5, int(np.sqrt(spacings.size)))), stat="count", ax=ax, color="#4c72b0", alpha=0.7)
        if np.unique(spacings).size > 1:
            sns.kdeplot(spacings, ax=ax, color="black", linewidth=1.5)
        if int(np.max(spacings)) >= 3:
            for multiple in range(3, int(np.max(spacings)) + 1, 3):
                ax.axvline(multiple, color="red", alpha=0.15, linewidth=0.8)

    ax.set_title(f"Peak-iteration spacing distribution for k={stopping_time}")
    ax.set_xlabel("Spacing between sorted peak iterations")
    ax.set_ylabel("Count")
    ax.text(
        0.98,
        0.98,
        f"chi2 = {chi2_stat:.4g}\np = {chi2_p:.4g}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)
    return chi2_stat, chi2_p


def compute_convergence_nodes(trajectory_df: pd.DataFrame) -> pd.DataFrame:
    node_df = (
        trajectory_df.groupby(["iteration_index", "value"], as_index=False)
        .size()
        .rename(columns={"size": "frequency"})
    )
    return node_df[node_df["frequency"] > 1].sort_values(
        ["frequency", "iteration_index", "value"],
        ascending=[False, True, True],
        kind="stable",
    )


def plot_convergence_nodes(
    trajectory_df: pd.DataFrame,
    convergence_nodes_df: pd.DataFrame,
    stopping_time: int,
    output_path: Path,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 8))
    for _, member_df in trajectory_df.groupby("original_number", sort=False):
        ax.plot(
            member_df["iteration_index"],
            member_df["value"],
            color="black",
            alpha=0.12,
            linewidth=0.7,
        )
    if not convergence_nodes_df.empty:
        scatter = ax.scatter(
            convergence_nodes_df["iteration_index"],
            convergence_nodes_df["value"],
            s=20 + (convergence_nodes_df["frequency"] * 8),
            c=convergence_nodes_df["frequency"],
            cmap="plasma",
            alpha=0.8,
        )
        fig.colorbar(scatter, ax=ax, label="Shared trajectory count")

    ax.set_title(f"Convergence nodes for stopping-time class k={stopping_time}")
    ax.set_xlabel("Iteration index")
    ax.set_ylabel("Value")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def ks_profile_by_step(
    subfamily_labels: np.ndarray,
    two_adic_profiles: list[list[int]],
) -> tuple[pd.DataFrame, dict[str, float | int | bool]]:
    if len(np.unique(subfamily_labels)) < 2:
        empty_df = pd.DataFrame(
            columns=["iteration_index", "ks_statistic", "ks_pvalue", "significant"]
        )
        summary = {
            "ks_fisher_stat": math.nan,
            "ks_fisher_pvalue": math.nan,
            "ks_min_pvalue": math.nan,
            "ks_significant_step_count": 0,
            "ks_significant_profile": False,
        }
        return empty_df, summary

    step_records: list[dict[str, int | float | bool]] = []
    pvalues: list[float] = []
    trajectory_length = len(two_adic_profiles[0])

    for iteration_index in range(trajectory_length):
        subfamily_a = [
            profile[iteration_index]
            for profile, label in zip(two_adic_profiles, subfamily_labels.tolist())
            if label == "A"
        ]
        subfamily_b = [
            profile[iteration_index]
            for profile, label in zip(two_adic_profiles, subfamily_labels.tolist())
            if label == "B"
        ]
        if not subfamily_a or not subfamily_b:
            ks_statistic = math.nan
            ks_pvalue = math.nan
            significant = False
        else:
            ks_result = stats.ks_2samp(subfamily_a, subfamily_b)
            ks_statistic = float(ks_result.statistic)
            ks_pvalue = float(ks_result.pvalue)
            significant = bool(ks_pvalue < 0.05)
            if not math.isnan(ks_pvalue) and ks_pvalue > 0:
                pvalues.append(ks_pvalue)

        step_records.append(
            {
                "iteration_index": iteration_index,
                "ks_statistic": ks_statistic,
                "ks_pvalue": ks_pvalue,
                "significant": significant,
            }
        )

    ks_df = pd.DataFrame.from_records(step_records)
    if pvalues:
        fisher_stat, fisher_pvalue = stats.combine_pvalues(pvalues, method="fisher")
        fisher_stat = float(fisher_stat)
        fisher_pvalue = float(fisher_pvalue)
    else:
        fisher_stat = math.nan
        fisher_pvalue = math.nan

    summary = {
        "ks_fisher_stat": fisher_stat,
        "ks_fisher_pvalue": fisher_pvalue,
        "ks_min_pvalue": float(ks_df["ks_pvalue"].min()) if not ks_df.empty else math.nan,
        "ks_significant_step_count": int(ks_df["significant"].sum()) if not ks_df.empty else 0,
        "ks_significant_profile": bool((ks_df["significant"].sum() > 0) or (not math.isnan(fisher_pvalue) and fisher_pvalue < 0.05)),
    }
    return ks_df, summary


def plot_ks_profile(ks_df: pd.DataFrame, stopping_time: int, output_path: Path, dpi: int) -> None:
    if ks_df.empty:
        return
    plot_df = ks_df.copy()
    plot_df["neg_log10_p"] = -np.log10(plot_df["ks_pvalue"].clip(lower=1e-300))

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(plot_df["iteration_index"], plot_df["neg_log10_p"], color="#4c72b0", linewidth=1.4)
    ax.axhline(-math.log10(0.05), color="red", linestyle="--", linewidth=1.0)
    ax.set_title(f"Stepwise KS profile for 2-adic subfamilies in k={stopping_time}")
    ax.set_xlabel("Iteration index")
    ax.set_ylabel("-log10(KS p-value)")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_pearson_by_class(cross_class_df: pd.DataFrame, output_path: Path, dpi: int) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        cross_class_df["stopping_time"],
        cross_class_df["pearson_r"],
        marker="o",
        linewidth=1.2,
        color="#1b9e77",
    )
    ax.axhline(0, color="black", linewidth=1.0, linestyle="--")
    ax.set_title("Peak magnitude vs peak timing correlation by class")
    ax.set_xlabel("Stopping time k")
    ax.set_ylabel("Pearson r")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_cross_class_comparison(cross_class_df: pd.DataFrame, output_path: Path, dpi: int) -> None:
    sorted_df = cross_class_df.sort_values("stopping_time", kind="stable").reset_index(drop=True)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True)

    axes[0, 0].plot(sorted_df["stopping_time"], sorted_df["pearson_r"], marker="o")
    axes[0, 0].axhline(0, color="black", linestyle="--", linewidth=1.0)
    axes[0, 0].set_title("Pearson r")
    axes[0, 0].set_ylabel("r")

    axes[0, 1].plot(sorted_df["stopping_time"], sorted_df["stratified_indicator"], marker="o")
    axes[0, 1].set_title("Stratified indicator")
    axes[0, 1].set_ylabel("0 / 1")

    axes[1, 0].plot(sorted_df["stopping_time"], sorted_df["convergence_node_count"], marker="o")
    axes[1, 0].set_title("Convergence node count")
    axes[1, 0].set_xlabel("Stopping time k")
    axes[1, 0].set_ylabel("Count")

    axes[1, 1].plot(sorted_df["stopping_time"], sorted_df["inter_peak_spacing_mean"], marker="o")
    axes[1, 1].set_title("Mean inter-peak spacing")
    axes[1, 1].set_xlabel("Stopping time k")
    axes[1, 1].set_ylabel("Mean spacing")

    for axis in axes.ravel():
        axis.grid(alpha=0.2)

    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def run_top_class_suite(
    sample_b_df: pd.DataFrame,
    top_classes_df: pd.DataFrame,
    output_data_dir: Path,
    output_figures_dir: Path,
    interpolation_points: int,
    dpi: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cross_class_records: list[dict[str, int | float | bool]] = []
    subfamily_records: list[dict[str, int | float | str]] = []
    ks_records: list[dict[str, int | float | bool]] = []
    convergence_summary_records: list[dict[str, int | float]] = []

    for rank, top_row in enumerate(top_classes_df.itertuples(index=False), start=1):
        stopping_time = int(top_row.stopping_time)
        class_data_dir = ensure_dir(output_data_dir / "classes" / f"k_{stopping_time}")
        class_figures_dir = ensure_dir(output_figures_dir / f"k_{stopping_time}")

        class_df = (
            sample_b_df.loc[sample_b_df["stopping_time"] == stopping_time]
            .sort_values(["peak_iteration", "original_number"], kind="stable")
            .reset_index(drop=True)
        )
        member_count = int(len(class_df))
        stratified_flag = bool(top_row.stratified)

        subfamily_labels, subfamily_summary_df = classify_subfamilies(class_df, stratified_flag)
        class_df = class_df.copy()
        class_df.insert(0, "subfamily", subfamily_labels.tolist())
        class_df.insert(0, "class_rank", rank)
        class_df.to_csv(class_data_dir / "class_members.csv", index=False)

        subfamily_summary_df.insert(0, "stopping_time", stopping_time)
        subfamily_summary_df.insert(0, "class_rank", rank)
        subfamily_summary_df.to_csv(class_data_dir / "subfamily_summary.csv", index=False)
        subfamily_records.extend(subfamily_summary_df.to_dict(orient="records"))

        trajectory_df, trajectories, two_adic_profiles = build_class_trajectory_df(
            class_df, subfamily_labels
        )
        trajectory_df.to_csv(class_data_dir / "trajectory_long.csv", index=False)

        peak_scatter_df = class_df[
            ["class_rank", "subfamily", "original_number", "stopping_time", "peak_value", "peak_iteration"]
        ].copy()
        peak_scatter_df["seed_two_adic_signature_mod4"] = peak_scatter_df["original_number"].map(
            seed_two_adic_signature_mod4
        )
        peak_scatter_df.to_csv(class_data_dir / "peak_scatter.csv", index=False)

        heatmap_df = plot_heatmap(
            class_df,
            trajectories,
            subfamily_labels,
            stopping_time,
            class_figures_dir / "plot_D_trajectory_shape_heatmap.png",
            interpolation_points,
            dpi,
        )
        heatmap_df.to_csv(class_data_dir / "trajectory_shape_heatmap.csv", index=False)

        plot_full_overlay(
            trajectory_df,
            stopping_time,
            member_count,
            class_figures_dir / "plot_A_full_trajectory_overlay_colored.png",
            dpi,
        )
        plot_zoomed_overlay(
            trajectory_df,
            stopping_time,
            member_count,
            int(class_df["peak_value"].max()),
            class_figures_dir / "plot_B_zoomed_trajectory_overlay_black.png",
            dpi,
        )
        pearson_r, pearson_p = plot_peak_scatter(
            peak_scatter_df,
            stopping_time,
            class_figures_dir / "plot_C_peak_scatter.png",
            dpi,
        )
        plot_two_adic_overlay(
            trajectory_df,
            stopping_time,
            stratified_flag,
            class_figures_dir / "plot_E_two_adic_profile_overlay.png",
            dpi,
        )

        spacings = np.diff(np.sort(class_df["peak_iteration"].to_numpy(dtype=int)))
        pd.DataFrame({"spacing": spacings}).to_csv(
            class_data_dir / "inter_peak_spacing.csv", index=False
        )
        spacing_chi2, spacing_chi2_p = plot_peak_spacing(
            spacings,
            stopping_time,
            class_figures_dir / "plot_F_peak_spacing_distribution.png",
            dpi,
        )

        convergence_nodes_df = compute_convergence_nodes(trajectory_df)
        convergence_nodes_df.to_csv(class_data_dir / "convergence_nodes.csv", index=False)
        plot_convergence_nodes(
            trajectory_df,
            convergence_nodes_df,
            stopping_time,
            class_figures_dir / "plot_G_convergence_nodes.png",
            dpi,
        )

        ks_df, ks_summary = ks_profile_by_step(subfamily_labels, two_adic_profiles)
        ks_df.insert(0, "stopping_time", stopping_time)
        ks_df.insert(0, "class_rank", rank)
        ks_df.to_csv(class_data_dir / "two_adic_ks_by_step.csv", index=False)
        if not ks_df.empty:
            plot_ks_profile(
                ks_df,
                stopping_time,
                class_figures_dir / "plot_H_two_adic_ks_profile.png",
                dpi,
            )
        ks_records.extend(ks_df.to_dict(orient="records"))

        power_of_two_fraction = float(
            np.mean([is_power_of_two(int(value)) for value in convergence_nodes_df["value"]])
        ) if not convergence_nodes_df.empty else math.nan
        dominant_residue_mod6 = mode_or_nan(
            (convergence_nodes_df["value"] % 6).to_numpy(dtype=int)
            if not convergence_nodes_df.empty
            else np.array([])
        )
        dominant_iteration_index = mode_or_nan(
            convergence_nodes_df["iteration_index"].to_numpy(dtype=int)
            if not convergence_nodes_df.empty
            else np.array([])
        )

        convergence_summary = {
            "class_rank": rank,
            "stopping_time": stopping_time,
            "convergence_node_count": int(len(convergence_nodes_df)),
            "mean_convergence_frequency": float(convergence_nodes_df["frequency"].mean())
            if not convergence_nodes_df.empty
            else math.nan,
            "max_convergence_frequency": float(convergence_nodes_df["frequency"].max())
            if not convergence_nodes_df.empty
            else math.nan,
            "dominant_iteration_index": dominant_iteration_index,
            "power_of_two_fraction": power_of_two_fraction,
            "dominant_residue_mod6": dominant_residue_mod6,
        }
        convergence_summary_records.append(convergence_summary)

        cross_class_records.append(
            {
                "class_rank": rank,
                "stopping_time": stopping_time,
                "member_count": member_count,
                "peak_value_mean": float(class_df["peak_value"].mean()),
                "peak_iteration_mean": float(class_df["peak_iteration"].mean()),
                "pearson_r": pearson_r,
                "pearson_pvalue": pearson_p,
                "inter_peak_spacing_mean": float(np.mean(spacings)) if spacings.size else math.nan,
                "inter_peak_spacing_median": float(np.median(spacings)) if spacings.size else math.nan,
                "inter_peak_spacing_multiple_of_3_fraction": float(np.mean(spacings % 3 == 0))
                if spacings.size
                else math.nan,
                "inter_peak_spacing_chi2_stat": spacing_chi2,
                "inter_peak_spacing_chi2_pvalue": spacing_chi2_p,
                "dip_statistic": float(top_row.dip_statistic),
                "dip_pvalue": float(top_row.dip_pvalue),
                "kde_mode_count": int(top_row.kde_mode_count),
                "stratified_indicator": int(stratified_flag),
                "convergence_node_count": convergence_summary["convergence_node_count"],
                "dominant_convergence_iteration_index": convergence_summary["dominant_iteration_index"],
                "convergence_power_of_two_fraction": convergence_summary["power_of_two_fraction"],
                "convergence_dominant_residue_mod6": convergence_summary["dominant_residue_mod6"],
                "ks_fisher_stat": float(ks_summary["ks_fisher_stat"]),
                "ks_fisher_pvalue": float(ks_summary["ks_fisher_pvalue"]),
                "ks_min_pvalue": float(ks_summary["ks_min_pvalue"]),
                "ks_significant_step_count": int(ks_summary["ks_significant_step_count"]),
                "ks_significant_profile": bool(ks_summary["ks_significant_profile"]),
            }
        )

    return (
        pd.DataFrame.from_records(cross_class_records),
        pd.DataFrame.from_records(subfamily_records),
        pd.DataFrame.from_records(ks_records),
        pd.DataFrame.from_records(convergence_summary_records),
    )


def build_final_report(
    sample_summary_df: pd.DataFrame,
    top_classes_table_df: pd.DataFrame,
    cross_class_df: pd.DataFrame,
    subfamily_df: pd.DataFrame,
    convergence_summary_df: pd.DataFrame,
    assumptions: list[str],
) -> str:
    pearson_values = cross_class_df["pearson_r"].dropna().to_numpy(dtype=float)
    pearson_ttest = stats.ttest_1samp(pearson_values, popmean=0.0, nan_policy="omit")
    pearson_ttest_stat = float(pearson_ttest.statistic)
    pearson_ttest_p = float(pearson_ttest.pvalue)
    negative_fraction = float(np.mean(pearson_values < 0)) if pearson_values.size else math.nan

    stratified_fraction = float(cross_class_df["stratified_indicator"].mean())
    stratified_count = int(cross_class_df["stratified_indicator"].sum())
    total_classes = int(len(cross_class_df))

    trend_records = []
    for metric in [
        "pearson_r",
        "stratified_indicator",
        "convergence_node_count",
        "inter_peak_spacing_mean",
    ]:
        valid_df = cross_class_df[["stopping_time", metric]].dropna()
        if len(valid_df) >= 2 and valid_df[metric].nunique() > 1:
            spearman = stats.spearmanr(valid_df["stopping_time"], valid_df[metric])
            trend_records.append(
                {
                    "metric": metric,
                    "spearman_rho": float(spearman.statistic),
                    "spearman_pvalue": float(spearman.pvalue),
                }
            )
        else:
            trend_records.append(
                {"metric": metric, "spearman_rho": math.nan, "spearman_pvalue": math.nan}
            )
    trend_df = pd.DataFrame.from_records(trend_records)

    significant_ks_classes_df = (
        cross_class_df.loc[cross_class_df["ks_significant_profile"] == True]
        .sort_values("stopping_time", kind="stable")
        .reset_index(drop=True)
    )

    report_lines = [
        "# Collatz Findings",
        "",
        "## Assumptions",
        "",
    ]
    report_lines.extend([f"- {assumption}" for assumption in assumptions])
    report_lines.extend(
        [
            "",
            "## 1. Sample statistics",
            "",
            write_markdown_table(
                sample_summary_df,
                {
                    "stopping_time_mean",
                    "stopping_time_median",
                    "stopping_time_std",
                    "peak_value_mean",
                    "peak_value_median",
                    "peak_iteration_mean",
                },
            ),
            "",
            "## 2. Top 30 equivalence classes table",
            "",
            write_markdown_table(
                top_classes_table_df,
                {
                    "peak_value_mean",
                    "pearson_r",
                    "pearson_pvalue",
                    "dip_pvalue",
                },
            ),
            "",
            "## 3. Quantitative tests",
            "",
            f"- One-sample t-test on class-wise Pearson r against 0: t = {pearson_ttest_stat:.6g}, p = {pearson_ttest_p:.6g}",
            f"- Fraction of top classes with negative Pearson r: {negative_fraction:.6g}",
            f"- Stratified classes among top 30: {stratified_count}/{total_classes} = {stratified_fraction:.6g}",
            "",
            write_markdown_table(
                cross_class_df[
                    [
                        "class_rank",
                        "stopping_time",
                        "pearson_r",
                        "pearson_pvalue",
                        "inter_peak_spacing_mean",
                        "inter_peak_spacing_multiple_of_3_fraction",
                        "inter_peak_spacing_chi2_stat",
                        "inter_peak_spacing_chi2_pvalue",
                        "dip_pvalue",
                        "stratified_indicator",
                        "convergence_node_count",
                        "ks_fisher_pvalue",
                    ]
                ].copy(),
                {
                    "pearson_r",
                    "pearson_pvalue",
                    "inter_peak_spacing_mean",
                    "inter_peak_spacing_multiple_of_3_fraction",
                    "inter_peak_spacing_chi2_stat",
                    "inter_peak_spacing_chi2_pvalue",
                    "dip_pvalue",
                    "ks_fisher_pvalue",
                },
            ),
            "",
            "Cross-class trend statistics:",
            "",
            write_markdown_table(trend_df, {"spearman_rho", "spearman_pvalue"}),
            "",
            "## 4. 2-adic formalization results",
            "",
            write_markdown_table(
                significant_ks_classes_df[
                    [
                        "class_rank",
                        "stopping_time",
                        "ks_fisher_stat",
                        "ks_fisher_pvalue",
                        "ks_min_pvalue",
                        "ks_significant_step_count",
                    ]
                ].copy(),
                {
                    "ks_fisher_stat",
                    "ks_fisher_pvalue",
                    "ks_min_pvalue",
                },
            )
            if not significant_ks_classes_df.empty
            else "No class met the 2-adic profile significance criterion.",
            "",
            "Subfamily characterization:",
            "",
            write_markdown_table(
                subfamily_df,
                {
                    "mean_peak_iteration",
                    "mean_peak_value",
                    "modal_seed_two_adic_signature_mod4",
                },
            )
            if not subfamily_df.empty
            else "No stratified classes were identified.",
            "",
            "Convergence node summary:",
            "",
            write_markdown_table(
                convergence_summary_df,
                {
                    "mean_convergence_frequency",
                    "max_convergence_frequency",
                    "dominant_iteration_index",
                    "power_of_two_fraction",
                    "dominant_residue_mod6",
                },
            ),
            "",
            "## 5. Formal claims",
            "",
            f"1. Claim 1: Within stopping-time equivalence classes of the Collatz map, peak trajectory magnitude and peak iteration index are inversely correlated across the modal equivalence classes. In this run, the class-wise Pearson coefficients produced t = {pearson_ttest_stat:.6g}, p = {pearson_ttest_p:.6g}, with negative correlation in {negative_fraction:.6g} of the top classes.",
            f"2. Claim 2: A statistically significant fraction of modal stopping-time equivalence classes exhibit internal stratification into distinct subfamilies. In this run, {stratified_count} of {total_classes} top classes were stratified by the dip/KDE criterion, and {int(significant_ks_classes_df.shape[0])} classes also showed significant 2-adic profile separation.",
            "",
            "## 6. Figure references",
            "",
            "- `output/figures/summary/sample_stopping_time_distributions.png`",
            "- `output/figures/summary/pearson_r_by_class.png`",
            "- `output/figures/summary/cross_class_comparison.png`",
            "- `output/figures/k_<k>/plot_A_full_trajectory_overlay_colored.png`",
            "- `output/figures/k_<k>/plot_B_zoomed_trajectory_overlay_black.png`",
            "- `output/figures/k_<k>/plot_C_peak_scatter.png`",
            "- `output/figures/k_<k>/plot_D_trajectory_shape_heatmap.png`",
            "- `output/figures/k_<k>/plot_E_two_adic_profile_overlay.png`",
            "- `output/figures/k_<k>/plot_F_peak_spacing_distribution.png`",
            "- `output/figures/k_<k>/plot_G_convergence_nodes.png`",
            "- `output/figures/k_<k>/plot_H_two_adic_ks_profile.png`",
        ]
    )
    return "\n".join(report_lines)


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    rng = np.random.default_rng(args.seed)

    output_root = ensure_dir(REPO_ROOT / args.output_root)
    output_data_dir = ensure_dir(output_root / "data")
    output_figures_dir = ensure_dir(output_root / "figures")
    summary_figures_dir = ensure_dir(output_figures_dir / "summary")

    cache: dict[int, CachedAnalysis] = {}
    assumptions = [
        "Sample A and Sample B random ranges were interpreted as odd integers drawn without replacement from 1 to 1,000,000 because the prompt omitted explicit upper bounds.",
        "Plot C colors use v2(3n+1) mod 4 as the first nontrivial 2-adic seed signature, because v2(n)=0 for every odd starting integer.",
        "Top-30 equivalence-class analysis is centered on Sample B, the 100,000-member odd random sample, because the prompt emphasizes that scale as the main result.",
        "Trajectory heatmaps use log10(value + 1) for display while the saved CSV retains the raw interpolated values.",
    ]

    samples = {
        "Sample A": random_odd_sample(args.sample_a_count, args.random_max, rng),
        "Sample B": random_odd_sample(args.sample_b_count, args.random_max, rng),
        "Sample C": exhaustive_odd_sample(args.sample_c_max),
    }

    sample_dataframes: dict[str, pd.DataFrame] = {}
    sample_summary_records: list[dict[str, int | float | str]] = []
    sample_distribution_records: list[dict[str, int | str]] = []

    for sample_name, numbers in samples.items():
        df = build_sample_dataframe(sample_name, numbers, cache)
        sample_dataframes[sample_name] = df
        file_stem = sample_name.replace(" ", "_")
        df.to_csv(output_data_dir / f"{file_stem}_data.csv", index=False)

        sample_summary_records.append(sample_summary(sample_name, df))
        stopping_distribution = (
            df.groupby("stopping_time", as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values("stopping_time", kind="stable")
        )
        stopping_distribution.insert(0, "sample_name", sample_name)
        sample_distribution_records.extend(stopping_distribution.to_dict(orient="records"))

        class_stats_df, spacing_records_df = compute_class_statistics(sample_name, df)
        class_stats_df.to_csv(output_data_dir / f"{file_stem}_class_stats.csv", index=False)
        spacing_records_df.to_csv(
            output_data_dir / f"{file_stem}_inter_peak_spacings.csv",
            index=False,
        )

    sample_summary_df = pd.DataFrame.from_records(sample_summary_records)
    sample_summary_df.to_csv(output_data_dir / "sample_summary.csv", index=False)

    sample_distribution_df = pd.DataFrame.from_records(sample_distribution_records)
    sample_distribution_df.to_csv(
        output_data_dir / "sample_stopping_time_distribution.csv",
        index=False,
    )
    plot_sample_stopping_time_distributions(
        sample_distribution_df,
        summary_figures_dir / "sample_stopping_time_distributions.png",
        args.dpi,
    )

    sample_b_df = sample_dataframes["Sample B"]
    sample_b_class_stats_df = pd.read_csv(output_data_dir / "Sample_B_class_stats.csv")
    top_classes_df = (
        sample_b_class_stats_df.sort_values(
            ["member_count", "stopping_time"], ascending=[False, True], kind="stable"
        )
        .head(args.top_classes)
        .reset_index(drop=True)
    )
    top_classes_df.to_csv(output_data_dir / "sample_B_top_30_classes.csv", index=False)

    cross_class_df, subfamily_df, ks_df, convergence_summary_df = run_top_class_suite(
        sample_b_df,
        top_classes_df,
        output_data_dir,
        output_figures_dir,
        args.interpolation_points,
        args.dpi,
    )
    cross_class_df.to_csv(output_data_dir / "top_30_cross_class_summary.csv", index=False)
    subfamily_df.to_csv(output_data_dir / "top_30_subfamily_summary.csv", index=False)
    ks_df.to_csv(output_data_dir / "top_30_ks_by_step.csv", index=False)
    convergence_summary_df.to_csv(
        output_data_dir / "top_30_convergence_summary.csv", index=False
    )

    plot_pearson_by_class(
        cross_class_df.sort_values("stopping_time", kind="stable"),
        summary_figures_dir / "pearson_r_by_class.png",
        args.dpi,
    )
    plot_cross_class_comparison(
        cross_class_df.sort_values("stopping_time", kind="stable"),
        summary_figures_dir / "cross_class_comparison.png",
        args.dpi,
    )

    top_classes_report_df = cross_class_df[
        [
            "class_rank",
            "stopping_time",
            "member_count",
            "peak_value_mean",
            "pearson_r",
            "pearson_pvalue",
            "dip_pvalue",
        ]
    ].copy()
    report_text = build_final_report(
        sample_summary_df,
        top_classes_report_df,
        cross_class_df,
        subfamily_df,
        convergence_summary_df,
        assumptions,
    )
    (output_root / "collatz_findings.md").write_text(report_text, encoding="utf-8")


if __name__ == "__main__":
    main()
