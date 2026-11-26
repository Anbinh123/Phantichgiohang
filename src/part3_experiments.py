"""Part 3 experimental pipeline: 5-Fold CV on Train, Grid Search, Ablation Study, and Redundant Rule Pruning."""

from __future__ import annotations

from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.preprocessing import TransactionEncoder
from sklearn.model_selection import KFold

from src.algorithms import evaluate_rules_on_test, extract_rules
from src.data_pipeline import compute_item_frequencies


def prune_redundant_rules(rules: pd.DataFrame) -> pd.DataFrame:
    """Remove redundant rules X => Y if a subset X' < X predicts Y with confidence(X'=>Y) >= confidence(X=>Y)."""
    if rules.empty:
        return rules.copy()

    keep_indices: list[int] = []
    # Build quick lookup from (antecedent, consequent) -> confidence
    conf_map: dict[tuple[frozenset[str], frozenset[str]], float] = {
        (frozenset(r["antecedents"]), frozenset(r["consequents"])): float(r["confidence"])
        for _, r in rules.iterrows()
    }

    for idx, row in rules.iterrows():
        ant = frozenset(row["antecedents"])
        cons = frozenset(row["consequents"])
        conf = float(row["confidence"])
        is_redundant = False
        if len(ant) > 1:
            for other_ant, other_cons in conf_map:
                if other_cons == cons and other_ant < ant and conf_map[(other_ant, other_cons)] >= conf:
                    is_redundant = True
                    break
        if not is_redundant:
            keep_indices.append(idx)

    return rules.loc[keep_indices].reset_index(drop=True)


def evaluate_config_kfold(
    train_baskets: list[list[str]],
    min_support: float,
    min_confidence: float,
    min_lift: float,
    max_len: int | None,
    apply_pruning: bool = False,
    n_splits: int = 5,
    random_state: int = 42,
) -> dict[str, float]:
    """Run 5-Fold Cross-Validation inside train_baskets (never touching held-out test set)."""
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    baskets_arr = np.array(train_baskets, dtype=object)

    fold_val_lifts: list[float] = []
    fold_val_confs: list[float] = []
    fold_train_lifts: list[float] = []
    fold_train_confs: list[float] = []
    fold_n_rules: list[int] = []
    fold_coverage: list[float] = []

    for tr_idx, val_idx in kf.split(baskets_arr):
        fold_tr = baskets_arr[tr_idx].tolist()
        fold_val = baskets_arr[val_idx].tolist()

        te = TransactionEncoder()
        df_tr = pd.DataFrame(te.fit(fold_tr).transform(fold_tr), columns=te.columns_)
        known = set(te.columns_)
        sanitized_val = [[it for it in b if it in known] for b in fold_val]
        df_val = pd.DataFrame(te.transform(sanitized_val), columns=te.columns_)

        freq = fpgrowth(df_tr, min_support=min_support, use_colnames=True, max_len=max_len)
        rules = extract_rules(
            freq,
            min_confidence=min_confidence,
            min_lift=min_lift,
            max_len=max_len,
        )
        if apply_pruning and not rules.empty:
            rules = prune_redundant_rules(rules)

        fold_n_rules.append(len(rules))
        if rules.empty:
            fold_train_lifts.append(0.0)
            fold_train_confs.append(0.0)
            fold_val_lifts.append(0.0)
            fold_val_confs.append(0.0)
            fold_coverage.append(0.0)
            continue

        fold_train_lifts.append(float(rules["lift"].mean()))
        fold_train_confs.append(float(rules["confidence"].mean()))

        eval_val = evaluate_rules_on_test(rules, df_val)
        valid_val = eval_val[eval_val["test_support"] > 0]
        fold_coverage.append(len(valid_val) / len(rules) if len(rules) else 0.0)
        fold_val_lifts.append(float(eval_val["test_lift"].mean()) if not eval_val.empty else 0.0)
        fold_val_confs.append(float(eval_val["test_confidence"].mean()) if not eval_val.empty else 0.0)

    return {
        "n_rules_mean": float(np.mean(fold_n_rules)),
        "n_rules_std": float(np.std(fold_n_rules, ddof=1)),
        "train_lift_mean": float(np.mean(fold_train_lifts)),
        "train_conf_mean": float(np.mean(fold_train_confs)),
        "val_lift_mean": float(np.mean(fold_val_lifts)),
        "val_lift_std": float(np.std(fold_val_lifts, ddof=1)),
        "val_conf_mean": float(np.mean(fold_val_confs)),
        "val_conf_std": float(np.std(fold_val_confs, ddof=1)),
        "rule_retention_pct": float(np.mean(fold_coverage) * 100.0),
    }


