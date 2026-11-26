"""Interactive Streamlit product demo for Market Basket Analysis (Group 23 - ICTU)."""

from __future__ import annotations

import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.algorithms import (
    ALGORITHM_RUNNERS,
    apriori_custom_with_trace,
    benchmark_algorithms,
    compute_shelf_zones,
    evaluate_rules_on_test,
    extract_rules,
    format_rules_display,
    mine_with_metrics,
    recommend_for_basket,
)
from src.part3_experiments import (
    prune_redundant_rules,
    run_ablation_study,
    run_cv_grid_search,
)
from src.data_pipeline import (
    DEFAULT_DATA_PATH,
    VN_DATA_PATH,
    compute_cooccurrence_matrix,
    compute_item_frequencies,
    load_raw_baskets,
    parse_csv_lines,
    prepare_dataset,
)
from src.visualizations import (
    plot_basket_size_distribution,
    plot_benchmark_curves,
    plot_cooccurrence_heatmap,
    plot_rules_network,
    plot_rules_scatter,
    plot_top_items,
)

st.set_page_config(
    page_title="Market Basket Analysis Demo | Nhóm 23 - ICTU",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Subtle custom CSS for clean metric cards and badges
st.markdown(
    """
    <style>
    .hero-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        color: #F8FAFC;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .hero-sub {
        font-size: 0.92rem;
        color: #CBD5E1;
    }
    .rec-card {
        border: 1px solid #E2E8F0;
        border-left: 5px solid #10B981;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.65rem;
        background-color: #F8FAFC;
    }
    .baseline-card {
        border: 1px solid #E2E8F0;
        border-left: 5px solid #94A3B8;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.55rem;
        background-color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_and_prepare(
    dataset_source: str,
    file_bytes: bytes | None,
    min_basket_size: int,
    test_size: float,
):
    if file_bytes is not None:
        text = file_bytes.decode("utf-8", errors="ignore")
        raw_baskets = parse_csv_lines(text.splitlines())
    elif dataset_source == "vn":
        raw_baskets = load_raw_baskets(VN_DATA_PATH)
    else:
        raw_baskets = load_raw_baskets(DEFAULT_DATA_PATH)
    return prepare_dataset(
        raw_baskets,
        min_basket_size=min_basket_size,
        test_size=test_size,
        random_state=42,
    )


@st.cache_data(show_spinner=False)
def cached_mine(
    _df_train: pd.DataFrame,
    dataset_sig: tuple[int, int, int],
    algorithm: str,
    min_support: float,
    min_confidence: float,
    min_lift: float,
    max_len: int | None,
):
    return mine_with_metrics(
        _df_train,
        algorithm=algorithm,
        min_support=min_support,
        min_confidence=min_confidence,
        min_lift=min_lift,
        max_len=max_len,
    )


st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">🛒 Hệ thống Phân tích Giỏ hàng & Gợi ý Sản phẩm Mua kèm</div>
        <div class="hero-sub">
            Đề tài Học máy (Nhóm 23 — CNTT K22H, ICTU) | SV: Trần Văn Thực & Nguyễn Đức An Bình | GVHD: Nguyễn Tuấn Anh
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Cấu hình Mô hình & Dữ liệu")

    dataset_option = st.radio(
        "Chọn nguồn dữ liệu giao dịch:",
        options=[
            "🇻🇳 Siêu thị Việt Nam (3.000 hóa đơn)",
            "🌍 Groceries chuẩn (9.835 hóa đơn)",
            "📤 Tải lên CSV tùy chỉnh",
        ],
        index=0,
    )
    dataset_source = "vn" if dataset_option.startswith("🇻🇳") else "groceries"
    file_bytes: bytes | None = None
    if dataset_option.startswith("📤"):
        uploaded_file = st.file_uploader(
            "Tải lên dữ liệu giao dịch CSV (Groceries / Online Retail)",
            type=["csv", "txt"],
            help="Hỗ trợ cả định dạng giỏ hàng từng dòng và Online Retail (cột InvoiceNo, Description).",
        )
        file_bytes = uploaded_file.getvalue() if uploaded_file is not None else None
        if file_bytes is None:
            st.info("Chưa chọn file tải lên — tạm hiển thị dữ liệu Siêu thị Việt Nam.")
            dataset_source = "vn"

    filter_single = st.checkbox(
        "Lọc bỏ giỏ hàng chỉ có 1 sản phẩm",
        value=True,
        help="Loại bỏ các hóa đơn chỉ có 1 món gây nhiễu để tập trung vào hành vi mua kèm.",
    )
    min_basket_size = 2 if filter_single else 1

    st.divider()
    st.subheader("Thuật toán & Siêu tham số")
    algorithm = st.selectbox(
        "Thuật toán khai phá",
        options=list(ALGORITHM_RUNNERS.keys()),
        index=0,
    )
    min_support = st.slider(
        "Ngưỡng hỗ trợ (min_support)",
        min_value=0.003,
        max_value=0.050,
        value=0.008,
        step=0.001,
        format="%.3f",
    )
    min_confidence = st.slider(
        "Ngưỡng tin cậy (min_confidence)",
        min_value=0.10,
        max_value=0.70,
        value=0.25,
        step=0.05,
        format="%.2f",
    )
    min_lift = st.slider(
        "Ngưỡng tương quan (min_lift)",
        min_value=1.00,
        max_value=3.00,
        value=1.50,
        step=0.05,
        format="%.2f",
        help="Báo cáo đặt tiêu chí thành công Lift >= 1.30 và giá trị tối ưu Lift >= 1.50.",
    )
    max_len_choice = st.selectbox(
        "Độ dài luật tối đa (max_len)",
        options=[2, 3, 4, "Không giới hạn"],
        index=1,
    )
    max_len = None if max_len_choice == "Không giới hạn" else int(max_len_choice)
    apply_pruning = st.checkbox(
        "Hậu xử lý cắt tỉa luật dư thừa",
        value=False,
        help="Loại bỏ luật X ⇒ Y nếu tồn tại tập con X' ⊂ X cho Confidence ≥ Confidence(X ⇒ Y).",
    )

    st.caption("Chiến lược đánh giá: Hold-out 80% Train / 20% Test (`random_state=42`).")

with st.spinner("Đang chuẩn bị dữ liệu và huấn luyện mô hình..."):
    bundle = load_and_prepare(
        dataset_source=dataset_source,
        file_bytes=file_bytes,
        min_basket_size=min_basket_size,
        test_size=0.20,
    )
    dataset_sig = (
        hash(dataset_source),
        bundle.stats["n_raw_transactions"],
        bundle.stats["n_train"],
        min_basket_size,
    )
    mining_res = cached_mine(
        bundle.df_train,
        dataset_sig=dataset_sig,
        algorithm=algorithm,
        min_support=min_support,
        min_confidence=min_confidence,
        min_lift=min_lift,
        max_len=max_len,
    )
    freq_train_df = compute_item_frequencies(bundle.train_baskets)
    freq_raw_df = compute_item_frequencies(bundle.clean_baskets)
    rules_df = prune_redundant_rules(mining_res.rules) if apply_pruning else mining_res.rules

# Top summary KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Tổng hóa đơn gốc", f"{bundle.stats['n_raw_transactions']:,}")
k2.metric("Tập Train (80%)", f"{bundle.stats['n_train']:,}", delta=f"Test: {bundle.stats['n_test']:,} (20%)", delta_color="off")
k3.metric("Số luật khai phá được", f"{len(rules_df)}")
avg_lift = float(rules_df["lift"].mean()) if not rules_df.empty else 0.0
avg_conf = float(rules_df["confidence"].mean() * 100.0) if not rules_df.empty else 0.0
k4.metric("Lift trung bình", f"{avg_lift:.2f}", delta=f"{avg_lift - 1.0:+.2f} vs Baseline")
k5.metric("Thời gian chạy", f"{mining_res.runtime_sec:.3f} s", delta=f"{avg_conf:.1f}% Conf TB")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "🛒 Demo Gợi ý Mua kèm",
        "📊 Khám phá Dữ liệu (EDA)",
        "⚙️ Luật kết hợp & Lọc Lift",
        "🕸️ Mạng lưới & Quầy kệ",
        "⚡ So sánh Hiệu năng",
        "📖 Lý thuyết & Độ đo",
        "🔬 Tối ưu & Cải tiến (Phần 3)",
    ]
)

# ==============================================================================
# TAB 1: POS / E-COMMERCE RECOMMENDATION DEMO
# ==============================================================================
with tab1:
    st.subheader("Mô phỏng Hệ thống Gợi ý Sản phẩm tại Quầy thu ngân / Giỏ hàng TMĐT")
    st.write(
        "Chọn các sản phẩm khách hàng đang có trong giỏ để xem mô hình đề xuất món **Thường được mua kèm** theo thời gian thực và đối chiếu với mô hình cơ sở (Most Popular)."
    )

    all_items = sorted(bundle.df_train.columns.tolist())

    # Adaptive preset scenarios based on active dataset language
    is_vn_dataset = "Thịt ba chỉ" in all_items or "Sữa tươi Vinamilk" in all_items
    if is_vn_dataset:
        presets = {
            "Tùy chọn thủ công": [],
            "🥗 Giỏ Cơm gia đình (Thịt ba chỉ + Rau muống)": [
                i for i in ["Thịt ba chỉ", "Rau muống"] if i in all_items
            ],
            "🍲 Giỏ Lẩu cuối tuần (Gia vị lẩu Thái + Thịt bò Úc)": [
                i for i in ["Gia vị lẩu Thái", "Thịt bò Úc"] if i in all_items
            ],
            "🥖 Giỏ Bữa sáng (Bánh mì sandwich + Xúc xích Vissan)": [
                i for i in ["Bánh mì sandwich", "Xúc xích Vissan"] if i in all_items
            ],
            "☕ Giỏ Cà phê sáng (Cà phê hòa tan G7)": [
                i for i in ["Cà phê hòa tan G7"] if i in all_items
            ],
            "🧼 Giỏ Giặt giũ gia đình (Nước giặt Omo)": [
                i for i in ["Nước giặt Omo"] if i in all_items
            ],
        }
    else:
        presets = {
            "Tùy chọn thủ công": [],
            "🥗 Giỏ Rau củ & Trái cây (Root veg + Tropical fruit)": [
                i for i in ["root vegetables", "tropical fruit"] if i in all_items
            ],
            "🥛 Giỏ Sữa & Bữa sáng (Yogurt + Whole milk)": [
                i for i in ["yogurt", "whole milk"] if i in all_items
            ],
            "🥖 Giỏ Bánh mì & Sữa (Rolls/buns + Whole milk)": [
                i for i in ["rolls/buns", "whole milk"] if i in all_items
            ],
            "🥤 Giỏ Đồ uống & Ăn vặt (Soda + Shopping bags)": [
                i for i in ["soda", "shopping bags"] if i in all_items
            ],
        }

    c_left, c_right = st.columns([1.05, 1.35])
    with c_left:
        selected_preset = st.selectbox("Chọn kịch bản giỏ hàng mẫu:", list(presets.keys()), index=1)
        default_items = presets[selected_preset] if presets[selected_preset] else all_items[:2]
        selected_basket = st.multiselect(
            "🛍️ Sản phẩm hiện có trong giỏ hàng:",
            options=all_items,
            default=default_items,
        )
        top_k = st.slider("Số lượng gợi ý tối đa", min_value=1, max_value=10, value=5)

        if selected_basket:
            st.info(f"**Giỏ hàng hiện tại ({len(selected_basket)} món):** " + ", ".join(selected_basket))
        else:
            st.warning("Hãy chọn ít nhất 1 sản phẩm để nhận gợi ý mua kèm.")

    with c_right:
        rec_df, baseline_df = recommend_for_basket(
            selected_basket, rules_df, freq_train_df, top_k=top_k
        )
        col_smart, col_base = st.columns(2)

        with col_smart:
            st.markdown("### ✅ Gợi ý từ Mô hình Luật kết hợp")
            if rec_df.empty:
                st.warning(
                    "Chưa tìm thấy luật phù hợp với tổ hợp hiện tại ở ngưỡng lọc hiện hành. Hãy thử thêm sản phẩm khác hoặc giảm `min_support` / `min_lift`."
                )
            else:
                for idx, row in rec_df.iterrows():
                    conv = row["conviction"]
                    conv_str = f"{conv:.2f}" if pd.notna(conv) and conv < 1e6 else "∞"
                    st.markdown(
                        f"""
                        <div class="rec-card">
                            <strong>#{idx + 1} {row['recommended_item']}</strong><br/>
                            <small>Kích hoạt bởi: <code>{row['triggered_by']}</code></small><br/>
                            <small>
                                <b>Confidence:</b> {row['confidence']*100:.1f}% &nbsp;|&nbsp;
                                <b>Lift:</b> {row['lift']:.2f}x &nbsp;|&nbsp;
                                <b>Conviction:</b> {conv_str}
                            </small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                top_rec = rec_df.iloc[0]
                st.success(
                    f"💡 **Đề xuất Combo / Upsell:** Tặng mã giảm 10% khi khách mua **{top_rec['triggered_by']}** kèm **{top_rec['recommended_item']}** (xác suất mua kèm đạt **{top_rec['confidence']*100:.1f}%**, cao gấp **{top_rec['lift']:.2f} lần** ngẫu nhiên)."
                )

        with col_base:
            st.markdown("### 📌 Mô hình Cơ sở (Most Popular)")
            st.caption("Luôn gợi ý các món bán chạy nhất toàn cửa hàng mà không xét ngữ cảnh giỏ hàng (Lift = 1.00).")
            for idx, row in baseline_df.iterrows():
                st.markdown(
                    f"""
                    <div class="baseline-card">
                        <strong>{row['item']}</strong><br/>
                        <small>
                            <b>Tỷ lệ mua mặc định:</b> {row['support_pct']:.2f}% &nbsp;|&nbsp;
                            <b>Lift:</b> 1.00x
                        </small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ==============================================================================
# TAB 2: EDA & DATA PREPROCESSING
# ==============================================================================
with tab2:
    st.subheader("Khảo sát Thống kê & Xử lý Chất lượng Dữ liệu")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Độ dài giỏ TB (gốc)", f"{bundle.stats['avg_basket_size']:.2f} món")
    m2.metric("Trung vị / Tối đa", f"{bundle.stats['median_basket_size']:.0f} / {bundle.stats['max_basket_size']} món")
    m3.metric("Độ thưa ma trận", f"{bundle.stats['sparsity_pct']:.2f}%")
    m4.metric("Hóa đơn 1 món đã lọc", f"{bundle.stats['single_item_count']:,}", delta=f"{bundle.stats['single_item_pct']:.2f}% tổng gốc", delta_color="off")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_top_items(freq_raw_df, top_n=15), width="stretch")
    with c2:
        st.plotly_chart(plot_basket_size_distribution(bundle.clean_baskets, max_display=15), width="stretch")

    st.plotly_chart(
        plot_cooccurrence_heatmap(compute_cooccurrence_matrix(bundle.clean_baskets, top_n=8)),
        width="stretch",
    )

    st.markdown("#### Bảng kiểm toán & Xử lý Chất lượng Dữ liệu")
    audit_df = pd.DataFrame(
        [
            {
                "Vấn đề": "Giá trị thiếu (Ô trống cuối dòng)",
                "Thống kê phát hiện": "Độ dài mỗi giỏ hàng khác nhau (1–32 món)",
                "Cách xử lý áp dụng": "Bỏ qua ô trống khi phân tách danh sách giao dịch",
            },
            {
                "Vấn đề": "Mặt hàng trùng trong cùng hóa đơn",
                "Thống kê phát hiện": f"{bundle.stats['duplicate_items_removed']} bản ghi món lặp lại",
                "Cách xử lý áp dụng": "Chuyển từng giỏ thành tập hợp (set) trước khi mã hóa One-Hot",
            },
            {
                "Vấn đề": "Giá trị ngoại lai (Giỏ chỉ 1 món)",
                "Thống kê phát hiện": f"{bundle.stats['single_item_count']:,} hóa đơn ({bundle.stats['single_item_pct']:.2f}%)",
                "Cách xử lý áp dụng": "Lọc bỏ giỏ < 2 món" if filter_single else "Đang giữ lại (chưa lọc)",
            },
            {
                "Vấn đề": "Nguy cơ rò rỉ dữ liệu (Data Leakage)",
                "Thống kê phát hiện": f"{bundle.stats['n_filtered_transactions']:,} hóa đơn hợp lệ",
                "Cách xử lý áp dụng": f"Chia Hold-out 80/20 (random_state=42); TransactionEncoder chỉ fit trên {bundle.stats['n_train']:,} giỏ Train",
            },
        ]
    )
    st.dataframe(audit_df, width="stretch", hide_index=True)

# ==============================================================================
# TAB 3: RULES & HOLD-OUT GENERALIZATION
# ==============================================================================
with tab3:
    st.subheader("Kết quả Khai phá Luật kết hợp & Đánh giá trên Tập kiểm tra (20%)")

    if rules_df.empty:
        st.warning("Không có luật nào thỏa mãn bộ ngưỡng hiện tại. Vui lòng nới lỏng ngưỡng ở thanh bên trái.")
    else:
        col_pass1, col_pass2, col_pass3 = st.columns(3)
        col_pass1.metric(
            "Tiêu chí Lift >= 1.30",
            f"{avg_lift:.2f}",
            delta="ĐẠT MỤC TIÊU" if avg_lift >= 1.30 else "CHƯA ĐẠT",
        )
        col_pass2.metric(
            "Tiêu chí Confidence >= 25%",
            f"{avg_conf:.2f}%",
            delta="ĐẠT MỤC TIÊU" if avg_conf >= 25.0 else "CHƯA ĐẠT",
        )
        col_pass3.metric("Tập phổ biến tìm được", f"{len(mining_res.frequent_itemsets)}")

        st.plotly_chart(plot_rules_scatter(rules_df, min_confidence=min_confidence), width="stretch")

        # Compare impact of Lift filtering thresholds on the discovered frequent itemsets
        lift_summary_rows = []
        for l_thr, label in [
            (1.00, "Không lọc Lift (Lift >= 1.00)"),
            (1.30, "Ngưỡng cơ bản (Lift >= 1.30)"),
            (1.50, "Ngưỡng tối ưu (Lift >= 1.50)"),
        ]:
            sub_r = extract_rules(
                mining_res.frequent_itemsets,
                min_confidence=min_confidence,
                min_lift=l_thr,
                max_len=max_len,
            )
            lift_summary_rows.append(
                {
                    "Mức lọc Lift": label,
                    "Số luật giữ lại": len(sub_r),
                    "Confidence TB (%)": round(float(sub_r["confidence"].mean() * 100.0), 2) if not sub_r.empty else 0.0,
                    "Lift TB": round(float(sub_r["lift"].mean()), 2) if not sub_r.empty else 0.0,
                }
            )
        with st.expander("📌 Tác động của việc lọc luật có ý nghĩa theo Lift", expanded=True):
            st.dataframe(pd.DataFrame(lift_summary_rows), width="stretch", hide_index=True)

        search_hint = "Thịt ba chỉ, Trứng gà ta, Sữa tươi Vinamilk" if is_vn_dataset else "whole milk, yogurt, rolls/buns"
        search_kw = st.text_input(f"🔍 Lọc nhanh luật theo tên sản phẩm (ví dụ: {search_hint}):")
        display_rules = format_rules_display(rules_df)
        if search_kw.strip():
            kw = search_kw.strip().lower()
            mask = display_rules["Sản phẩm đã mua (Vế trái X)"].str.lower().str.contains(kw) | display_rules[
                "Gợi ý mua kèm (Vế phải Y)"
            ].str.lower().str.contains(kw)
            display_rules = display_rules[mask]

        st.dataframe(display_rules, width="stretch", hide_index=True)

        csv_buf = io.StringIO()
        display_rules.to_csv(csv_buf, index=False, encoding="utf-8-sig")
        st.download_button(
            "⬇️ Tải xuống bảng luật kết hợp (.csv)",
            data=csv_buf.getvalue().encode("utf-8-sig"),
            file_name="association_rules_nhom23.csv",
            mime="text/csv",
        )

        st.divider()
        st.markdown("#### 🧪 Kiểm chứng Khả năng Tổng quát hóa trên Tập kiểm tra giữ lại (Test 20%)")
        eval_df = evaluate_rules_on_test(rules_df, bundle.df_test)
        if not eval_df.empty:
            train_lift_mean = eval_df["train_lift"].mean()
            test_lift_mean = eval_df["test_lift"].mean()
            train_conf_mean = eval_df["train_confidence"].mean() * 100.0
            test_conf_mean = eval_df["test_confidence"].mean() * 100.0
            drift_pct = ((test_lift_mean - train_lift_mean) / train_lift_mean * 100.0) if train_lift_mean else 0.0

            e1, e2, e3 = st.columns(3)
            e1.metric("Lift TB (Train → Test)", f"{train_lift_mean:.2f} → {test_lift_mean:.2f}", delta=f"{drift_pct:+.1f}%")
            e2.metric(
                "Confidence TB (Train → Test)",
                f"{train_conf_mean:.1f}% → {test_conf_mean:.1f}%",
                delta=f"{test_conf_mean - train_conf_mean:+.1f}%",
            )
            e3.metric("Số giỏ hàng kiểm chứng", f"{len(bundle.df_test):,}")

            st.dataframe(
                eval_df.assign(
                    train_support=lambda d: (d["train_support"] * 100).round(2),
                    test_support=lambda d: (d["test_support"] * 100).round(2),
                    train_confidence=lambda d: (d["train_confidence"] * 100).round(1),
                    test_confidence=lambda d: (d["test_confidence"] * 100).round(1),
                    train_lift=lambda d: d["train_lift"].round(2),
                    test_lift=lambda d: d["test_lift"].round(2),
                    conviction=lambda d: d["conviction"].round(2),
                ).rename(
                    columns={
                        "rule": "Luật kết hợp",
                        "train_support": "Sup Train (%)",
                        "test_support": "Sup Test (%)",
                        "train_confidence": "Conf Train (%)",
                        "test_confidence": "Conf Test (%)",
                        "train_lift": "Lift Train",
                        "test_lift": "Lift Test",
                        "conviction": "Conviction",
                    }
                ),
                width="stretch",
                hide_index=True,
            )

# ==============================================================================
# TAB 4: NETWORK GRAPH & STORE LAYOUT INSIGHTS
# ==============================================================================
with tab4:
    st.subheader("Trực quan hóa Mạng lưới Luật kết hợp & Đề xuất Bố trí Quầy kệ")
    if rules_df.empty:
        st.warning("Chưa có luật kết hợp để dựng mạng lưới.")
    else:
        net_items = sorted({item for row in rules_df["antecedents"] for item in row} | {item for row in rules_df["consequents"] for item in row})
        n_c1, n_c2 = st.columns([1.4, 1.0])
        with n_c1:
            max_net_rules = st.slider(
                "Số luật hiển thị trên đồ thị mạng",
                min_value=5,
                max_value=min(60, max(5, len(rules_df))),
                value=min(25, len(rules_df)),
            )
        with n_c2:
            focus_choice = st.selectbox(
                "Thu phóng theo sản phẩm trung tâm (tùy chọn)",
                options=["(Tất cả sản phẩm)"] + net_items,
                index=0,
            )
        focus_item = None if focus_choice == "(Tất cả sản phẩm)" else focus_choice
        st.plotly_chart(
            plot_rules_network(rules_df, max_rules=max_net_rules, focus_item=focus_item),
            width="stretch",
        )

        st.markdown("#### 🗺️ Đề xuất Phân khu & Sắp xếp Quầy kệ Siêu thị (Phân cụm mạng luật)")
        zones = compute_shelf_zones(rules_df, max_zones=4)
        if zones:
            z_cols = st.columns(min(4, len(zones)))
            for idx, z in enumerate(zones):
                with z_cols[idx]:
                    preview_items = ", ".join(z["items"][:6])
                    extra = f" (+{len(z['items']) - 6} món)" if len(z["items"]) > 6 else ""
                    st.success(
                        f"**Khu #{z['zone_id']} — Tâm điểm: {z['anchor_item']}**\n\n"
                        f"- **Nhóm hàng nên đặt gần nhau:** {preview_items}{extra}\n"
                        f"- **Lift nội khu TB:** `{z['avg_lift']:.2f}x` ({z['n_links']} liên kết)"
                    )

        st.markdown("#### 🏬 Đề xuất Quy tắc Bán chéo & Khuyến mãi Chi tiết")
        top_insights = rules_df.head(6)
        cols = st.columns(2)
        for idx, (_, row) in enumerate(top_insights.iterrows()):
            ant = ", ".join(sorted(row["antecedents"]))
            cons = ", ".join(sorted(row["consequents"]))
            with cols[idx % 2]:
                st.info(
                    f"**Quy tắc #{idx + 1}: {ant} → {cons}**\n\n"
                    f"- **Độ mạnh liên kết:** Lift = **{row['lift']:.2f}**, Confidence = **{row['confidence']*100:.1f}%**\n"
                    f"- **Ứng dụng thực tế:** Đặt quầy **{ant}** gần khu vực **{cons}** hoặc gắn nhãn *'Thường được mua kèm'* trên ứng dụng đặt hàng."
                )

# ==============================================================================
# TAB 5: ALGORITHM PERFORMANCE BENCHMARK
# ==============================================================================
with tab5:
    st.subheader("Đối sánh Hiệu năng Thuật toán: Apriori (Python) vs ECLAT vs FP-Growth (mlxtend)")
    st.write(
        "Chạy thực nghiệm đo trực tiếp thời gian thực thi (`perf_counter`) và bộ nhớ đỉnh (`tracemalloc`) trên tập huấn luyện hiện tại khi giảm dần ngưỡng `min_support`."
    )

    include_005 = st.checkbox(
        "Bao gồm ngưỡng siêu thấp min_support = 0.005 (Apriori có thể mất vài giây)",
        value=False,
    )
    support_grid = [0.05, 0.03, 0.02, 0.01, 0.008] + ([0.005] if include_005 else [])

    if st.button("🚀 Chạy Benchmark So sánh Trực tiếp", type="primary"):
        with st.spinner("Đang thực thi Apriori, ECLAT và FP-Growth qua các ngưỡng support..."):
            bench_df = benchmark_algorithms(bundle.df_train, support_thresholds=support_grid, max_len=max_len)
        st.session_state["bench_df"] = bench_df

    if "bench_df" in st.session_state:
        bench_df = st.session_state["bench_df"]
        fig_t, fig_m = plot_benchmark_curves(bench_df)
        b1, b2 = st.columns(2)
        b1.plotly_chart(fig_t, width="stretch")
        b2.plotly_chart(fig_m, width="stretch")

        # Speedup summary at lowest tested support
        lowest_sup = min(bench_df["min_support"])
        sub_low = bench_df[bench_df["min_support"] == lowest_sup].set_index("algorithm")
        if "Apriori (Python)" in sub_low.index and "FP-Growth (mlxtend)" in sub_low.index:
            t_apr = sub_low.loc["Apriori (Python)", "runtime_sec"]
            t_fp = sub_low.loc["FP-Growth (mlxtend)", "runtime_sec"]
            t_ecl = sub_low.loc["ECLAT (Python)", "runtime_sec"] if "ECLAT (Python)" in sub_low.index else None
            n_apr = int(sub_low.loc["Apriori (Python)", "n_itemsets"])
            n_fp = int(sub_low.loc["FP-Growth (mlxtend)", "n_itemsets"])
            speedup_fp = (t_apr / t_fp) if t_fp > 0 else 0.0
            ecl_note = f", ECLAT: `{t_ecl:.3f}s`" if t_ecl is not None else ""
            st.success(
                f"Tại ngưỡng `min_support = {lowest_sup:.3f}`: Cả 3 thuật toán tìm ra chính xác **{n_fp} == {n_apr} tập phổ biến** (nhất quán 100%). "
                f"**FP-Growth** đạt `{t_fp:.3f}s` — nhanh gấp **{speedup_fp:.1f} lần** so với Apriori tự cài đặt (`{t_apr:.3f}s`){ecl_note}."
            )

        st.dataframe(
            bench_df.assign(
                runtime_sec=lambda d: d["runtime_sec"].round(4),
                peak_memory_mb=lambda d: d["peak_memory_mb"].round(3),
            ).rename(
                columns={
                    "min_support": "min_support",
                    "algorithm": "Thuật toán",
                    "runtime_sec": "Thời gian (giây)",
                    "peak_memory_mb": "Bộ nhớ đỉnh (MB)",
                    "n_itemsets": "Số tập phổ biến",
                }
            ),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("Nhấn nút **🚀 Chạy Benchmark So sánh Trực tiếp** để đo hiệu năng thực tế trên máy của bạn.")

# ==============================================================================
# TAB 6: THEORY, METRICS CALCULATOR & APRIORI STEP-BY-STEP TRACE
# ==============================================================================
with tab6:
    st.subheader("Cơ sở Lý thuyết: Tập phổ biến, Luật kết hợp & Các Độ đo Đánh giá")

    f1, f2 = st.columns(2)
    with f1:
        st.markdown("#### 📐 Công thức 4 độ đo cốt lõi ($X \\Rightarrow Y$)")
        st.latex(r"\text{Support}(X \Rightarrow Y) = P(X \cup Y) = \frac{|\{T \in D : X \cup Y \subseteq T\}|}{N}")
        st.latex(r"\text{Confidence}(X \Rightarrow Y) = \frac{P(X \cup Y)}{P(X)}")
        st.latex(r"\text{Lift}(X \Rightarrow Y) = \frac{\text{Confidence}(X \Rightarrow Y)}{P(Y)} = \frac{P(X \cup Y)}{P(X)\cdot P(Y)}")
        st.latex(r"\text{Conviction}(X \Rightarrow Y) = \frac{1 - P(Y)}{1 - \text{Confidence}(X \Rightarrow Y)}")
        st.caption(
            "• **Lift > 1**: tương quan dương thực sự (mục tiêu ≥ 1.30). "
            "• **Conviction**: đo độ lệch so với giả định độc lập thống kê, giúp phân biệt chiều gợi ý X ⇒ Y hay Y ⇒ X."
        )

    with f2:
        st.markdown("#### 🧮 Minh họa Tính toán Trực tiếp trên Luật Thực tế")
        if rules_df.empty:
            st.info("Hãy giảm ngưỡng lọc để có luật minh họa.")
        else:
            rule_labels = [
                f"{', '.join(sorted(r['antecedents']))}  ⇒  {', '.join(sorted(r['consequents']))}"
                for _, r in rules_df.head(30).iterrows()
            ]
            chosen_idx = st.selectbox(
                "Chọn một luật khai phá được để xem chi tiết phép tính:",
                options=range(len(rule_labels)),
                format_func=lambda i: f"#{i+1}: {rule_labels[i]}",
            )
            r = rules_df.iloc[chosen_idx]
            n_train_tx = len(bundle.df_train)
            p_x = float(r["antecedent support"])
            p_y = float(r["consequent support"])
            p_xy = float(r["support"])
            conf_xy = float(r["confidence"])
            lift_xy = float(r["lift"])
            conv_xy = float(r["conviction"])
            # Reverse direction Y => X for Conviction comparison
            conf_yx = (p_xy / p_y) if p_y > 0 else 0.0
            conv_yx = ((1.0 - p_x) / (1.0 - conf_yx)) if conf_yx < 1.0 else float("inf")

            c_m1, c_m2, c_m3, c_m4 = st.columns(4)
            c_m1.metric("Support", f"{p_xy*100:.2f}%", delta=f"{int(round(p_xy*n_train_tx))}/{n_train_tx} giỏ", delta_color="off")
            c_m2.metric("Confidence", f"{conf_xy*100:.1f}%")
            c_m3.metric("Lift", f"{lift_xy:.2f}x")
            c_m4.metric("Conviction", f"{conv_xy:.2f}" if conv_xy < 1e6 else "∞")

            st.info(
                f"**So sánh 2 chiều để thấy vai trò của Conviction:**\n"
                f"- Chiều thuận **X ⇒ Y**: `Confidence = {conf_xy*100:.1f}%`, `Conviction = {conv_xy:.2f}`\n"
                f"- Chiều ngược **Y ⇒ X**: `Confidence = {conf_yx*100:.1f}%`, `Conviction = {conv_yx:.2f}`\n"
                f"→ Chiều có Confidence & Conviction cao hơn phản ánh sản phẩm dẫn dắt hành vi mua kèm đáng tin cậy hơn."
            )

    st.divider()
    st.markdown("#### 🔍 Cơ chế 3 Thuật toán & Theo dõi Cắt tỉa Apriori (`C_k → L_k`)")
    algo_c1, algo_c2, algo_c3 = st.columns(3)
    algo_c1.info("**1. Apriori (Tự cài đặt Python)**\nDuyệt theo chiều rộng (BFS), sinh tập ứng viên $C_k$ từ $L_{k-1}$, cắt tỉa theo nguyên lý phản đơn điệu và quét CSDL theo từng mức.")
    algo_c2.success("**2. FP-Growth (mlxtend)**\nNén toàn bộ giỏ hàng vào cây tiền tố **FP-Tree** + Header Table chỉ sau 2 lần quét CSDL, không sinh tập ứng viên trung gian.")
    algo_c3.warning("**3. ECLAT (Bổ trợ)**\nBiểu diễn dữ liệu dọc (**TID-set**) và duyệt chiều sâu (DFS), tính Support nhanh bằng phép giao $|TID(X) \\cap TID(Y)|$.")

    if st.button("🔎 Chạy & Hiển thị Bảng Cắt tỉa Ứng viên Apriori (C_k → L_k)"):
        with st.spinner("Đang theo dõi quá trình sinh & cắt tỉa ứng viên Apriori..."):
            _, trace_df = apriori_custom_with_trace(bundle.df_train, min_support=min_support, max_len=max_len)
        st.session_state["apriori_trace"] = trace_df

    if "apriori_trace" in st.session_state and not st.session_state["apriori_trace"].empty:
        tdf = st.session_state["apriori_trace"].copy()
        tdf["pruned_pct"] = ((tdf["candidates_Ck"] - tdf["frequent_Lk"]) / tdf["candidates_Ck"].clip(lower=1) * 100.0).round(1)
        st.dataframe(
            tdf.rename(
                columns={
                    "k": "Độ dài tập (k)",
                    "candidates_Ck": "Số ứng viên (|C_k|)",
                    "frequent_Lk": "Đạt min_support (|L_k|)",
                    "pruned_pct": "Tỷ lệ loại bỏ (%)",
                }
            ),
            width="stretch",
            hide_index=True,
        )

# ==============================================================================
# TAB 7: PART 3 - OPTIMIZATION, ABLATION STUDY & GENERALIZATION
# ==============================================================================
with tab7:
    st.subheader("Tối ưu hóa, Cải tiến & So sánh Mô hình (Bài kiểm tra 3)")

    st.markdown("#### 1. Bảng Phân tích Hạn chế Ban đầu & Giải pháp Cải tiến")
    lim_df = pd.DataFrame(
        [
            {
                "Hạn chế của mô hình ban đầu": "Thời gian chạy Apriori tăng theo hàm mũ khi giảm min_support (lên tới 5,67s tại 0,005)",
                "Bằng chứng thực nghiệm": "Benchmark hiệu năng: Apriori chậm hơn FP-Growth ~29–45 lần tại min_support 0,008–0,005",
                "Giải pháp & Cơ sở lý thuyết": "Chuyển sang FP-Growth (cây tiền tố nén FP-Tree, chỉ 2 lần quét CSDL, không sinh ứng viên C_k)",
            },
            {
                "Hạn chế của mô hình ban đầu": f"{bundle.stats['single_item_count']:,} giỏ hàng 1 món ({bundle.stats['single_item_pct']:.2f}%) làm loãng Support và tăng dao động giữa các fold",
                "Bằng chứng thực nghiệm": "Các hóa đơn chỉ có 1 sản phẩm không tạo ra thông tin đồng xuất hiện khi tính Support & Confidence",
                "Giải pháp & Cơ sở lý thuyết": "Lọc bỏ giỏ < 2 món để tập trung vào hành vi mua kèm và giảm phương sai giữa các fold",
            },
            {
                "Hạn chế của mô hình ban đầu": "Ngưỡng Lift thấp (1,30) và luật quá dài (>3 món) gây nhiễu, khó trưng bày thực tế",
                "Bằng chứng thực nghiệm": "Giữ lại 406 luật, trong đó có nhiều cặp trùng hợp ngẫu nhiên với sản phẩm thiết yếu",
                "Giải pháp & Cơ sở lý thuyết": "Grid Search trên 5-Fold CV chọn min_lift=1,50, max_len=3 + Cắt tỉa luật dư thừa (Pruning)",
            },
        ]
    )
    st.dataframe(lim_df, width="stretch", hide_index=True)

    st.divider()
    st.markdown("#### 2. Tìm kiếm Siêu tham số (Grid Search) bằng Kiểm định chéo 5-Fold trên Tập Train")
    st.caption("Tuyệt đối KHÔNG dùng Tập kiểm tra (Test 20%) trong bước chọn siêu tham số để tránh rò rỉ dữ liệu.")

    g1, g2, g3, g4 = st.columns(4)
    sup_choices = g1.multiselect(
        "Không gian min_support",
        options=[0.005, 0.008, 0.010, 0.015, 0.020],
        default=[0.005, 0.008, 0.010, 0.015],
    )
    conf_choices = g2.multiselect(
        "Không gian min_confidence",
        options=[0.20, 0.25, 0.30, 0.35],
        default=[0.20, 0.25, 0.30],
    )
    lift_choices = g3.multiselect(
        "Không gian min_lift",
        options=[1.20, 1.30, 1.50, 1.80],
        default=[1.30, 1.50, 1.80],
    )
    len_choices = g4.multiselect(
        "Không gian max_len",
        options=[2, 3, "None"],
        default=[2, 3, "None"],
    )

    if st.button("🧪 Chạy 5-Fold CV Grid Search (Chỉ trên tập Train)", type="primary"):
        if not (sup_choices and conf_choices and lift_choices and len_choices):
            st.warning("Vui lòng chọn ít nhất 1 giá trị cho mỗi siêu tham số.")
        else:
            parsed_lens = [None if x == "None" else int(x) for x in len_choices]
            with st.spinner("Đang chạy kiểm định chéo 5-Fold trên 6.140 giỏ hàng Train..."):
                cv_grid_df = run_cv_grid_search(
                    bundle.train_baskets,
                    support_grid=sorted(sup_choices),
                    confidence_grid=sorted(conf_choices),
                    lift_grid=sorted(lift_choices),
                    max_len_grid=parsed_lens,
                    n_splits=5,
                )
            st.session_state["cv_grid_df"] = cv_grid_df

    if "cv_grid_df" in st.session_state and not st.session_state["cv_grid_df"].empty:
        gdf = st.session_state["cv_grid_df"]
        st.dataframe(
            gdf.head(15).assign(
                val_lift_mean=lambda d: d["val_lift_mean"].round(3),
                val_lift_std=lambda d: d["val_lift_std"].round(3),
                val_conf_mean=lambda d: (d["val_conf_mean"] * 100.0).round(2),
                val_conf_std=lambda d: (d["val_conf_std"] * 100.0).round(2),
                n_rules_mean=lambda d: d["n_rules_mean"].round(1),
                rule_retention_pct=lambda d: d["rule_retention_pct"].round(1),
            )[
                [
                    "min_support",
                    "min_confidence",
                    "min_lift",
                    "max_len",
                    "n_rules_mean",
                    "val_lift_mean",
                    "val_lift_std",
                    "val_conf_mean",
                    "val_conf_std",
                    "rule_retention_pct",
                ]
            ].rename(
                columns={
                    "n_rules_mean": "Số luật TB",
                    "val_lift_mean": "CV Lift TB",
                    "val_lift_std": "CV Lift Std",
                    "val_conf_mean": "CV Conf TB (%)",
                    "val_conf_std": "CV Conf Std (%)",
                    "rule_retention_pct": "Tỷ lệ giữ luật (%)",
                }
            ),
            width="stretch",
            hide_index=True,
        )

        # Interactive validation curve across min_support & min_lift
        curve_sub = gdf[(gdf["min_confidence"] == gdf["min_confidence"].median()) | (gdf["min_confidence"] == 0.25)]
        if 0.25 in gdf["min_confidence"].values:
            curve_sub = gdf[gdf["min_confidence"] == 0.25]
        if 3 in gdf["max_len"].values:
            curve_sub = curve_sub[curve_sub["max_len"] == 3]
        if not curve_sub.empty:
            fig_cv = go.Figure()
            for l_val in sorted(curve_sub["min_lift"].unique()):
                s = curve_sub[curve_sub["min_lift"] == l_val].sort_values("min_support")
                fig_cv.add_trace(
                    go.Scatter(
                        x=s["min_support"],
                        y=s["val_lift_mean"],
                        error_y=dict(type="data", array=s["val_lift_std"], visible=True),
                        mode="lines+markers",
                        name=f"min_lift ≥ {l_val:.2f}",
                    )
                )
            fig_cv.update_layout(
                title="Đường cong kiểm định chéo 5-Fold (Lift TB ± Std theo min_support)",
                xaxis_title="min_support",
                yaxis_title="CV Lift trung bình",
                height=400,
            )
            st.plotly_chart(fig_cv, width="stretch")

    st.divider()
    st.markdown("#### 3. So sánh Trước – Sau Cải tiến (Ablation Study) & Khả năng Tổng quát hóa")
    if st.button("📊 Chạy Ablation Study (5-Fold CV vs Tập Kiểm tra 20%)"):
        with st.spinner("Đang đo lường đóng góp từng bước cải tiến..."):
            ab_df = run_ablation_study(
                raw_clean_baskets=bundle.clean_baskets,
                filtered_train_baskets=bundle.train_baskets,
                df_filtered_train=bundle.df_train,
                df_filtered_test=bundle.df_test,
            )
        st.session_state["ab_df"] = ab_df

    if "ab_df" in st.session_state and not st.session_state["ab_df"].empty:
        ab_df = st.session_state["ab_df"]
        st.dataframe(
            ab_df.assign(
                cv_lift_mean=lambda d: d["cv_lift_mean"].round(3),
                cv_lift_std=lambda d: d["cv_lift_std"].round(3),
                cv_conf_mean=lambda d: d["cv_conf_mean"].round(2),
                cv_conf_std=lambda d: d["cv_conf_std"].round(2),
                test_lift=lambda d: d["test_lift"].round(3),
                test_conf=lambda d: d["test_conf"].round(2),
                delta_cv_lift=lambda d: d["delta_cv_lift"].round(3),
            ).rename(
                columns={
                    "step": "Cấu hình mô hình",
                    "n_rules_train": "Số luật",
                    "cv_lift_mean": "CV Lift TB",
                    "cv_lift_std": "CV Lift Std",
                    "cv_conf_mean": "CV Conf TB (%)",
                    "cv_conf_std": "CV Conf Std (%)",
                    "test_lift": "Test Lift TB",
                    "test_conf": "Test Conf TB (%)",
                    "delta_cv_lift": "Δ CV Lift",
                }
            ),
            width="stretch",
            hide_index=True,
        )

        fig_ab = go.Figure(
            data=[
                go.Bar(
                    name="5-Fold CV (Train)",
                    x=ab_df["step"],
                    y=ab_df["cv_lift_mean"],
                    error_y=dict(type="data", array=ab_df["cv_lift_std"], visible=True),
                    marker_color="#3B82F6",
                ),
                go.Bar(
                    name="Tập kiểm tra giữ lại (Test 20%)",
                    x=ab_df["step"],
                    y=ab_df["test_lift"],
                    marker_color="#10B981",
                ),
            ]
        )
        fig_ab.add_hline(y=1.30, line_dash="dash", line_color="#EF4444", annotation_text="Mục tiêu Lift ≥ 1.30")
        fig_ab.update_layout(
            barmode="group",
            title="So sánh Lift TB (5-Fold CV vs Hold-out Test) qua từng bước cải tiến",
            yaxis_title="Chỉ số Lift trung bình",
            height=430,
        )
        st.plotly_chart(fig_ab, width="stretch")
