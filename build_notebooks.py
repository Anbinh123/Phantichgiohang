"""Create structured Jupyter Notebooks (bai1/kt1_eda.ipynb, kt2.ipynb, kt3.ipynb) for Nhóm 23."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def make_notebook(cells: list[tuple[str, str]]) -> dict:
    nb_cells = []
    for cell_type, source in cells:
        lines = [line + "\n" for line in source.strip().splitlines()]
        if lines:
            lines[-1] = lines[-1].rstrip("\n")
        if cell_type == "markdown":
            nb_cells.append(
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": lines,
                }
            )
        else:
            nb_cells.append(
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": lines,
                }
            )
    return {
        "cells": nb_cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_nb(path: Path, cells: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(make_notebook(cells), ensure_ascii=False, indent=1), encoding="utf-8")
    print("Created:", path)


def main() -> None:
    # 1. bai1/kt1_eda.ipynb — Bài kiểm tra 1: EDA, Data Quality & Hold-out 80/20
    kt1_cells = [
        (
            "markdown",
            "# BÀI KIỂM TRA 1 – KHÁM PHÁ DỮ LIỆU (EDA) & TIỀN XỬ LÝ\n"
            "**Đề tài:** Phân tích giỏ hàng và phát hiện các sản phẩm thường được mua kèm\n\n"
            "**Nhóm 23 (CNTT K22H – ICTU):** Trần Văn Thực (`DTC235200734`), Nguyễn Đức An Bình (`DTC235200066`)\n\n"
            "**GVHD:** ThS. Nguyễn Tuấn Anh",
        ),
        (
            "code",
            "import sys\n"
            "from pathlib import Path\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n\n"
            "ROOT = Path.cwd().parent if Path.cwd().name == 'bai1' else Path.cwd()\n"
            "sys.path.insert(0, str(ROOT))\n\n"
            "from src.data_pipeline import (\n"
            "    load_raw_baskets,\n"
            "    prepare_dataset,\n"
            "    compute_item_frequencies,\n"
            "    compute_cooccurrence_matrix,\n"
            ")\n\n"
            "plt.rcParams['figure.dpi'] = 120\n"
            "raw_baskets = load_raw_baskets(ROOT / 'data' / 'groceries.csv')\n"
            "print(f'Tổng số giao dịch gốc: {len(raw_baskets):,}')\n"
            "print('5 giỏ hàng mẫu:', raw_baskets[:5])",
        ),
        (
            "markdown",
            "## 1. Khảo sát thống kê mô tả & Phân bố sản phẩm (EDA)",
        ),
        (
            "code",
            "bundle_raw = prepare_dataset(raw_baskets, min_basket_size=1, test_size=0.20, random_state=42)\n"
            "print('Thống kê dữ liệu gốc:')\n"
            "for k in ['n_raw_transactions', 'n_unique_items', 'avg_basket_size', 'std_basket_size', 'median_basket_size', 'max_basket_size', 'sparsity_pct', 'single_item_count']:\n"
            "    print(f'  {k}: {bundle_raw.stats[k]:.2f}' if isinstance(bundle_raw.stats[k], float) else f'  {k}: {bundle_raw.stats[k]}')\n\n"
            "freq_raw = compute_item_frequencies(bundle_raw.clean_baskets)\n"
            "freq_raw.head(15)",
        ),
        (
            "code",
            "top15 = freq_raw.head(15).iloc[::-1]\n"
            "sizes = np.array([len(b) for b in bundle_raw.clean_baskets])\n"
            "counts = pd.Series(sizes[sizes <= 15]).value_counts().sort_index()\n\n"
            "fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))\n"
            "axes[0].barh(top15['item'], top15['support_pct'], color='#2563EB')\n"
            "axes[0].set_title('a) Top 15 sản phẩm phổ biến nhất')\n"
            "axes[0].set_xlabel('Support (%)')\n\n"
            "axes[1].bar(counts.index, counts.values, color='#3B82F6')\n"
            "axes[1].axvline(np.mean(sizes), color='#DC2626', linestyle='--', label=f'TB = {np.mean(sizes):.2f} món')\n"
            "axes[1].set_title('b) Phân bố kích thước giỏ hàng (1-15 món)')\n"
            "axes[1].set_xlabel('Số sản phẩm trong giỏ')\n"
            "axes[1].set_ylabel('Số hóa đơn')\n"
            "axes[1].legend()\n"
            "plt.tight_layout()\n"
            "plt.show()",
        ),
        (
            "markdown",
            "## 2. Phân tích quan hệ đồng xuất hiện (Top 8 nhóm sản phẩm chính)",
        ),
        (
            "code",
            "cooc = compute_cooccurrence_matrix(bundle_raw.clean_baskets, top_n=8)\n"
            "fig, ax = plt.subplots(figsize=(7.5, 5.8))\n"
            "im = ax.imshow(cooc.values, cmap='Blues', vmin=0, vmax=12)\n"
            "ax.set_xticks(range(len(cooc.columns)))\n"
            "ax.set_yticks(range(len(cooc.columns)))\n"
            "ax.set_xticklabels(cooc.columns, rotation=35, ha='right')\n"
            "ax.set_yticklabels(cooc.columns)\n"
            "for i in range(len(cooc)):\n"
            "    for j in range(len(cooc)):\n"
            "        ax.text(j, i, f'{cooc.values[i, j]:.2f}%', ha='center', va='center', fontsize=8,\n"
            "                color='white' if cooc.values[i, j] > 7 else '#0F172A')\n"
            "fig.colorbar(im, ax=ax, label='Support (%)')\n"
            "ax.set_title('Ma trận đồng xuất hiện Top 8 sản phẩm')\n"
            "plt.tight_layout()\n"
            "plt.show()",
        ),
        (
            "markdown",
            "## 3. Tiền xử lý làm sạch, lọc giỏ < 2 món và chia Hold-out 80/20 chống rò rỉ",
        ),
        (
            "code",
            "bundle = prepare_dataset(raw_baskets, min_basket_size=2, test_size=0.20, random_state=42)\n"
            "summary_df = pd.DataFrame([\n"
            "    {'Giai đoạn': 'Dữ liệu gốc', 'Số giỏ': bundle_raw.stats['n_raw_transactions'], 'Độ dài TB': round(bundle_raw.stats['avg_basket_size'], 2), 'Độ dày ma trận (%)': round(100 - bundle_raw.stats['sparsity_pct'], 2)},\n"
            "    {'Giai đoạn': 'Sau lọc >= 2 món (Train 80%)', 'Số giỏ': bundle.stats['n_train'], 'Độ dài TB': round(float(np.mean([len(b) for b in bundle.train_baskets])), 2), 'Độ dày ma trận (%)': round(bundle.stats['train_density_pct'], 2)},\n"
            "    {'Giai đoạn': 'Sau lọc >= 2 món (Test 20%)', 'Số giỏ': bundle.stats['n_test'], 'Độ dài TB': round(float(np.mean([len(b) for b in bundle.test_baskets])), 2), 'Độ dày ma trận (%)': round(bundle.stats['test_density_pct'], 2)},\n"
            "])\n"
            "summary_df",
        ),
    ]
    write_nb(ROOT / "bai1" / "kt1_eda.ipynb", kt1_cells)

    # 2. kt2.ipynb — Bài kiểm tra 2: Cài đặt Apriori, ECLAT, FP-Growth, Benchmark & Đánh giá Test
    kt2_cells = [
        (
            "markdown",
            "# BÀI KIỂM TRA 2 – HUẤN LUYỆN, ĐỐI SÁNH THUẬT TOÁN & ĐÁNH GIÁ MÔ HÌNH\n"
            "**Đề tài:** Phân tích giỏ hàng và phát hiện các sản phẩm thường được mua kèm\n\n"
            "**Nhóm 23 (CNTT K22H – ICTU):** Trần Văn Thực (`DTC235200734`), Nguyễn Đức An Bình (`DTC235200066`)",
        ),
        (
            "code",
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "from src.data_pipeline import load_raw_baskets, prepare_dataset, compute_item_frequencies\n"
            "from src.algorithms import (\n"
            "    mine_with_metrics,\n"
            "    benchmark_algorithms,\n"
            "    evaluate_rules_on_test,\n"
            "    recommend_for_basket,\n"
            ")\n\n"
            "bundle = prepare_dataset(load_raw_baskets(), min_basket_size=2, test_size=0.20, random_state=42)\n"
            "freq_train = compute_item_frequencies(bundle.train_baskets)\n"
            "print(f'Train: {len(bundle.df_train):,} giỏ | Test: {len(bundle.df_test):,} giỏ | Số đặc trưng: {bundle.df_train.shape[1]}')",
        ),
        (
            "markdown",
            "## 1. Mô hình cơ sở (Most Popular) và đối sánh 3 thuật toán (Apriori, ECLAT, FP-Growth)",
        ),
        (
            "code",
            "top_item = freq_train.iloc[0]\n"
            "print(f\"Baseline (Most Popular): '{top_item['item']}' | Confidence = {top_item['support_pct']:.2f}% | Lift = 1.00\")\n\n"
            "results = []\n"
            "for algo in ['Apriori (Python)', 'ECLAT (Python)', 'FP-Growth (mlxtend)']:\n"
            "    res = mine_with_metrics(bundle.df_train, algorithm=algo, min_support=0.008, min_confidence=0.25, min_lift=1.30, max_len=None)\n"
            "    results.append({\n"
            "        'Thuật toán': algo,\n"
            "        'Số tập phổ biến': len(res.frequent_itemsets),\n"
            "        'Số luật': len(res.rules),\n"
            "        'Confidence TB (%)': round(float(res.rules['confidence'].mean() * 100), 2),\n"
            "        'Lift TB': round(float(res.rules['lift'].mean()), 2),\n"
            "        'Thời gian (s)': round(res.runtime_sec, 4),\n"
            "    })\n"
            "pd.DataFrame(results)",
        ),
        (
            "markdown",
            "## 2. Benchmark thời gian chạy & bộ nhớ theo ngưỡng min_support (0.05 -> 0.005)",
        ),
        (
            "code",
            "bench_df = benchmark_algorithms(bundle.df_train, support_thresholds=[0.05, 0.03, 0.02, 0.01, 0.008, 0.005], max_len=3)\n"
            "fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))\n"
            "sup_order = ['0.050', '0.030', '0.020', '0.010', '0.008', '0.005']\n"
            "bench_df['sup_str'] = bench_df['min_support'].map(lambda v: f'{v:.3f}')\n"
            "for algo in ['Apriori (Python)', 'ECLAT (Python)', 'FP-Growth (mlxtend)']:\n"
            "    sub = bench_df[bench_df['algorithm'] == algo].set_index('sup_str').loc[sup_order]\n"
            "    axes[0].plot(sup_order, sub['runtime_sec'], marker='o', label=algo)\n"
            "    axes[1].plot(sup_order, sub['peak_memory_mb'], marker='s', label=algo)\n"
            "axes[0].set_title('Thời gian thực thi (giây)')\n"
            "axes[0].set_xlabel('min_support')\n"
            "axes[0].legend()\n"
            "axes[1].set_title('Bộ nhớ đỉnh tracemalloc (MB)')\n"
            "axes[1].set_xlabel('min_support')\n"
            "axes[1].legend()\n"
            "plt.tight_layout()\n"
            "plt.show()\n"
            "bench_df.drop(columns=['sup_str'])",
        ),
        (
            "markdown",
            "## 3. Kiểm chứng trên tập Test 20% và Thử nghiệm gợi ý mua kèm",
        ),
        (
            "code",
            "fp_res = mine_with_metrics(bundle.df_train, algorithm='FP-Growth (mlxtend)', min_support=0.008, min_confidence=0.25, min_lift=1.30, max_len=None)\n"
            "eval_test = evaluate_rules_on_test(fp_res.rules, bundle.df_test)\n"
            "print(f\"Train Lift TB: {fp_res.rules['lift'].mean():.2f} -> Test Lift TB: {eval_test['test_lift'].mean():.2f}\")\n"
            "print(f\"Train Conf TB: {fp_res.rules['confidence'].mean()*100:.2f}% -> Test Conf TB: {eval_test['test_confidence'].mean()*100:.2f}%\")\n\n"
            "rec, base = recommend_for_basket(['root vegetables', 'tropical fruit'], fp_res.rules, freq_train, top_k=5)\n"
            "print('\\nGợi ý cho giỏ [root vegetables, tropical fruit]:')\n"
            "rec",
        ),
    ]
    write_nb(ROOT / "kt2.ipynb", kt2_cells)

    # 3. kt3.ipynb — Bài kiểm tra 3: 5-Fold CV Grid Search, Ablation Study & Pruning
    kt3_cells = [
        (
            "markdown",
            "# BÀI KIỂM TRA 3 – TỐI ƯU HÓA, CẢI TIẾN & SO SÁNH MÔ HÌNH\n"
            "**Đề tài:** Phân tích giỏ hàng và phát hiện các sản phẩm thường được mua kèm\n\n"
            "**Nhóm 23 (CNTT K22H – ICTU):** Trần Văn Thực (`DTC235200734`), Nguyễn Đức An Bình (`DTC235200066`)",
        ),
        (
            "code",
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "from src.data_pipeline import load_raw_baskets, prepare_dataset\n"
            "from src.algorithms import mine_with_metrics, evaluate_rules_on_test\n"
            "from src.part3_experiments import run_cv_grid_search, run_ablation_study, prune_redundant_rules\n\n"
            "bundle = prepare_dataset(load_raw_baskets(), min_basket_size=2, test_size=0.20, random_state=42)\n"
            "print(f'Tập phát triển (Train 80%): {len(bundle.train_baskets):,} giỏ | Tập kiểm tra (Test 20%): {len(bundle.test_baskets):,} giỏ')",
        ),
        (
            "markdown",
            "## 1. Tối ưu hóa siêu tham số bằng Grid Search trên 5-Fold CV (chỉ trên tập Train)",
        ),
        (
            "code",
            "grid_df = run_cv_grid_search(\n"
            "    bundle.train_baskets,\n"
            "    support_grid=[0.005, 0.008, 0.010, 0.015],\n"
            "    confidence_grid=[0.20, 0.25, 0.30],\n"
            "    lift_grid=[1.30, 1.50, 1.80],\n"
            "    max_len_grid=[2, 3, None],\n"
            "    n_splits=5,\n"
            ")\n"
            "print('Top 10 cấu hình trên 5-Fold CV:')\n"
            "grid_df.head(10)",
        ),
        (
            "code",
            "sub_grid = grid_df[(grid_df['min_confidence'] == 0.25) & (grid_df['max_len'] == 3)]\n"
            "fig, ax = plt.subplots(figsize=(8, 4.5))\n"
            "for l_val in sorted(sub_grid['min_lift'].unique()):\n"
            "    s = sub_grid[sub_grid['min_lift'] == l_val].sort_values('min_support')\n"
            "    ax.errorbar(s['min_support'], s['val_lift_mean'], yerr=s['val_lift_std'], marker='o', capsize=4, label=f'min_lift >= {l_val:.2f}')\n"
            "ax.set_title('Đường cong kiểm định chéo 5-Fold (Lift TB ± Std)')\n"
            "ax.set_xlabel('min_support')\n"
            "ax.set_ylabel('CV Lift (Mean ± Std)')\n"
            "ax.grid(True, linestyle='--', alpha=0.4)\n"
            "ax.legend()\n"
            "plt.tight_layout()\n"
            "plt.show()",
        ),
        (
            "markdown",
            "## 2. Nghiên cứu đóng góp từng bước cải tiến (Ablation Study: 5-Fold CV vs Test 20%)",
        ),
        (
            "code",
            "ablation_df = run_ablation_study(\n"
            "    raw_clean_baskets=bundle.clean_baskets,\n"
            "    filtered_train_baskets=bundle.train_baskets,\n"
            "    df_filtered_train=bundle.df_train,\n"
            "    df_filtered_test=bundle.df_test,\n"
            ")\n"
            "ablation_df",
        ),
        (
            "markdown",
            "## 3. Đánh giá mô hình cuối cùng (sau tối ưu & cắt tỉa luật dư thừa) trên tập Test giữ lại",
        ),
        (
            "code",
            "final_res = mine_with_metrics(bundle.df_train, algorithm='FP-Growth (mlxtend)', min_support=0.008, min_confidence=0.25, min_lift=1.50, max_len=3)\n"
            "pruned_rules = prune_redundant_rules(final_res.rules)\n"
            "eval_final = evaluate_rules_on_test(pruned_rules, bundle.df_test)\n"
            "print(f'Số luật trước Pruning: {len(final_res.rules)} -> Sau Pruning: {len(pruned_rules)}')\n"
            "print(f\"Train Lift TB: {pruned_rules['lift'].mean():.3f} | Test Lift TB: {eval_final['test_lift'].mean():.3f}\")\n"
            "print(f\"Train Conf TB: {pruned_rules['confidence'].mean()*100:.2f}% | Test Conf TB: {eval_final['test_confidence'].mean()*100:.2f}%\")\n"
            "eval_final.head(10)",
        ),
    ]
    write_nb(ROOT / "kt3.ipynb", kt3_cells)


if __name__ == "__main__":
    main()
