from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy import stats

matplotlib.use("Agg")
from matplotlib import pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Robustness checks for within-class partial correlations."
    )
    parser.add_argument("--output-root", default="output")
    parser.add_argument("--dpi", type=int, default=300)
    return parser.parse_args()


def safe_pearsonr(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    if x.size < 2 or y.size < 2:
        return math.nan, math.nan
    if np.allclose(x, x[0]) or np.allclose(y, y[0]):
        return math.nan, math.nan
    result = stats.pearsonr(x, y)
    return float(result.statistic), float(result.pvalue)


def residualize(target: np.ndarray, control: np.ndarray) -> np.ndarray:
    design = np.column_stack([np.ones(control.size), control])
    coefficients, _, _, _ = np.linalg.lstsq(design, target, rcond=None)
    return target - (design @ coefficients)


def partial_corr(x: np.ndarray, y: np.ndarray, control: np.ndarray) -> tuple[float, float]:
    residual_x = residualize(x, control)
    residual_y = residualize(y, control)
    return safe_pearsonr(residual_x, residual_y)


def markdown_table(df: pd.DataFrame, float_columns: set[str]) -> str:
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


def plot_robustness(summary_df: pd.DataFrame, output_path: Path, dpi: int) -> None:
    sorted_df = summary_df.sort_values("stopping_time", kind="stable")
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(
        sorted_df["stopping_time"],
        sorted_df["baseline_partial_r"],
        marker="o",
        label="Baseline partial | original_number",
    )
    ax.plot(
        sorted_df["stopping_time"],
        sorted_df["log_control_partial_r"],
        marker="o",
        label="Partial | log10(original_number)",
    )
    ax.plot(
        sorted_df["stopping_time"],
        sorted_df["spearman_partial_r"],
        marker="o",
        label="Rank-based partial",
    )
    ax.axhline(0, color="black", linestyle="--", linewidth=1.0)
    ax.set_title("Robustness of within-class partial correlation")
    ax.set_xlabel("Stopping time k")
    ax.set_ylabel("Partial correlation")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    output_root = REPO_ROOT / args.output_root
    data_dir = output_root / "data"
    figures_dir = output_root / "figures" / "summary"
    figures_dir.mkdir(parents=True, exist_ok=True)

    sample_b_df = pd.read_csv(
        data_dir / "Sample_B_data.csv",
        usecols=["original_number", "stopping_time", "peak_value", "peak_iteration"],
    )
    baseline_df = pd.read_csv(
        data_dir / "top_30_partial_correlation_summary.csv",
        usecols=[
            "class_rank",
            "stopping_time",
            "member_count",
            "partial_peak_corr",
            "partial_peak_corr_pvalue",
        ],
    ).rename(
        columns={
            "partial_peak_corr": "baseline_partial_r",
            "partial_peak_corr_pvalue": "baseline_partial_pvalue",
        }
    )

    records: list[dict[str, float | int | bool]] = []
    for row in baseline_df.itertuples(index=False):
        class_df = sample_b_df.loc[sample_b_df["stopping_time"] == row.stopping_time]
        original_number = class_df["original_number"].to_numpy(dtype=float)
        log_original_number = np.log10(original_number)
        peak_value = class_df["peak_value"].to_numpy(dtype=float)
        peak_iteration = class_df["peak_iteration"].to_numpy(dtype=float)

        log_partial_r, log_partial_p = partial_corr(
            peak_iteration, peak_value, log_original_number
        )

        rank_original = stats.rankdata(original_number)
        rank_peak_value = stats.rankdata(peak_value)
        rank_peak_iteration = stats.rankdata(peak_iteration)
        spearman_partial_r, spearman_partial_p = partial_corr(
            rank_peak_iteration,
            rank_peak_value,
            rank_original,
        )

        records.append(
            {
                "class_rank": int(row.class_rank),
                "stopping_time": int(row.stopping_time),
                "member_count": int(row.member_count),
                "baseline_partial_r": float(row.baseline_partial_r),
                "baseline_partial_pvalue": float(row.baseline_partial_pvalue),
                "log_control_partial_r": log_partial_r,
                "log_control_partial_pvalue": log_partial_p,
                "spearman_partial_r": spearman_partial_r,
                "spearman_partial_pvalue": spearman_partial_p,
                "log_minus_baseline": log_partial_r - float(row.baseline_partial_r),
                "spearman_minus_baseline": spearman_partial_r - float(row.baseline_partial_r),
            }
        )

    summary_df = pd.DataFrame.from_records(records).sort_values("class_rank", kind="stable")
    summary_df.to_csv(data_dir / "top_30_partial_correlation_robustness.csv", index=False)

    method_summary_df = pd.DataFrame(
        [
            {
                "method": "baseline_original_number",
                "mean_partial_r": float(summary_df["baseline_partial_r"].mean()),
                "fraction_positive": float((summary_df["baseline_partial_r"] > 0).mean()),
                "fraction_significant": float((summary_df["baseline_partial_pvalue"] < 0.05).mean()),
            },
            {
                "method": "log10_original_number",
                "mean_partial_r": float(summary_df["log_control_partial_r"].mean()),
                "fraction_positive": float((summary_df["log_control_partial_r"] > 0).mean()),
                "fraction_significant": float((summary_df["log_control_partial_pvalue"] < 0.05).mean()),
            },
            {
                "method": "spearman_rank_partial",
                "mean_partial_r": float(summary_df["spearman_partial_r"].mean()),
                "fraction_positive": float((summary_df["spearman_partial_r"] > 0).mean()),
                "fraction_significant": float((summary_df["spearman_partial_pvalue"] < 0.05).mean()),
            },
        ]
    )
    method_summary_df.to_csv(
        data_dir / "top_30_partial_correlation_robustness_summary.csv",
        index=False,
    )

    baseline_values = summary_df["baseline_partial_r"].to_numpy(dtype=float)
    log_values = summary_df["log_control_partial_r"].to_numpy(dtype=float)
    spearman_values = summary_df["spearman_partial_r"].to_numpy(dtype=float)
    log_paired_t = stats.ttest_rel(log_values, baseline_values, nan_policy="omit")
    spearman_paired_t = stats.ttest_rel(spearman_values, baseline_values, nan_policy="omit")

    plot_robustness(
        summary_df,
        figures_dir / "partial_correlation_robustness_by_class.png",
        args.dpi,
    )

    note = [
        "# Partial Correlation Robustness Checks",
        "",
        "## Summary",
        "",
        markdown_table(
            method_summary_df,
            {"mean_partial_r", "fraction_positive", "fraction_significant"},
        ),
        "",
        "## Paired t-tests against baseline partial correlation",
        "",
        f"- log10(original_number) control vs baseline: t = {float(log_paired_t.statistic):.6g}, p = {float(log_paired_t.pvalue):.6g}",
        f"- rank-based Spearman partial vs baseline: t = {float(spearman_paired_t.statistic):.6g}, p = {float(spearman_paired_t.pvalue):.6g}",
        "",
        "## Class-wise table",
        "",
        markdown_table(
            summary_df,
            {
                "baseline_partial_r",
                "baseline_partial_pvalue",
                "log_control_partial_r",
                "log_control_partial_pvalue",
                "spearman_partial_r",
                "spearman_partial_pvalue",
                "log_minus_baseline",
                "spearman_minus_baseline",
            },
        ),
        "",
        "Outputs:",
        "",
        "- `output/data/top_30_partial_correlation_robustness.csv`",
        "- `output/data/top_30_partial_correlation_robustness_summary.csv`",
        "- `output/figures/summary/partial_correlation_robustness_by_class.png`",
    ]
    (output_root / "collatz_partial_correlation_robustness.md").write_text(
        "\n".join(note),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
