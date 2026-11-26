"""Generate all high-DPI Vietnamese figures and extract ICTU logo for Nhóm 23 PDF report."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from src.algorithms import mine_with_metrics
from src.data_pipeline import (
    compute_cooccurrence_matrix,
    compute_item_frequencies,
    load_raw_baskets,
    prepare_dataset,
)
from src.part3_experiments import prune_redundant_rules

ROOT = Path(__file__).resolve().parent
FIG_DIR = ROOT / "outputs" / "figures"


def extract_ictu_logo() -> None:
    """Extract ICTU emblem image from page 1 of original Nhóm 23.pdf."""
    import pymupdf

    doc = pymupdf.open(ROOT / "Nhóm 23.pdf")
    page = doc[0]
    imgs = page.get_images(full=True)
    if imgs:
        xref = imgs[0][0]
        base = doc.extract_image(xref)
        out = FIG_DIR / f"ictu_logo.{base['ext']}"
        out.write_bytes(base["image"])
        print("Extracted ICTU logo:", out.name)
    doc.close()


def draw_flowchart_box(ax, x, y, w, h, title, subtitle="", facecolor="#EFF6FF", edgecolor="#1D4ED8"):
    box = patches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=1.5,
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.65, title, ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0F172A")
        ax.text(x + w / 2, y + h * 0.30, subtitle, ha="center", va="center", fontsize=8, color="#334155")
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0F172A")


def draw_fig_1_1_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(11, 2.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 2.5)
    ax.axis("off")

    steps = [
        ("1. Phát biểu bài toán", "ARM / FIM không giám sát\nLift >= 1.30, Conf >= 25%", "#EFF6FF", "#1D4ED8"),
        ("2. Khảo sát & Tiền xử lý", "9.835 giỏ -> 7.676 giỏ\nLoại trùng & giỏ < 2 món", "#F0FDF4", "#15803D"),
        ("3. Chia Hold-out 80/20", "Train: 6.140 | Test: 1.536\nFit encoder chỉ trên Train", "#FEFCE8", "#A16207"),
        ("4. Huấn luyện & CV 5-Fold", "Apriori, ECLAT, FP-Growth\nGrid Search & Ablation", "#FFF7ED", "#C2410C"),
        ("5. Đánh giá & Demo", "Test độc lập (266 luật)\nỨng dụng Streamlit POS", "#F5F3FF", "#6D28D9"),
    ]
    w, h = 1.9, 1.35
    y = 0.55
    xs = [0.2 + i * 2.15 for i in range(5)]
    for i, (x, (t, sub, fc, ec)) in enumerate(zip(xs, steps)):
        draw_flowchart_box(ax, x, y, w, h, t, sub, fc, ec)
        if i < 4:
            ax.annotate(
                "",
                xy=(xs[i + 1] - 0.03, y + h / 2),
                xytext=(x + w + 0.03, y + h / 2),
                arrowprops=dict(arrowstyle="->", lw=1.8, color="#475569"),
            )

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_1_1_pipeline.png", dpi=180)
    plt.close(fig)


def draw_fig_2_1_cv_workflow() -> None:
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    draw_flowchart_box(ax, 3.3, 3.65, 4.4, 0.72, "Dữ liệu Groceries đã làm sạch (7.676 giỏ >= 2 món)", "Loại bỏ trùng trong giỏ & 2.159 giỏ 1 món", "#F8FAFC", "#334155")
    ax.annotate("", xy=(5.5, 3.35), xytext=(5.5, 3.63), arrowprops=dict(arrowstyle="->", lw=1.6, color="#334155"))

    draw_flowchart_box(ax, 3.6, 2.65, 3.8, 0.68, "Chia Hold-out 80/20 (random_state = 42)", "Ngăn ngừa rò rỉ dữ liệu ngay từ đầu", "#EFF6FF", "#1D4ED8")

    # Left branch: Train 80%
    ax.annotate("", xy=(2.7, 2.28), xytext=(4.5, 2.63), arrowprops=dict(arrowstyle="->", lw=1.6, color="#1D4ED8"))
    draw_flowchart_box(ax, 0.4, 1.45, 4.6, 0.80, "Tập huấn luyện Train (80% = 6.140 giỏ)", "TransactionEncoder.fit() chỉ chạy trên Train của từng Fold", "#EFF6FF", "#2563EB")

    # Right branch: Test 20%
    ax.annotate("", xy=(8.3, 2.28), xytext=(6.5, 2.63), arrowprops=dict(arrowstyle="->", lw=1.6, color="#DC2626"))
    draw_flowchart_box(ax, 6.2, 1.45, 4.4, 0.80, "Tập kiểm tra giữ lại Test (20% = 1.536 giỏ)", "NIÊM PHONG — Không dùng để chọn siêu tham số", "#FEF2F2", "#DC2626")

    # Inside CV loop
    ax.annotate("", xy=(2.7, 1.12), xytext=(2.7, 1.43), arrowprops=dict(arrowstyle="->", lw=1.6, color="#15803D"))
    draw_flowchart_box(
        ax,
        0.4,
        0.22,
        4.6,
        0.88,
        "Kiểm định chéo 5-Fold CV & Grid Search",
        "4 Fold Train -> Khai phá -> 1 Fold Val (Mean ± Std)\nChọn cấu hình tối ưu + Hậu xử lý Pruning",
        "#F0FDF4",
        "#15803D",
    )

    # Final evaluation arrow
    ax.annotate("", xy=(6.18, 0.65), xytext=(5.02, 0.65), arrowprops=dict(arrowstyle="->", lw=1.8, color="#6D28D9"))
    ax.annotate("", xy=(8.4, 1.10), xytext=(8.4, 1.43), arrowprops=dict(arrowstyle="->", lw=1.6, color="#DC2626", ls="--"))
    draw_flowchart_box(
        ax,
        6.2,
        0.22,
        4.4,
        0.88,
        "Huấn luyện lại trên 100% Train & Kiểm chứng Test",
        "Đánh giá một lần duy nhất (266 luật cuối)\nSo sánh CV Lift (1,82 ± 0,07) vs Test Lift (1,78)",
        "#F5F3FF",
        "#6D28D9",
    )

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_2_1_cv_workflow.png", dpi=180)
    plt.close(fig)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
    plt.rcParams["axes.unicode_minus"] = False

    extract_ictu_logo()
    draw_fig_1_1_pipeline()
    draw_fig_2_1_cv_workflow()

    raw_baskets = load_raw_baskets()
    bundle = prepare_dataset(raw_baskets, min_basket_size=2, test_size=0.20, random_state=42)

    # Fig 3.1: EDA Top 15 + Basket Size Distribution
    freq_raw = compute_item_frequencies(bundle.clean_baskets)
    top15 = freq_raw.head(15).iloc[::-1]
    sizes = np.array([len(b) for b in bundle.clean_baskets], dtype=int)
    counts = pd.Series(sizes[sizes <= 15]).value_counts().sort_index()

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    axes[0].barh(top15["item"], top15["support_pct"], color="#2563EB")
    for i, v in enumerate(top15["support_pct"]):
        axes[0].text(v + 0.3, i, f"{v:.2f}%", va="center", fontsize=8)
    axes[0].set_xlim(0, 30)
    axes[0].set_xlabel("Tỷ lệ xuất hiện - Support (%)")
    axes[0].set_title("a) Top 15 sản phẩm phổ biến nhất (9.835 hóa đơn)")
    axes[0].grid(axis="x", linestyle="--", alpha=0.4)

    axes[1].bar(counts.index, counts.values, color="#3B82F6")
    axes[1].axvline(np.mean(sizes), color="#DC2626", linestyle="--", linewidth=1.6, label=f"Trung bình = {np.mean(sizes):.2f} món")
    axes[1].set_xticks(range(1, 16))
    axes[1].set_xlabel("Số lượng mặt hàng trong giỏ (Basket Size)")
    axes[1].set_ylabel("Số lượng hóa đơn")
    axes[1].set_title("b) Phân bố kích thước giỏ hàng (1–15 món)")
    axes[1].legend()
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_3_1_eda.png", dpi=180)
    plt.close(fig)

    # Fig 3.2: Co-occurrence Heatmap Top 8
    cooc = compute_cooccurrence_matrix(bundle.clean_baskets, top_n=8)
    fig, ax = plt.subplots(figsize=(8.2, 6.4))
    im = ax.imshow(cooc.values, cmap="Blues", vmin=0, vmax=12)
    labels = [c if len(c) <= 13 else c[:11] + ".." for c in cooc.columns]
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8.5)
    ax.set_yticklabels(labels, fontsize=8.5)
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = cooc.values[i, j]
            txt_color = "white" if val > 7 else "#0F172A"
            ax.text(j, i, f"{val:.2f}%", ha="center", va="center", color=txt_color, fontsize=7.5)
    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("Tỷ lệ đồng xuất hiện - Support (%)")
    ax.set_title("Ma trận tỷ lệ mua cùng nhau giữa Top 8 sản phẩm chính")
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_3_2_cooccurrence.png", dpi=180)
    plt.close(fig)

    # Fig 3.3: Scatter Support vs Confidence colored by Lift (266 final rules)
    res_opt = mine_with_metrics(
        bundle.df_train,
        algorithm="FP-Growth (mlxtend)",
        min_support=0.008,
        min_confidence=0.25,
        min_lift=1.50,
        max_len=3,
    )
    pruned_rules = prune_redundant_rules(res_opt.rules)

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    sc = ax.scatter(
        pruned_rules["support"] * 100.0,
        pruned_rules["confidence"] * 100.0,
        c=pruned_rules["lift"],
        cmap="viridis",
        s=pruned_rules["lift"] * 28,
        alpha=0.85,
        edgecolors="#1E293B",
        linewidth=0.5,
    )
    ax.axhline(25.0, color="#DC2626", linestyle="--", linewidth=1.3, label="Ngưỡng Confidence = 25%")
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Chỉ số Lift")
    ax.set_xlabel("Độ hỗ trợ - Support (%)")
    ax.set_ylabel("Độ tin cậy - Confidence (%)")
    ax.set_title(f"Phân bố Support, Confidence và Lift của {len(pruned_rules)} luật kết hợp cuối cùng")
    ax.legend(loc="lower right")
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_3_3_rules_scatter.png", dpi=180)
    plt.close(fig)

    # Fig 3.7: Network Graph Top 15 pruned rules (clean layout without overlapping labels)
    sub = pruned_rules.head(15)
    g = nx.DiGraph()
    for _, row in sub.iterrows():
        u = ", ".join(sorted(row["antecedents"]))
        v = ", ".join(sorted(row["consequents"]))
        g.add_edge(u, v, lift=float(row["lift"]))

    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    pos = nx.kamada_kawai_layout(g)
    degs = [g.degree(n) for n in g.nodes()]
    edge_colors = [g[u][v]["lift"] for u, v in g.edges()]
    nx.draw_networkx_nodes(
        g,
        pos,
        ax=ax,
        node_size=[260 + d * 90 for d in degs],
        node_color="#DBEAFE",
        edgecolors="#1E3A8A",
        linewidths=1.5,
    )
    nx.draw_networkx_edges(
        g,
        pos,
        ax=ax,
        edge_color=edge_colors,
        edge_cmap=plt.cm.viridis,
        width=2.2,
        arrows=True,
        arrowsize=15,
        connectionstyle="arc3,rad=0.08",
    )
    nx.draw_networkx_labels(
        g,
        pos,
        ax=ax,
        font_size=8.2,
        font_weight="bold",
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="#CBD5E1", boxstyle="round,pad=0.2"),
    )
    sm = plt.cm.ScalarMappable(
        cmap=plt.cm.viridis,
        norm=matplotlib.colors.Normalize(vmin=min(edge_colors), vmax=max(edge_colors)),
    )
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.8)
    cbar.set_label("Chỉ số Lift")
    ax.set_title("Mạng lưới 15 luật kết hợp mạnh nhất theo Lift (Mô hình FP-Growth sau tối ưu)")
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_3_7_network.png", dpi=180)
    plt.close(fig)

    print("All report figures generated successfully!")


if __name__ == "__main__":
    main()