def run_cv_grid_search(
    train_baskets: list[list[str]],
    support_grid: list[float] | None = None,
    confidence_grid: list[float] | None = None,
    lift_grid: list[float] | None = None,
    max_len_grid: list[int | None] | None = None,
    n_splits: int = 5,
) -> pd.DataFrame:
    """Grid search over hyperparameters using 5-Fold CV inside train_baskets only."""
    support_grid = support_grid or [0.005, 0.008, 0.010, 0.015]
    confidence_grid = confidence_grid or [0.20, 0.25, 0.30]
    lift_grid = lift_grid or [1.30, 1.50, 1.80]
    max_len_grid = max_len_grid or [2, 3, None]

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    baskets_arr = np.array(train_baskets, dtype=object)

    # Mine FP-Growth ONCE per fold at min(support_grid) and max_len=max(grid), then reuse
    min_sup_base = min(support_grid)
    max_len_base = None if any(m is None for m in max_len_grid) else max(int(m) for m in max_len_grid)

    fold_cache: list[tuple[pd.DataFrame, pd.DataFrame]] = []
    for tr_idx, val_idx in kf.split(baskets_arr):
        fold_tr = baskets_arr[tr_idx].tolist()
        fold_val = baskets_arr[val_idx].tolist()
        te = TransactionEncoder()
        df_tr = pd.DataFrame(te.fit(fold_tr).transform(fold_tr), columns=te.columns_)
        known = set(te.columns_)
        df_val = pd.DataFrame(
            te.transform([[it for it in b if it in known] for b in fold_val]),
            columns=te.columns_,
        )
        base_freq = fpgrowth(df_tr, min_support=min_sup_base, use_colnames=True, max_len=max_len_base)
        base_freq["itemset_len"] = base_freq["itemsets"].apply(len)
        fold_cache.append((base_freq, df_val))

    rows: list[dict[str, object]] = []
    min_conf_base = min(confidence_grid)
    min_lift_base = min(lift_grid)

    # Pre-generate base rules per (fold, sup) at min_conf_base & min_lift_base, then slice!
    for sup in support_grid:
        fold_base_rules: list[tuple[pd.DataFrame, pd.DataFrame]] = []
        for base_freq, df_val in fold_cache:
            freq_sub = base_freq[base_freq["support"] >= sup].drop(columns=["itemset_len"])
            rules_sub = extract_rules(
                freq_sub,
                min_confidence=min_conf_base,
                min_lift=min_lift_base,
                max_len=max_len_base,
            )
            eval_base = evaluate_rules_on_test(rules_sub, df_val)
            if not rules_sub.empty and not eval_base.empty:
                # Merge train metrics + validation metrics once per rule
                merged = rules_sub[["confidence", "lift", "rule_len"]].reset_index(drop=True).join(
                    eval_base[["test_support", "test_confidence", "test_lift"]]
                )
            else:
                merged = pd.DataFrame(
                    columns=["confidence", "lift", "rule_len", "test_support", "test_confidence", "test_lift"]
                )
            fold_base_rules.append((merged, df_val))

        for conf, lift_thr, mlen in product(confidence_grid, lift_grid, max_len_grid):
            val_lifts, val_confs, tr_lifts, tr_confs, n_rules_list, ret_list = [], [], [], [], [], []
            for merged, _ in fold_base_rules:
                sub = merged[(merged["confidence"] >= conf) & (merged["lift"] >= lift_thr)]
                if mlen is not None:
                    sub = sub[sub["rule_len"] <= mlen]
                n_rules_list.append(len(sub))
                if sub.empty:
                    tr_lifts.append(0.0)
                    tr_confs.append(0.0)
                    val_lifts.append(0.0)
                    val_confs.append(0.0)
                    ret_list.append(0.0)
                else:
                    tr_lifts.append(float(sub["lift"].mean()))
                    tr_confs.append(float(sub["confidence"].mean()))
                    val_lifts.append(float(sub["test_lift"].mean()))
                    val_confs.append(float(sub["test_confidence"].mean()))
                    ret_list.append(float((sub["test_support"] > 0).mean() * 100.0))

            rows.append(
                {
                    "min_support": sup,
                    "min_confidence": conf,
                    "min_lift": lift_thr,
                    "max_len": "None" if mlen is None else mlen,
                    "n_rules_mean": float(np.mean(n_rules_list)),
                    "n_rules_std": float(np.std(n_rules_list, ddof=1)),
                    "train_lift_mean": float(np.mean(tr_lifts)),
                    "train_conf_mean": float(np.mean(tr_confs)),
                    "val_lift_mean": float(np.mean(val_lifts)),
                    "val_lift_std": float(np.std(val_lifts, ddof=1)),
                    "val_conf_mean": float(np.mean(val_confs)),
                    "val_conf_std": float(np.std(val_confs, ddof=1)),
                    "rule_retention_pct": float(np.mean(ret_list)),
                }
            )

    df = pd.DataFrame(rows)
    return df.sort_values(["val_lift_mean", "val_conf_mean"], ascending=False).reset_index(drop=True)


