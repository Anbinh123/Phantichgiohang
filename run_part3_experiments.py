"""Reproducible script generating all Part 2 & Part 3 tables and figures for Nhóm 23."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.algorithms import (
    benchmark_algorithms,
    evaluate_rules_on_test,
    mine_with_metrics,
)
from src.data_pipeline import load_raw_baskets, prepare_dataset
from src.part3_experiments import (
    prune_redundant_rules,
    run_ablation_study,
    run_cv_grid_search,
)

OUT_DIR = Path(__file__).resolve().parent / "outputs"
FIG_DIR = OUT_DIR / "figures"
TAB_DIR = OUT_DIR / "tables"


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TAB_DIR.mkdir(parents=True, exist_ok=True)

    raw_baskets = load_raw_baskets()
    bundle = prepare_dataset(raw_baskets, min_basket_size=2, test_size=0.20, random_state=42)

    # 1. Benchmark Apriori vs ECLAT vs FP-Growth across min_support
    print("Running algorithm benchmark (0.05 -> 0.005)...")
    bench_df = benchmark_algorithms(
        bundle.df_train,
        support_thresholds=[0.05, 0.03, 0.02, 0.01, 0.008, 0.005],
        max_len=3,
    )
    bench_df.to_csv(TAB_DIR / "benchmark_algorithms.csv", index=False, encoding="utf-8-sig")

    # 2. 5-Fold Cross-Validation Grid Search inside train_baskets ONLY (never touching test)
    print("Running 5-Fold CV Grid Search on train_baskets...")
    grid_df = run_cv_grid_search(
        bundle.train_baskets,
        support_grid=[0.005, 0.008, 0.010, 0.015],
        confidence_grid=[0.20, 0.25, 0.30],
        lift_grid=[1.30, 1.50, 1.80],
        max_len_grid=[2, 3, None],
        n_splits=5,
    )
    grid_df.to_csv(TAB_DIR / "cv_grid_search.csv", index=False, encoding="utf-8-sig")

    # 3. Unified Ablation Study (Baseline -> Raw -> Filtered -> Tuned -> Redundant Pruning)
    print("Running unified Ablation Study (5-Fold CV + Hold-out Test)...")
    ablation_df = run_ablation_study(
        raw_clean_baskets=bundle.clean_baskets,
        filtered_train_baskets=bundle.train_baskets,
        df_filtered_train=bundle.df_train,
        df_filtered_test=bundle.df_test,
    )
    ablation_df.to_csv(TAB_DIR / "ablation_study.csv", index=False, encoding="utf-8-sig")

    # 4. Final selected model rules & Hold-out test verification
    final_res = mine_with_metrics(
        bundle.df_train,
        algorithm="FP-Growth (mlxtend)",
        min_support=0.008,
        min_confidence=0.25,
        min_lift=1.50,
        max_len=3,
    )
    pruned_rules = prune_redundant_rules(final_res.rules)
    eval_final_test = evaluate_rules_on_test(pruned_rules, bundle.df_test)
    eval_final_test.to_csv(TAB_DIR / "final_rules_test_eval.csv", index=False, encoding="utf-8-sig")

    # --- Generate Figures ---
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
    plt.rcParams["axes.unicode_minus"] = False

    # Fig A: Benchmark Runtime & Memory curves
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    sup_order = ["0.050", "0.030", "0.020", "0.010", "0.008", "0.005"]
    bench_plot = bench_df.copy()
    bench_plot["sup_str"] = bench_plot["min_support"].map(lambda v: f"{v:.3f}")
    for algo, color, marker in [
        ("Apriori (Python)", "#DC2626", "o"),
        ("ECLAT (Python)", "#F59E0B", "^"),
        ("FP-Growth (mlxtend)", "#2563EB", "s"),
    ]:
        sub = bench_plot[bench_plot["algorithm"] == algo].set_index("sup_str").loc[sup_order]
        axes[0].plot(sup_order, sub["runtime_sec"], label=algo, color=color, marker=marker, linewidth=2)
        axes[1].plot(sup_order, sub["peak_memory_mb"], label=algo, color=color, marker=marker, linewidth=2)

    axes[0].set_title("a) Thời gian thực thi khi giảm dần min_support")
    axes[0].set_xlabel("Ngưỡng hỗ trợ tối thiểu (min_support)")
    axes[0].set_ylabel("Thời gian thực thi (giây)")
    axes[0].grid(True, linestyle="--", alpha=0.4)
    axes[0].legend()

    axes[1].set_title("b) Bộ nhớ đỉnh (tracemalloc) theo min_support")
    axes[1].set_xlabel("Ngưỡng hỗ trợ tối thiểu (min_support)")
    axes[1].set_ylabel("Bộ nhớ đỉnh (MB)")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    axes[1].legend()

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_benchmark_runtime_memory.png", dpi=180)
    plt.close(fig)

    # Fig B: Ablation Study (5-Fold CV Mean ± Std vs Hold-out Test)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    labels = ["Cơ sở\n(Popular)", "FP-Growth\ndữ liệu thô", "+ Lọc giỏ\n>= 2 món", "+ Tối ưu\nLift>=1.5, len<=3", "+ Cắt tỉa\nluật dư thừa"]
    x = np.arange(len(labels))
    w = 0.36

    axes[0].bar(x - w / 2, ablation_df["cv_lift_mean"], w, yerr=ablation_df["cv_lift_std"], capsize=4, label="5-Fold CV (Train)", color="#3B82F6")
    axes[0].bar(x + w / 2, ablation_df["test_lift"], w, label="Tập kiểm tra (Test 20%)", color="#10B981")
    axes[0].axhline(1.30, color="#DC2626", linestyle="--", linewidth=1.3, label="Ngưỡng mục tiêu Lift >= 1.30")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, fontsize=8.5)
    axes[0].set_ylabel("Chỉ số Lift trung bình")
    axes[0].set_title("a) Cải thiện Lift qua từng bước (Ablation Study)")
    axes[0].legend(fontsize=8)
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)

    axes[1].bar(x - w / 2, ablation_df["cv_conf_mean"], w, yerr=ablation_df["cv_conf_std"], capsize=4, label="5-Fold CV (Train)", color="#3B82F6")
    axes[1].bar(x + w / 2, ablation_df["test_conf"], w, label="Tập kiểm tra (Test 20%)", color="#10B981")
    axes[1].axhline(25.0, color="#DC2626", linestyle="--", linewidth=1.3, label="Ngưỡng mục tiêu Conf >= 25%")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, fontsize=8.5)
    axes[1].set_ylabel("Độ tin cậy Confidence TB (%)")
    axes[1].set_title("b) Cải thiện Confidence (%) qua từng bước")
    axes[1].legend(fontsize=8)
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_ablation_cv_vs_test.png", dpi=180)
    plt.close(fig)

    # Fig C: 5-Fold CV Validation Curve across min_lift & min_support (at min_conf=0.25, max_len=3)
    sub_grid = grid_df[(grid_df["min_confidence"] == 0.25) & (grid_df["max_len"] == 3)].copy()
    pivot_lift = sub_grid.pivot(index="min_support", columns="min_lift", values="val_lift_mean")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for lift_col in pivot_lift.columns:
        sub_err = sub_grid[sub_grid["min_lift"] == lift_col].sort_values("min_support")
        ax.errorbar(
            sub_err["min_support"],
            sub_err["val_lift_mean"],
            yerr=sub_err["val_lift_std"],
            marker="o",
            capsize=4,
            linewidth=2,
            label=f"min_lift >= {lift_col:.2f}",
        )
    ax.set_title("Đường cong kiểm định chéo 5-Fold: Lift TB theo min_support và min_lift")
    ax.set_xlabel("Ngưỡng hỗ trợ tối thiểu (min_support)")
    ax.set_ylabel("Lift trung bình trên tập kiểm định (Mean ± Std)")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_cv_validation_curve.png", dpi=180)
    plt.close(fig)

    print("\n=== BENCHMARK SUMMARY ===")
    print(bench_df.to_string(index=False))
    print("\n=== TOP 10 CV GRID SEARCH CONFIGS ===")
    print(grid_df.head(10).to_string(index=False))
    print("\n=== ABLATION STUDY ===")
    print(ablation_df.to_string(index=False))
    print(
        f"\n=== FINAL MODEL (min_support=0.008, min_conf=0.25, min_lift=1.50, max_len=3, pruned) ==="
        f"\nRules before pruning: {len(final_res.rules)}, after pruning: {len(pruned_rules)}"
        f"\nTrain Lift TB: {pruned_rules['lift'].mean():.3f}, Train Conf TB: {pruned_rules['confidence'].mean()*100:.2f}%"
        f"\nTest Lift TB: {eval_final_test['test_lift'].mean():.3f}, Test Conf TB: {eval_final_test['test_confidence'].mean()*100:.2f}%"
    )


if __name__ == "__main__":
    main()
