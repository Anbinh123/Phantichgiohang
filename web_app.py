"""Modern full-stack web server (Starlette + Uvicorn) for SmartBasket MBA Demo."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from src.algorithms import (
    ALGORITHM_RUNNERS,
    apriori_custom_with_trace,
    benchmark_algorithms,
    compute_shelf_zones,
    evaluate_rules_on_test,
    extract_rules,
    mine_with_metrics,
    recommend_for_basket,
)
from src.data_pipeline import (
    DEFAULT_DATA_PATH,
    VN_DATA_PATH,
    DatasetBundle,
    compute_cooccurrence_matrix,
    compute_item_frequencies,
    load_raw_baskets,
    parse_csv_lines,
    prepare_dataset,
)
from src.part3_experiments import (
    prune_redundant_rules,
    run_ablation_study,
    run_cv_grid_search,
)

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"

# Metadata for Vietnamese supermarket products (category, icon, realistic retail price VND)
VN_CATALOG_META: dict[str, tuple[str, str, int]] = {
    "Thịt ba chỉ": ("Thịt & Rau củ", "🥩", 78000),
    "Thịt bò Úc": ("Thịt & Rau củ", "🥩", 145000),
    "Rau muống": ("Thịt & Rau củ", "🥬", 12000),
    "Rau cải thảo": ("Thịt & Rau củ", "🥬", 18000),
    "Cà chua": ("Thịt & Rau củ", "🍅", 16000),
    "Hành lá": ("Thịt & Rau củ", "🌿", 8000),
    "Tỏi ta": ("Thịt & Rau củ", "🧄", 15000),
    "Nấm kim châm": ("Thịt & Rau củ", "🍄", 19000),
    "Đậu phụ": ("Thịt & Rau củ", "🧈", 12000),
    "Trứng gà ta": ("Thịt & Rau củ", "🥚", 36000),
    "Chuối tiêu": ("Trái cây", "🍌", 22000),
    "Cam sành": ("Trái cây", "🍊", 32000),
    "Táo nhập khẩu": ("Trái cây", "🍎", 55000),
    "Thanh long": ("Trái cây", "🐉", 28000),
    "Sữa tươi Vinamilk": ("Sữa & Ăn sáng", "🥛", 34000),
    "Sữa chua Vinamilk": ("Sữa & Ăn sáng", "🍨", 26000),
    "Sữa đặc Ông Thọ": ("Sữa & Ăn sáng", "🥫", 24000),
    "Bánh mì sandwich": ("Sữa & Ăn sáng", "🍞", 22000),
    "Xúc xích Vissan": ("Sữa & Ăn sáng", "🌭", 35000),
    "Cà phê hòa tan G7": ("Sữa & Ăn sáng", "☕", 48000),
    "Mì tôm Hảo Hảo": ("Đồ khô & Gia vị", "🍜", 118000),
    "Gạo ST25": ("Đồ khô & Gia vị", "🍚", 185000),
    "Bún tươi": ("Đồ khô & Gia vị", "🍝", 15000),
    "Nước mắm Nam Ngư": ("Đồ khô & Gia vị", "🍾", 38000),
    "Dầu ăn Neptune": ("Đồ khô & Gia vị", "🌻", 54000),
    "Gia vị lẩu Thái": ("Đồ khô & Gia vị", "🍲", 21000),
    "Hạt nêm Knorr": ("Đồ khô & Gia vị", "🧂", 32000),
    "Đường trắng Biên Hòa": ("Đồ khô & Gia vị", "🍬", 28000),
    "Muối i-ốt": ("Đồ khô & Gia vị", "🧂", 7000),
    "Nước tương Maggi": ("Đồ khô & Gia vị", "🫙", 25000),
    "Bia Tiger": ("Đồ uống & Ăn vặt", "🍺", 19500),
    "Nước ngọt Coca-Cola": ("Đồ uống & Ăn vặt", "🥤", 12000),
    "Nước suối Lavie": ("Đồ uống & Ăn vặt", "💧", 6000),
    "Trà xanh Không Độ": ("Đồ uống & Ăn vặt", "🍵", 10000),
    "Snack Oishi": ("Đồ uống & Ăn vặt", "🍟", 11000),
    "Lạc rang": ("Đồ uống & Ăn vặt", "🥜", 18000),
    "Nước rửa chén Sunlight": ("Hóa mỹ phẩm", "🧴", 39000),
    "Nước giặt Omo": ("Hóa mỹ phẩm", "🧺", 135000),
    "Nước xả Comfort": ("Hóa mỹ phẩm", "🌸", 98000),
    "Giấy vệ sinh Pulppy": ("Hóa mỹ phẩm", "🧻", 68000),
    "Kem đánh răng P/S": ("Hóa mỹ phẩm", "🪥", 34000),
    "Bàn chải đánh răng": ("Hóa mỹ phẩm", "🪥", 25000),
    "Dầu gội Clear": ("Hóa mỹ phẩm", "🧴", 115000),
    "Túi đựng thực phẩm": ("Hóa mỹ phẩm", "🛍️", 22000),
}

# Server-side state cache for fast interactive operations
STATE: dict[str, Any] = {
    "dataset_source": "vn",
    "filter_single": True,
    "bundle": None,
    "freq_raw": None,
    "freq_train": None,
    "mining_res": None,
    "rules_df": pd.DataFrame(),
    "last_params": {},
}


def _infer_meta(item: str, is_vn: bool) -> dict[str, Any]:
    if item in VN_CATALOG_META:
        cat, icon, price = VN_CATALOG_META[item]
        return {"category": cat, "icon": icon, "price": price}
    lower = item.lower()
    if any(k in lower for k in ["milk", "yogurt", "cheese", "butter", "cream", "curd"]):
        return {"category": "Sữa & Bơ", "icon": "🥛", "price": 35000}
    if any(k in lower for k in ["veg", "fruit", "berries", "onions", "herbs", "citrus", "tropical"]):
        return {"category": "Rau củ & Trái cây", "icon": "🥬", "price": 28000}
    if any(k in lower for k in ["bread", "rolls", "pastry", "cake"]):
        return {"category": "Bánh mì & Ngọt", "icon": "🥐", "price": 24000}
    if any(k in lower for k in ["beef", "pork", "chicken", "sausage", "meat", "fish"]):
        return {"category": "Thịt & Hải sản", "icon": "🥩", "price": 85000}
    if any(k in lower for k in ["soda", "water", "beer", "wine", "juice", "coffee", "tea"]):
        return {"category": "Đồ uống", "icon": "🥤", "price": 18000}
    return {"category": "Khác" if is_vn else "Tạp hóa", "icon": "🛒", "price": 25000}


def _load_bundle(dataset_source: str, filter_single: bool, raw_text: str | None = None) -> DatasetBundle:
    if raw_text is not None:
        raw_baskets = parse_csv_lines(raw_text.splitlines())
    elif dataset_source == "vn":
        raw_baskets = load_raw_baskets(VN_DATA_PATH)
    else:
        raw_baskets = load_raw_baskets(DEFAULT_DATA_PATH)

    bundle = prepare_dataset(
        raw_baskets,
        min_basket_size=2 if filter_single else 1,
        test_size=0.20,
        random_state=42,
    )
    STATE["dataset_source"] = dataset_source
    STATE["filter_single"] = filter_single
    STATE["bundle"] = bundle
    STATE["freq_raw"] = compute_item_frequencies(bundle.clean_baskets)
    STATE["freq_train"] = compute_item_frequencies(bundle.train_baskets)
    return bundle


def _ensure_initialized() -> DatasetBundle:
    if STATE["bundle"] is None:
        return _load_bundle("vn", True)
    return STATE["bundle"]


def _serialize_dataset_payload(bundle: DatasetBundle) -> dict[str, Any]:
    freq_raw: pd.DataFrame = STATE["freq_raw"]
    freq_train: pd.DataFrame = STATE["freq_train"]
    train_items = set(bundle.df_train.columns.tolist())
    is_vn = "Thịt ba chỉ" in train_items or "Sữa tươi Vinamilk" in train_items

    freq_map = {
        row["item"]: {"count": int(row["count"]), "support_pct": round(float(row["support_pct"]), 2)}
        for _, row in freq_train.iterrows()
    }

    catalog = []
    for item in sorted(train_items):
        meta = _infer_meta(item, is_vn=is_vn)
        stats = freq_map.get(item, {"count": 0, "support_pct": 0.0})
        catalog.append(
            {
                "name": item,
                "category": meta["category"],
                "icon": meta["icon"],
                "price": meta["price"],
                "count": stats["count"],
                "support_pct": stats["support_pct"],
            }
        )
    catalog.sort(key=lambda x: (-x["support_pct"], x["name"]))

    sizes = [len(b) for b in bundle.clean_baskets]
    size_counts = pd.Series([s for s in sizes if s <= 15]).value_counts().sort_index()
    cooc = compute_cooccurrence_matrix(bundle.clean_baskets, top_n=8)

    if is_vn:
        presets = [
            {"id": "meal", "label": "🥗 Cơm gia đình", "items": [i for i in ["Thịt ba chỉ", "Rau muống"] if i in train_items]},
            {"id": "hotpot", "label": "🍲 Lẩu cuối tuần", "items": [i for i in ["Gia vị lẩu Thái", "Thịt bò Úc"] if i in train_items]},
            {"id": "breakfast", "label": "🥖 Bữa sáng nhanh", "items": [i for i in ["Bánh mì sandwich", "Xúc xích Vissan"] if i in train_items]},
            {"id": "coffee", "label": "☕ Cà phê sáng", "items": [i for i in ["Cà phê hòa tan G7"] if i in train_items]},
            {"id": "laundry", "label": "🧼 Giặt giũ", "items": [i for i in ["Nước giặt Omo"] if i in train_items]},
        ]
    else:
        presets = [
            {"id": "veg", "label": "🥗 Rau củ & Trái cây", "items": [i for i in ["root vegetables", "tropical fruit"] if i in train_items]},
            {"id": "dairy", "label": "🥛 Sữa & Sữa chua", "items": [i for i in ["yogurt", "whole milk"] if i in train_items]},
            {"id": "bakery", "label": "🥖 Bánh mì & Sữa", "items": [i for i in ["rolls/buns", "whole milk"] if i in train_items]},
            {"id": "drinks", "label": "🥤 Đồ uống", "items": [i for i in ["soda", "shopping bags"] if i in train_items]},
        ]

    return {
        "dataset_source": STATE["dataset_source"],
        "is_vn": is_vn,
        "filter_single": STATE["filter_single"],
        "stats": bundle.stats,
        "catalog": catalog,
        "presets": presets,
        "eda": {
            "top_items": [
                {"item": r["item"], "count": int(r["count"]), "support_pct": round(float(r["support_pct"]), 2)}
                for _, r in freq_raw.head(15).iterrows()
            ],
            "basket_sizes": [
                {"size": int(k), "count": int(v)} for k, v in size_counts.items()
            ],
            "cooccurrence": {
                "labels": list(cooc.columns),
                "matrix": [[round(float(val), 2) for val in row] for row in cooc.values],
            } if not cooc.empty else {"labels": [], "matrix": []},
        },
    }


def _run_mining(params: dict[str, Any]) -> dict[str, Any]:
    bundle = _ensure_initialized()
    algorithm = params.get("algorithm", "FP-Growth (mlxtend)")
    if algorithm not in ALGORITHM_RUNNERS:
        algorithm = "FP-Growth (mlxtend)"
    min_support = float(params.get("min_support", 0.008))
    min_confidence = float(params.get("min_confidence", 0.25))
    min_lift = float(params.get("min_lift", 1.50))
    max_len_raw = params.get("max_len", 3)
    max_len = None if max_len_raw in (None, "None", "none", 0, "") else int(max_len_raw)
    apply_pruning = bool(params.get("apply_pruning", False))

    res = mine_with_metrics(
        bundle.df_train,
        algorithm=algorithm,
        min_support=min_support,
        min_confidence=min_confidence,
        min_lift=min_lift,
        max_len=max_len,
    )
    rules = prune_redundant_rules(res.rules) if apply_pruning else res.rules
    STATE["mining_res"] = res
    STATE["rules_df"] = rules
    STATE["last_params"] = {
        "algorithm": algorithm,
        "min_support": min_support,
        "min_confidence": min_confidence,
        "min_lift": min_lift,
        "max_len": max_len,
        "apply_pruning": apply_pruning,
    }

    # Lift filter ablation summary
    lift_impact = []
    for thr, label in [(1.00, "Không lọc (Lift ≥ 1.00)"), (1.30, "Cơ bản (Lift ≥ 1.30)"), (1.50, "Tối ưu (Lift ≥ 1.50)")]:
        sub_r = extract_rules(res.frequent_itemsets, min_confidence=min_confidence, min_lift=thr, max_len=max_len)
        lift_impact.append(
            {
                "label": label,
                "n_rules": len(sub_r),
                "avg_conf_pct": round(float(sub_r["confidence"].mean() * 100.0), 2) if not sub_r.empty else 0.0,
                "avg_lift": round(float(sub_r["lift"].mean()), 2) if not sub_r.empty else 0.0,
            }
        )

    # Test evaluation
    eval_test_df = evaluate_rules_on_test(rules, bundle.df_test)
    test_summary = {
        "n_test_baskets": len(bundle.df_test),
        "train_lift": round(float(rules["lift"].mean()), 2) if not rules.empty else 0.0,
        "test_lift": round(float(eval_test_df["test_lift"].mean()), 2) if not eval_test_df.empty else 0.0,
        "train_conf_pct": round(float(rules["confidence"].mean() * 100.0), 1) if not rules.empty else 0.0,
        "test_conf_pct": round(float(eval_test_df["test_confidence"].mean() * 100.0), 1) if not eval_test_df.empty else 0.0,
    }

    # Format rules for UI (including exact reverse metrics for Conviction explanation)
    n_train_tx = len(bundle.df_train)
    rules_list = []
    for idx, row in rules.iterrows():
        p_x = float(row["antecedent support"])
        p_y = float(row["consequent support"])
        p_xy = float(row["support"])
        conf_xy = float(row["confidence"])
        conv_xy = float(row["conviction"])
        conf_yx = (p_xy / p_y) if p_y > 0 else 0.0
        conv_yx = ((1.0 - p_x) / (1.0 - conf_yx)) if conf_yx < 1.0 else 999.0
        rules_list.append(
            {
                "id": idx + 1,
                "antecedents": sorted(row["antecedents"]),
                "consequents": sorted(row["consequents"]),
                "antecedent_str": ", ".join(sorted(row["antecedents"])),
                "consequent_str": ", ".join(sorted(row["consequents"])),
                "support_pct": round(p_xy * 100.0, 2),
                "support_count": int(round(p_xy * n_train_tx)),
                "p_x_pct": round(p_x * 100.0, 2),
                "p_y_pct": round(p_y * 100.0, 2),
                "confidence_pct": round(conf_xy * 100.0, 1),
                "lift": round(float(row["lift"]), 2),
                "conviction": round(conv_xy, 2) if np.isfinite(conv_xy) and conv_xy < 999 else 999.0,
                "reverse_conf_pct": round(conf_yx * 100.0, 1),
                "reverse_conv": round(conv_yx, 2) if np.isfinite(conv_yx) and conv_yx < 999 else 999.0,
                "rule_len": int(row["rule_len"]),
            }
        )

    # Shelf zones & network graph data (top 30 rules)
    zones = compute_shelf_zones(rules, max_zones=4)
    net_rules = rules.head(30)
    node_set: dict[str, int] = {}
    edges = []
    for _, row in net_rules.iterrows():
        u = ", ".join(sorted(row["antecedents"]))
        v = ", ".join(sorted(row["consequents"]))
        node_set[u] = node_set.get(u, 0) + 1
        node_set[v] = node_set.get(v, 0) + 1
        edges.append(
            {
                "source": u,
                "target": v,
                "lift": round(float(row["lift"]), 2),
                "confidence_pct": round(float(row["confidence"]) * 100.0, 1),
                "support_pct": round(float(row["support"]) * 100.0, 2),
            }
        )
    nodes = [{"id": n, "degree": deg} for n, deg in node_set.items()]

    return {
        "kpis": {
            "n_frequent_itemsets": len(res.frequent_itemsets),
            "n_rules": len(rules),
            "avg_lift": round(float(rules["lift"].mean()), 2) if not rules.empty else 0.0,
            "avg_conf_pct": round(float(rules["confidence"].mean() * 100.0), 1) if not rules.empty else 0.0,
            "runtime_sec": round(res.runtime_sec, 3),
            "n_train_tx": n_train_tx,
        },
        "lift_impact": lift_impact,
        "test_summary": test_summary,
        "rules": rules_list,
        "zones": [
            {
                "zone_id": z["zone_id"],
                "anchor_item": z["anchor_item"],
                "items": z["items"],
                "avg_lift": round(float(z["avg_lift"]), 2),
                "n_links": int(z["n_links"]),
            }
            for z in zones
        ],
        "network": {"nodes": nodes, "edges": edges},
    }


async def api_index(request: Request) -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


async def api_bootstrap(request: Request) -> JSONResponse:
    bundle = _ensure_initialized()
    ds_payload = _serialize_dataset_payload(bundle)
    mine_payload = _run_mining(STATE["last_params"] or {})
    return JSONResponse({"dataset": ds_payload, "mining": mine_payload})


async def api_select_dataset(request: Request) -> JSONResponse:
    content_type = request.headers.get("content-type", "")
    raw_text: str | None = None
    if "multipart/form-data" in content_type:
        form = await request.form()
        dataset_source = str(form.get("dataset_source", "custom"))
        filter_single = str(form.get("filter_single", "true")).lower() == "true"
        upload = form.get("file")
        if upload is not None and hasattr(upload, "read"):
            raw_bytes = await upload.read()
            raw_text = raw_bytes.decode("utf-8", errors="ignore")
        params = {
            "algorithm": str(form.get("algorithm", "FP-Growth (mlxtend)")),
            "min_support": float(form.get("min_support", 0.008)),
            "min_confidence": float(form.get("min_confidence", 0.25)),
            "min_lift": float(form.get("min_lift", 1.50)),
            "max_len": form.get("max_len", 3),
            "apply_pruning": str(form.get("apply_pruning", "false")).lower() == "true",
        }
    else:
        body = await request.json()
        dataset_source = str(body.get("dataset_source", "vn"))
        filter_single = bool(body.get("filter_single", True))
        params = body.get("mining_params", {})

    bundle = _load_bundle(dataset_source, filter_single, raw_text=raw_text)
    ds_payload = _serialize_dataset_payload(bundle)
    mine_payload = _run_mining(params)
    return JSONResponse({"dataset": ds_payload, "mining": mine_payload})


async def api_mine(request: Request) -> JSONResponse:
    body = await request.json()
    return JSONResponse(_run_mining(body))


async def api_recommend(request: Request) -> JSONResponse:
    bundle = _ensure_initialized()
    body = await request.json()
    basket: list[str] = body.get("basket", [])
    top_k = int(body.get("top_k", 5))
    rules_df: pd.DataFrame = STATE["rules_df"]
    freq_train: pd.DataFrame = STATE["freq_train"]

    rec_df, base_df = recommend_for_basket(basket, rules_df, freq_train, top_k=top_k)
    is_vn = "Thịt ba chỉ" in bundle.df_train.columns

    recs = []
    for _, r in rec_df.iterrows():
        item_name = str(r["recommended_item"])
        # For single-item or multi-item bundles, estimate combo price
        bundle_parts = [p.strip() for p in item_name.split(",")]
        price_sum = sum(_infer_meta(p, is_vn)["price"] for p in bundle_parts)
        icon = _infer_meta(bundle_parts[0], is_vn)["icon"]
        conv = float(r["conviction"])
        recs.append(
            {
                "recommended_item": item_name,
                "parts": bundle_parts,
                "icon": icon,
                "price": price_sum,
                "triggered_by": str(r["triggered_by"]),
                "confidence_pct": round(float(r["confidence"]) * 100.0, 1),
                "lift": round(float(r["lift"]), 2),
                "support_pct": round(float(r["support"]) * 100.0, 2),
                "conviction": round(conv, 2) if np.isfinite(conv) and conv < 999 else 999.0,
            }
        )

    baselines = []
    for _, r in base_df.iterrows():
        item_name = str(r["item"])
        meta = _infer_meta(item_name, is_vn)
        baselines.append(
            {
                "item": item_name,
                "icon": meta["icon"],
                "price": meta["price"],
                "support_pct": round(float(r["support_pct"]), 2),
                "lift": 1.00,
            }
        )

    return JSONResponse({"recommendations": recs, "baseline": baselines})


async def api_benchmark(request: Request) -> JSONResponse:
    bundle = _ensure_initialized()
    body = await request.json()
    include_005 = bool(body.get("include_005", False))
    min_sup_trace = float(body.get("min_support", 0.008))
    max_len_raw = body.get("max_len", 3)
    max_len = None if max_len_raw in (None, "None", 0, "") else int(max_len_raw)

    grid = [0.05, 0.03, 0.02, 0.01, 0.008] + ([0.005] if include_005 else [])
    bench_df = benchmark_algorithms(bundle.df_train, support_thresholds=grid, max_len=max_len)
    _, trace_df = apriori_custom_with_trace(bundle.df_train, min_support=min_sup_trace, max_len=max_len)

    trace_rows = []
    if not trace_df.empty:
        for _, r in trace_df.iterrows():
            ck = int(r["candidates_Ck"])
            lk = int(r["frequent_Lk"])
            trace_rows.append(
                {
                    "k": int(r["k"]),
                    "candidates_Ck": ck,
                    "frequent_Lk": lk,
                    "pruned_pct": round((ck - lk) / max(1, ck) * 100.0, 1),
                }
            )

    return JSONResponse(
        {
            "benchmark": [
                {
                    "min_support": float(r["min_support"]),
                    "algorithm": str(r["algorithm"]),
                    "runtime_sec": round(float(r["runtime_sec"]), 4),
                    "peak_memory_mb": round(float(r["peak_memory_mb"]), 3),
                    "n_itemsets": int(r["n_itemsets"]),
                }
                for _, r in bench_df.iterrows()
            ],
            "apriori_trace": trace_rows,
        }
    )


async def api_grid_search(request: Request) -> JSONResponse:
    bundle = _ensure_initialized()
    body = await request.json()
    sup_grid = [float(x) for x in body.get("support_grid", [0.008, 0.010, 0.015])]
    conf_grid = [float(x) for x in body.get("confidence_grid", [0.20, 0.25, 0.30])]
    lift_grid = [float(x) for x in body.get("lift_grid", [1.30, 1.50, 1.80])]
    len_grid = [None if x in (None, "None") else int(x) for x in body.get("max_len_grid", [2, 3])]

    gdf = run_cv_grid_search(
        bundle.train_baskets,
        support_grid=sorted(sup_grid),
        confidence_grid=sorted(conf_grid),
        lift_grid=sorted(lift_grid),
        max_len_grid=len_grid,
        n_splits=5,
    )
    rows = [
        {
            "min_support": float(r["min_support"]),
            "min_confidence": float(r["min_confidence"]),
            "min_lift": float(r["min_lift"]),
            "max_len": "None" if str(r["max_len"]) == "None" else str(int(float(r["max_len"]))),
            "n_rules_mean": round(float(r["n_rules_mean"]), 1),
            "val_lift_mean": round(float(r["val_lift_mean"]), 3),
            "val_lift_std": round(float(r["val_lift_std"]), 3),
            "val_conf_pct": round(float(r["val_conf_mean"]) * 100.0, 2),
            "val_conf_std": round(float(r["val_conf_std"]) * 100.0, 2),
            "retention_pct": round(float(r["rule_retention_pct"]), 1),
        }
        for _, r in gdf.iterrows()
    ]
    return JSONResponse({"results": rows})


async def api_ablation(request: Request) -> JSONResponse:
    bundle = _ensure_initialized()
    ab_df = run_ablation_study(
        raw_clean_baskets=bundle.clean_baskets,
        filtered_train_baskets=bundle.train_baskets,
        df_filtered_train=bundle.df_train,
        df_filtered_test=bundle.df_test,
    )
    rows = [
        {
            "step": str(r["step"]),
            "n_rules_train": int(r["n_rules_train"]),
            "cv_lift_mean": round(float(r["cv_lift_mean"]), 3),
            "cv_lift_std": round(float(r["cv_lift_std"]), 3),
            "cv_conf_mean": round(float(r["cv_conf_mean"]), 2),
            "cv_conf_std": round(float(r["cv_conf_std"]), 2),
            "test_lift": round(float(r["test_lift"]), 3),
            "test_conf": round(float(r["test_conf"]), 2),
            "delta_cv_lift": round(float(r["delta_cv_lift"]), 3),
        }
        for _, r in ab_df.iterrows()
    ]
    return JSONResponse({"ablation": rows})


async def api_export_rules(request: Request) -> Response:
    rules_df: pd.DataFrame = STATE["rules_df"]
    if rules_df.empty:
        csv_text = "antecedents,consequents,support_pct,confidence_pct,lift,conviction\n"
    else:
        out_df = pd.DataFrame(
            {
                "San pham da mua (X)": rules_df["antecedents"].apply(lambda s: ", ".join(sorted(s))),
                "Goi y mua kem (Y)": rules_df["consequents"].apply(lambda s: ", ".join(sorted(s))),
                "Support (%)": (rules_df["support"] * 100.0).round(2),
                "Confidence (%)": (rules_df["confidence"] * 100.0).round(2),
                "Lift": rules_df["lift"].round(2),
                "Conviction": rules_df["conviction"].round(2),
            }
        )
        buf = io.StringIO()
        out_df.to_csv(buf, index=False)
        csv_text = buf.getvalue()
    return Response(
        content=csv_text.encode("utf-8-sig"),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="luat_ket_hop_nhom23.csv"'},
    )


WEB_DIR.mkdir(parents=True, exist_ok=True)
app = Starlette(
    routes=[
        Route("/", api_index, methods=["GET"]),
        Route("/api/bootstrap", api_bootstrap, methods=["GET"]),
        Route("/api/dataset/select", api_select_dataset, methods=["POST"]),
        Route("/api/mine", api_mine, methods=["POST"]),
        Route("/api/recommend", api_recommend, methods=["POST"]),
        Route("/api/benchmark", api_benchmark, methods=["POST"]),
        Route("/api/part3/grid-search", api_grid_search, methods=["POST"]),
        Route("/api/part3/ablation", api_ablation, methods=["POST"]),
        Route("/api/export/rules.csv", api_export_rules, methods=["GET"]),
        Mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static"),
    ]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8501)
