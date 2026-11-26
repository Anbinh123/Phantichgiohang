"""Interactive Plotly visualizations for Market Basket Analysis."""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_top_items(freq_df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Horizontal bar chart of top frequent items by support percentage."""
    sub = freq_df.head(top_n).iloc[::-1]
    fig = px.bar(
        sub,
        x="support_pct",
        y="item",
        orientation="h",
        text=sub["support_pct"].map(lambda v: f"{v:.2f}%"),
        color="support_pct",
        color_continuous_scale="Blues",
        labels={"support_pct": "Tỷ lệ xuất hiện - Support (%)", "item": "Sản phẩm"},
        title=f"Top {top_n} sản phẩm phổ biến nhất",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(coloraxis_showscale=False, height=450, margin=dict(l=10, r=40, t=50, b=30))
    return fig


def plot_basket_size_distribution(baskets: list[list[str]], max_display: int = 15) -> go.Figure:
    """Histogram of basket sizes with mean vertical reference line."""
    sizes = np.array([len(b) for b in baskets], dtype=int)
    avg_size = float(np.mean(sizes)) if len(sizes) else 0.0
    clipped = sizes[sizes <= max_display]
    counts = pd.Series(clipped).value_counts().sort_index()

    fig = go.Figure(
        data=[
            go.Bar(
                x=counts.index.astype(str),
                y=counts.values,
                marker_color="#2563EB",
                name="Số hóa đơn",
            )
        ]
    )
    fig.add_vline(
        x=avg_size - 1 if len(counts) else 0,
        line_dash="dash",
        line_color="#DC2626",
        annotation_text=f"Trung bình = {avg_size:.2f} món",
        annotation_position="top right",
    )
    fig.update_layout(
        title=f"Phân bố kích thước giỏ hàng (1–{max_display} món)",
        xaxis_title="Số lượng mặt hàng trong giỏ (Basket Size)",
        yaxis_title="Số lượng hóa đơn",
        height=450,
        margin=dict(l=10, r=20, t=50, b=30),
    )
    return fig


def plot_cooccurrence_heatmap(cooc_df: pd.DataFrame) -> go.Figure:
    """Heatmap of pairwise co-occurrence percentages among top product groups."""
    fig = px.imshow(
        cooc_df.round(2),
        text_auto=".2f",
        color_continuous_scale="Blues",
        labels=dict(color="Support (%)"),
        title="Ma trận tỷ lệ mua cùng nhau giữa các nhóm sản phẩm chính (%)",
    )
    fig.update_layout(height=480, margin=dict(l=10, r=10, t=50, b=30))
    return fig


def plot_rules_scatter(rules: pd.DataFrame, min_confidence: float) -> go.Figure:
    """Scatter plot of Support (%) vs Confidence (%) colored by Lift."""
    df_plot = pd.DataFrame(
        {
            "rule": rules["antecedents"].apply(lambda s: ", ".join(sorted(s)))
            + " → "
            + rules["consequents"].apply(lambda s: ", ".join(sorted(s))),
            "support_pct": rules["support"] * 100.0,
            "confidence_pct": rules["confidence"] * 100.0,
            "lift": rules["lift"],
        }
    )
    fig = px.scatter(
        df_plot,
        x="support_pct",
        y="confidence_pct",
        color="lift",
        size="lift",
        hover_name="rule",
        color_continuous_scale="Viridis",
        labels={
            "support_pct": "Độ hỗ trợ - Support (%)",
            "confidence_pct": "Độ tin cậy - Confidence (%)",
            "lift": "Chỉ số Lift",
        },
        title=f"Phân bố Support, Confidence và Lift của {len(df_plot)} luật kết hợp",
    )
    fig.add_hline(
        y=min_confidence * 100.0,
        line_dash="dash",
        line_color="#EF4444",
        annotation_text=f"Ngưỡng Confidence = {min_confidence * 100:.0f}%",
    )
    fig.update_layout(height=460, margin=dict(l=10, r=10, t=50, b=30))
    return fig


def plot_rules_network(
    rules: pd.DataFrame,
    max_rules: int = 30,
    focus_item: str | None = None,
) -> go.Figure:
    """Interactive network graph of top association rules using NetworkX + Plotly."""
    sub = rules.copy()
    if focus_item:
        sub = sub[
            sub["antecedents"].apply(lambda s: focus_item in s)
            | sub["consequents"].apply(lambda s: focus_item in s)
        ]
    sub = sub.head(max_rules)

    graph = nx.DiGraph()
    for _, row in sub.iterrows():
        ant_label = ", ".join(sorted(row["antecedents"]))
        cons_label = ", ".join(sorted(row["consequents"]))
        graph.add_node(ant_label)
        graph.add_node(cons_label)
        graph.add_edge(
            ant_label,
            cons_label,
            lift=float(row["lift"]),
            confidence=float(row["confidence"]),
            support=float(row["support"]),
        )

    if graph.number_of_nodes() == 0:
        return go.Figure()

    pos = nx.spring_layout(graph, seed=42, k=2.1, iterations=150)

    edge_traces: list[go.Scatter] = []
    mid_x: list[float] = []
    mid_y: list[float] = []
    mid_text: list[str] = []
    annotations: list[dict[str, object]] = []

    for u, v, data in graph.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        width = max(1.2, min(5.5, data["lift"] * 1.3))
        color = "#10B981" if data["lift"] >= 2.0 else "#3B82F6"
        edge_traces.append(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode="lines",
                line=dict(width=width, color=color),
                opacity=0.6,
                hoverinfo="none",
                showlegend=False,
            )
        )
        # Directional arrow near target node
        annotations.append(
            dict(
                ax=x0 + 0.15 * (x1 - x0),
                ay=y0 + 0.15 * (y1 - y0),
                x=x0 + 0.85 * (x1 - x0),
                y=y0 + 0.85 * (y1 - y0),
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=2,
                arrowsize=1.1,
                arrowwidth=1.4,
                arrowcolor=color,
                opacity=0.75,
            )
        )
        mid_x.append((x0 + x1) / 2.0)
        mid_y.append((y0 + y1) / 2.0)
        mid_text.append(
            f"{u} → {v}<br>Lift: {data['lift']:.2f} | Conf: {data['confidence']*100:.1f}% | Sup: {data['support']*100:.2f}%"
        )

    edge_hover_trace = go.Scatter(
        x=mid_x,
        y=mid_y,
        mode="markers",
        marker=dict(size=9, color="rgba(0,0,0,0)"),
        hoverinfo="text",
        text=mid_text,
        showlegend=False,
    )

    node_x: list[float] = []
    node_y: list[float] = []
    node_text: list[str] = []
    node_sizes: list[int] = []
    node_colors: list[int] = []

    for node in graph.nodes():
        x, y = pos[node]
        deg = graph.degree(node)
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node} (kết nối: {deg})")
        node_sizes.append(16 + min(24, deg * 3))
        node_colors.append(deg)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[n for n in graph.nodes()],
        textposition="top center",
        textfont=dict(size=10, color="#0F172A"),
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            size=node_sizes,
            color=node_colors,
            colorscale="YlGnBu",
            line=dict(width=1.5, color="#1E293B"),
            showscale=True,
            colorbar=dict(title="Số liên kết"),
        ),
        showlegend=False,
    )

    title_suffix = f" (Lọc theo: {focus_item})" if focus_item else ""
    fig = go.Figure(data=edge_traces + [edge_hover_trace, node_trace])
    fig.update_layout(
        title=f"Mạng lưới Luật kết hợp (Top {len(sub)} luật theo Lift){title_suffix}",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        annotations=annotations,
        height=600,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def plot_benchmark_curves(bench_df: pd.DataFrame) -> tuple[go.Figure, go.Figure]:
    """Plot runtime and peak memory comparison curves across min_support thresholds."""
    df_sorted = bench_df.sort_values("min_support", ascending=False).copy()
    df_sorted["support_label"] = df_sorted["min_support"].map(lambda v: f"{v:.3f}")

    fig_time = px.line(
        df_sorted,
        x="support_label",
        y="runtime_sec",
        color="algorithm",
        markers=True,
        labels={
            "support_label": "Ngưỡng hỗ trợ tối thiểu (min_support)",
            "runtime_sec": "Thời gian thực thi (giây)",
            "algorithm": "Thuật toán",
        },
        title="So sánh thời gian thực thi khi giảm dần min_support",
    )
    fig_time.update_xaxes(type="category")
    fig_time.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=30))

    fig_mem = px.line(
        df_sorted,
        x="support_label",
        y="peak_memory_mb",
        color="algorithm",
        markers=True,
        labels={
            "support_label": "Ngưỡng hỗ trợ tối thiểu (min_support)",
            "peak_memory_mb": "Bộ nhớ đỉnh (MB)",
            "algorithm": "Thuật toán",
        },
        title="So sánh bộ nhớ đỉnh tiêu thụ khi giảm dần min_support",
    )
    fig_mem.update_xaxes(type="category")
    fig_mem.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=30))
    return fig_time, fig_mem