def run_ablation_study(
    raw_clean_baskets: list[list[str]],
    filtered_train_baskets: list[list[str]],
    df_filtered_train: pd.DataFrame,
    df_filtered_test: pd.DataFrame,
) -> pd.DataFrame:
    """Unified ablation study measuring each improvement step on 5-Fold CV and Hold-out Test."""
    from sklearn.model_selection import train_test_split

    # Raw split (including 1-item baskets) for initial baseline & uncleaned FP-Growth
    raw_train, raw_test = train_test_split(raw_clean_baskets, test_size=0.20, random_state=42)
    te_raw = TransactionEncoder()
    df_raw_tr = pd.DataFrame(te_raw.fit(raw_train).transform(raw_train), columns=te_raw.columns_)
    known_raw = set(te_raw.columns_)
    df_raw_te = pd.DataFrame(
        te_raw.transform([[i for i in b if i in known_raw] for b in raw_test]),
        columns=te_raw.columns_,
    )

    # 1. Baseline (Most Popular on filtered train -> evaluated on filtered test)
    freq_tr = compute_item_frequencies(filtered_train_baskets)
    top_item = str(freq_tr.iloc[0]["item"])
    baseline_train_conf = float(freq_tr.iloc[0]["support_pct"] / 100.0)
    baseline_test_conf = float(df_filtered_test[top_item].mean()) if top_item in df_filtered_test.columns else 0.0

    records: list[dict[str, object]] = [
        {
            "step": f"0. Mô hình cơ sở (Most Popular: {top_item})",
            "n_rules_train": 1,
            "cv_lift_mean": 1.00,
            "cv_lift_std": 0.00,
            "cv_conf_mean": baseline_train_conf * 100.0,
            "cv_conf_std": 0.00,
            "test_lift": 1.00,
            "test_conf": baseline_test_conf * 100.0,
        }
    ]

    # 2. Initial FP-Growth on raw data (unfiltered <2 items, min_lift=1.30, max_len=None)
    cv_raw = evaluate_config_kfold(
        raw_train,
        min_support=0.008,
        min_confidence=0.25,
        min_lift=1.30,
        max_len=None,
        apply_pruning=False,
    )
    freq_raw = fpgrowth(df_raw_tr, min_support=0.008, use_colnames=True)
    rules_raw = extract_rules(freq_raw, min_confidence=0.25, min_lift=1.30, max_len=None)
    test_raw = evaluate_rules_on_test(rules_raw, df_raw_te)
    records.append(
        {
            "step": "1. FP-Growth ban đầu (dữ liệu thô, Lift≥1.30)",
            "n_rules_train": len(rules_raw),
            "cv_lift_mean": cv_raw["val_lift_mean"],
            "cv_lift_std": cv_raw["val_lift_std"],
            "cv_conf_mean": cv_raw["val_conf_mean"] * 100.0,
            "cv_conf_std": cv_raw["val_conf_std"] * 100.0,
            "test_lift": float(test_raw["test_lift"].mean()) if not test_raw.empty else 0.0,
            "test_conf": float(test_raw["test_confidence"].mean() * 100.0) if not test_raw.empty else 0.0,
        }
    )

    # 3. + Data improvement: Filter out 2,159 single-item baskets
    cv_filt = evaluate_config_kfold(
        filtered_train_baskets,
        min_support=0.008,
        min_confidence=0.25,
        min_lift=1.30,
        max_len=None,
        apply_pruning=False,
    )
    freq_filt = fpgrowth(df_filtered_train, min_support=0.008, use_colnames=True)
    rules_filt = extract_rules(freq_filt, min_confidence=0.25, min_lift=1.30, max_len=None)
    test_filt = evaluate_rules_on_test(rules_filt, df_filtered_test)
    records.append(
        {
            "step": "2. + Lọc giỏ hàng < 2 món (giảm nhiễu đơn lẻ)",
            "n_rules_train": len(rules_filt),
            "cv_lift_mean": cv_filt["val_lift_mean"],
            "cv_lift_std": cv_filt["val_lift_std"],
            "cv_conf_mean": cv_filt["val_conf_mean"] * 100.0,
            "cv_conf_std": cv_filt["val_conf_std"] * 100.0,
            "test_lift": float(test_filt["test_lift"].mean()) if not test_filt.empty else 0.0,
            "test_conf": float(test_filt["test_confidence"].mean() * 100.0) if not test_filt.empty else 0.0,
        }
    )

    # 4. + Hyperparameter tuning (min_lift=1.50, max_len=3)
    cv_tuned = evaluate_config_kfold(
        filtered_train_baskets,
        min_support=0.008,
        min_confidence=0.25,
        min_lift=1.50,
        max_len=3,
        apply_pruning=False,
    )
    freq_tuned = fpgrowth(df_filtered_train, min_support=0.008, use_colnames=True, max_len=3)
    rules_tuned = extract_rules(freq_tuned, min_confidence=0.25, min_lift=1.50, max_len=3)
    test_tuned = evaluate_rules_on_test(rules_tuned, df_filtered_test)
    records.append(
        {
            "step": "3. + Tối ưu siêu tham số (Lift≥1.50, max_len=3)",
            "n_rules_train": len(rules_tuned),
            "cv_lift_mean": cv_tuned["val_lift_mean"],
            "cv_lift_std": cv_tuned["val_lift_std"],
            "cv_conf_mean": cv_tuned["val_conf_mean"] * 100.0,
            "cv_conf_std": cv_tuned["val_conf_std"] * 100.0,
            "test_lift": float(test_tuned["test_lift"].mean()) if not test_tuned.empty else 0.0,
            "test_conf": float(test_tuned["test_confidence"].mean() * 100.0) if not test_tuned.empty else 0.0,
        }
    )

    # 5. + Post-processing: Redundant rule pruning
    cv_pruned = evaluate_config_kfold(
        filtered_train_baskets,
        min_support=0.008,
        min_confidence=0.25,
        min_lift=1.50,
        max_len=3,
        apply_pruning=True,
    )
    rules_pruned = prune_redundant_rules(rules_tuned)
    test_pruned = evaluate_rules_on_test(rules_pruned, df_filtered_test)
    records.append(
        {
            "step": "4. + Hậu xử lý cắt tỉa luật dư thừa (Pruning)",
            "n_rules_train": len(rules_pruned),
            "cv_lift_mean": cv_pruned["val_lift_mean"],
            "cv_lift_std": cv_pruned["val_lift_std"],
            "cv_conf_mean": cv_pruned["val_conf_mean"] * 100.0,
            "cv_conf_std": cv_pruned["val_conf_std"] * 100.0,
            "test_lift": float(test_pruned["test_lift"].mean()) if not test_pruned.empty else 0.0,
            "test_conf": float(test_pruned["test_confidence"].mean() * 100.0) if not test_pruned.empty else 0.0,
        }
    )

    df_out = pd.DataFrame(records)
    df_out["delta_cv_lift"] = df_out["cv_lift_mean"].diff().fillna(0.0)
    return df_out
