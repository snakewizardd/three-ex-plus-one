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
        description="Partial-correlation follow-up for top Collatz stopping-time classes."
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


def partial_correlation_controlling_original_number(
    peak_iteration: np.ndarray,
    peak_value: np.ndarray,
    original_number: np.ndarray,
) -> tuple[float, float]:
    residual_peak_iteration = residualize(peak_iteration, original_number)
    residual_peak_value = residualize(peak_value, original_number)
    return safe_pearsonr(residual_peak_iteration, residual_peak_value)


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


def plot_raw_vs_partial(summary_df: pd.DataFrame, output_path: Path, dpi: int) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    sorted_df = summary_df.sort_values("stopping_time", kind="stable")
    ax.plot(sorted_df["stopping_time"], sorted_df["raw_peak_corr"], marker="o", label="Raw")
    ax.plot(
        sorted_df["stopping_time"],
        sorted_df["partial_peak_corr"],
        marker="o",
        label="Partial | original_number",
    )
    ax.axhline(0, color="black", linestyle="--", linewidth=1.0)
    ax.set_title("Within-class raw vs partial correlation")
    ax.set_xlabel("Stopping time k")
    ax.set_ylabel("Correlation")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_reduction(summary_df: pd.DataFrame, output_path: Path, dpi: int) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    sorted_df = summary_df.sort_values("stopping_time", kind="stable")
    ax.bar(
        sorted_df["stopping_time"].astype(str),
        sorted_df["raw_to_partial_drop"],
        color="#4c72b0",
    )
    ax.set_title("Drop in correlation after controlling for original_number")
    ax.set_xlabel("Stopping time k")
    ax.set_ylabel("Raw r - partial r")
    ax.tick_params(axis="x", labelrotation=90)
    ax.grid(alpha=0.2, axis="y")
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
    top_class_df = pd.read_csv(
        data_dir / "top_30_cross_class_summary.csv",
        usecols=["class_rank", "stopping_time", "member_count", "pearson_r", "pearson_pvalue"],
    )

    records: list[dict[str, float | int | bool]] = []
    for row in top_class_df.itertuples(index=False):
        class_df = sample_b_df.loc[sample_b_df["stopping_time"] == row.stopping_time].copy()
        original_number = class_df["original_number"].to_numpy(dtype=float)
        peak_value = class_df["peak_value"].to_numpy(dtype=float)
        peak_iteration = class_df["peak_iteration"].to_numpy(dtype=float)

        raw_r, raw_p = safe_pearsonr(peak_iteration, peak_value)
        number_to_peak_value_r, number_to_peak_value_p = safe_pearsonr(original_number, peak_value)
        number_to_peak_iteration_r, number_to_peak_iteration_p = safe_pearsonr(
            original_number, peak_iteration
        )
        partial_r, partial_p = partial_correlation_controlling_original_number(
            peak_iteration, peak_value, original_number
        )

        records.append(
            {
                "class_rank": int(row.class_rank),
                "stopping_time": int(row.stopping_time),
                "member_count": int(row.member_count),
                "raw_peak_corr": raw_r,
                "raw_peak_corr_pvalue": raw_p,
                "corr_original_to_peak_value": number_to_peak_value_r,
                "corr_original_to_peak_value_pvalue": number_to_peak_value_p,
                "corr_original_to_peak_iteration": number_to_peak_iteration_r,
                "corr_original_to_peak_iteration_pvalue": number_to_peak_iteration_p,
                "partial_peak_corr": partial_r,
                "partial_peak_corr_pvalue": partial_p,
                "raw_to_partial_drop": raw_r - partial_r,
                "structural_retention_ratio": (
                    partial_r / raw_r
                    if (not math.isnan(raw_r)) and raw_r != 0.0
                    else math.nan
                ),
                "partial_positive": bool(partial_r > 0),
                "partial_significant": bool((not math.isnan(partial_p)) and partial_p < 0.05),
            }
        )

    summary_df = pd.DataFrame.from_records(records).sort_values(
        "class_rank", kind="stable"
    )
    summary_path = data_dir / "top_30_partial_correlation_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    valid_mask = summary_df["raw_peak_corr"].notna() & summary_df["partial_peak_corr"].notna()
    raw_values = summary_df.loc[valid_mask, "raw_peak_corr"].to_numpy(dtype=float)
    partial_values = summary_df.loc[valid_mask, "partial_peak_corr"].to_numpy(dtype=float)
    raw_ttest = stats.ttest_1samp(raw_values, popmean=0.0, nan_policy="omit")
    partial_ttest = stats.ttest_1samp(partial_values, popmean=0.0, nan_policy="omit")
    paired_ttest = stats.ttest_rel(raw_values, partial_values, nan_policy="omit")

    plot_raw_vs_partial(
        summary_df,
        figures_dir / "partial_correlation_raw_vs_partial.png",
        args.dpi,
    )
    plot_reduction(
        summary_df,
        figures_dir / "partial_correlation_drop_by_class.png",
        args.dpi,
    )

    note = [
        "# Partial Correlation Follow-up",
        "",
        "## Summary",
        "",
        f"- Mean raw within-class correlation: {summary_df['raw_peak_corr'].mean():.6g}",
        f"- Mean partial correlation controlling for original_number: {summary_df['partial_peak_corr'].mean():.6g}",
        f"- Mean drop after control: {summary_df['raw_to_partial_drop'].mean():.6g}",
        f"- Classes with positive partial correlation: {int(summary_df['partial_positive'].sum())}/{len(summary_df)}",
        f"- Classes with significant partial correlation: {int(summary_df['partial_significant'].sum())}/{len(summary_df)}",
        f"- One-sample t-test on raw correlations vs 0: t = {float(raw_ttest.statistic):.6g}, p = {float(raw_ttest.pvalue):.6g}",
        f"- One-sample t-test on partial correlations vs 0: t = {float(partial_ttest.statistic):.6g}, p = {float(partial_ttest.pvalue):.6g}",
        f"- Paired t-test raw vs partial: t = {float(paired_ttest.statistic):.6g}, p = {float(paired_ttest.pvalue):.6g}",
        "",
        "## Class-wise table",
        "",
        markdown_table(
            summary_df,
            {
                "raw_peak_corr",
                "raw_peak_corr_pvalue",
                "corr_original_to_peak_value",
                "corr_original_to_peak_value_pvalue",
                "corr_original_to_peak_iteration",
                "corr_original_to_peak_iteration_pvalue",
                "partial_peak_corr",
                "partial_peak_corr_pvalue",
                "raw_to_partial_drop",
                "structural_retention_ratio",
            },
        ),
        "",
        "## Interpretation",
        "",
        "The size-driven component is operationalized here as the amount of raw within-class correlation removed when both peak_value and peak_iteration are residualized against original_number.",
        "The structural component is operationalized as the remaining partial correlation after that control.",
        "",
        "Outputs:",
        "",
        "- `output/data/top_30_partial_correlation_summary.csv`",
        "- `output/figures/summary/partial_correlation_raw_vs_partial.png`",
        "- `output/figures/summary/partial_correlation_drop_by_class.png`",
    ]
    (output_root / "collatz_partial_correlation_findings.md").write_text(
        "\n".join(note),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
