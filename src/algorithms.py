"""Association rule mining algorithms (Apriori, ECLAT, FP-Growth), evaluation, and recommendations."""

from __future__ import annotations

import gc
import time
import tracemalloc
from dataclasses import dataclass
from itertools import combinations
from typing import Callable

import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import association_rules, fpgrowth


@dataclass
class MiningResult:
    """Holds frequent itemsets, filtered association rules, and runtime metrics."""

    algorithm: str
    frequent_itemsets: pd.DataFrame
    rules: pd.DataFrame
    runtime_sec: float
    peak_memory_mb: float


def _df_to_transactions(df_bool: pd.DataFrame) -> list[frozenset[int]]:
    """Convert one-hot DataFrame to horizontal list of integer item-index frozensets."""
    matrix = df_bool.to_numpy(dtype=bool)
    return [frozenset(np.flatnonzero(row).tolist()) for row in matrix]


def apriori_custom_with_trace(
    df_bool: pd.DataFrame,
    min_support: float = 0.008,
    max_len: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Custom horizontal Python Apriori returning (frequent_itemsets, level_trace_df)."""
    n_tx = len(df_bool)
    if n_tx == 0:
        return pd.DataFrame(columns=["support", "itemsets"]), pd.DataFrame()

    min_count = min_support * n_tx
    columns = list(df_bool.columns)
    transactions = _df_to_transactions(df_bool)

    # Level 1 scan
    counts_1: dict[int, int] = {}
    for tx in transactions:
        for item_idx in tx:
            counts_1[item_idx] = counts_1.get(item_idx, 0) + 1

    freq_by_k: dict[int, list[tuple[frozenset[int], float]]] = {}
    level_1 = [
        (frozenset((idx,)), cnt / n_tx)
        for idx, cnt in sorted(counts_1.items())
        if cnt >= min_count
    ]
    trace_rows: list[dict[str, int]] = [
        {"k": 1, "candidates_Ck": len(counts_1), "frequent_Lk": len(level_1)}
    ]

    if not level_1:
        return pd.DataFrame(columns=["support", "itemsets"]), pd.DataFrame(trace_rows)

    freq_by_k[1] = level_1
    k = 2
    while freq_by_k.get(k - 1) and (max_len is None or k <= max_len):
        prev_sets = sorted((fs for fs, _ in freq_by_k[k - 1]), key=lambda s: tuple(sorted(s)))
        prev_lookup = set(prev_sets)
        candidates: set[frozenset[int]] = set()

        # Join step + anti-monotone subset pruning
        n_prev = len(prev_sets)
        for i in range(n_prev):
            s1 = prev_sets[i]
            for j in range(i + 1, n_prev):
                union_set = s1 | prev_sets[j]
                if len(union_set) == k:
                    if all(frozenset(sub) in prev_lookup for sub in combinations(union_set, k - 1)):
                        candidates.add(union_set)

        if not candidates:
            break

        # Horizontal DB scan for candidate support counting
        cand_counts: dict[frozenset[int], int] = {c: 0 for c in candidates}
        for tx in transactions:
            if len(tx) >= k:
                for cand in candidates:
                    if cand.issubset(tx):
                        cand_counts[cand] += 1

        next_level = [
            (cand, cnt / n_tx)
            for cand, cnt in cand_counts.items()
            if cnt >= min_count
        ]
        trace_rows.append(
            {"k": k, "candidates_Ck": len(candidates), "frequent_Lk": len(next_level)}
        )
        if not next_level:
            break
        freq_by_k[k] = next_level
        k += 1

    rows = [
        {"support": sup, "itemsets": frozenset(columns[i] for i in fs)}
        for items in freq_by_k.values()
        for fs, sup in items
    ]
    return pd.DataFrame(rows, columns=["support", "itemsets"]), pd.DataFrame(trace_rows)


def apriori_custom(
    df_bool: pd.DataFrame,
    min_support: float = 0.008,
    max_len: int | None = None,
) -> pd.DataFrame:
    """Custom Python implementation of horizontal Apriori with anti-monotone pruning."""
    freq_df, _ = apriori_custom_with_trace(df_bool, min_support=min_support, max_len=max_len)
    return freq_df


def eclat_custom(
    df_bool: pd.DataFrame,
    min_support: float = 0.008,
    max_len: int | None = None,
) -> pd.DataFrame:
    """Custom Python implementation of ECLAT using vertical TID-sets and DFS intersection."""
    n_tx = len(df_bool)
    if n_tx == 0:
        return pd.DataFrame(columns=["support", "itemsets"])

    min_count = min_support * n_tx
    columns = list(df_bool.columns)
    matrix = df_bool.to_numpy(dtype=bool)

    initial_items: list[tuple[tuple[int, ...], set[int]]] = []
    for idx in range(len(columns)):
        tids = set(np.flatnonzero(matrix[:, idx]).tolist())
        if len(tids) >= min_count:
            initial_items.append(((idx,), tids))

    results: list[dict[str, object]] = []

    def dfs(prefix_items: list[tuple[tuple[int, ...], set[int]]]) -> None:
        for i, (item_tuple, tid_set) in enumerate(prefix_items):
            results.append(
                {
                    "support": len(tid_set) / n_tx,
                    "itemsets": frozenset(columns[idx] for idx in item_tuple),
                }
            )
            if max_len is not None and len(item_tuple) >= max_len:
                continue

            suffix: list[tuple[tuple[int, ...], set[int]]] = []
            for j in range(i + 1, len(prefix_items)):
                other_tuple, other_tids = prefix_items[j]
                inter = tid_set & other_tids
                if len(inter) >= min_count:
                    merged = tuple(sorted(set(item_tuple) | set(other_tuple)))
                    suffix.append((merged, inter))
            if suffix:
                dfs(suffix)

    dfs(initial_items)
    return pd.DataFrame(results, columns=["support", "itemsets"])


def run_fpgrowth(
    df_bool: pd.DataFrame,
    min_support: float = 0.008,
    max_len: int | None = None,
) -> pd.DataFrame:
    """Run mlxtend FP-Growth returning frequent itemsets."""
    return fpgrowth(df_bool, min_support=min_support, use_colnames=True, max_len=max_len)


ALGORITHM_RUNNERS: dict[str, Callable[[pd.DataFrame, float, int | None], pd.DataFrame]] = {
    "FP-Growth (mlxtend)": run_fpgrowth,
    "Apriori (Python)": apriori_custom,
    "ECLAT (Python)": eclat_custom,
}


def extract_rules(
    frequent_itemsets: pd.DataFrame,
    min_confidence: float = 0.25,
    min_lift: float = 1.50,
    max_len: int | None = 3,
) -> pd.DataFrame:
    """Generate and filter association rules by confidence, lift, and rule length."""
    expected_cols = [
        "antecedents",
        "consequents",
        "antecedent support",
        "consequent support",
        "support",
        "confidence",
        "lift",
        "leverage",
        "conviction",
        "rule_len",
    ]
    if frequent_itemsets.empty:
        return pd.DataFrame(columns=expected_cols)

    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    if rules.empty:
        return pd.DataFrame(columns=expected_cols)

    rules = rules[rules["lift"] >= min_lift].copy()
    rules["rule_len"] = rules["antecedents"].apply(len) + rules["consequents"].apply(len)
    if max_len is not None:
        rules = rules[rules["rule_len"] <= max_len].copy()

    rules = rules.sort_values(["lift", "confidence", "support"], ascending=False).reset_index(drop=True)
    return rules


def _measure_algorithm(
    runner: Callable[[pd.DataFrame, float, int | None], pd.DataFrame],
    df_bool: pd.DataFrame,
    min_support: float,
    max_len: int | None,
) -> tuple[pd.DataFrame, float, float]:
    """Measure clean wall-clock runtime (without tracemalloc overhead) and peak Python heap separately."""
    gc.collect()
    start = time.perf_counter()
    freq = runner(df_bool, min_support, max_len)
    elapsed = time.perf_counter() - start

    gc.collect()
    tracemalloc.start()
    _ = runner(df_bool, min_support, max_len)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return freq, elapsed, peak / (1024 * 1024)


def mine_with_metrics(
    df_bool: pd.DataFrame,
    algorithm: str = "FP-Growth (mlxtend)",
    min_support: float = 0.008,
    min_confidence: float = 0.25,
    min_lift: float = 1.50,
    max_len: int | None = 3,
) -> MiningResult:
    """Run a selected frequent itemset mining algorithm and measure runtime and peak memory."""
    runner = ALGORITHM_RUNNERS[algorithm]
    freq, elapsed, peak_mb = _measure_algorithm(runner, df_bool, min_support, max_len)

    rules = extract_rules(freq, min_confidence=min_confidence, min_lift=min_lift, max_len=max_len)
    return MiningResult(
        algorithm=algorithm,
        frequent_itemsets=freq,
        rules=rules,
        runtime_sec=elapsed,
        peak_memory_mb=peak_mb,
    )


def evaluate_rules_on_test(rules: pd.DataFrame, df_test: pd.DataFrame) -> pd.DataFrame:
    """Evaluate discovered rules independently on the held-out test matrix."""
    if rules.empty or df_test.empty:
        return pd.DataFrame()

    n_test = len(df_test)
    col_arrays = {col: df_test[col].to_numpy(dtype=bool) for col in df_test.columns}
    col_set = set(col_arrays.keys())
    rows: list[dict[str, object]] = []

    for ant_fs, cons_fs, sup, conf, lift, conv in zip(
        rules["antecedents"],
        rules["consequents"],
        rules["support"],
        rules["confidence"],
        rules["lift"],
        rules["conviction"],
    ):
        ant = list(ant_fs)
        cons = list(cons_fs)
        if not set(ant).issubset(col_set) or not set(cons).issubset(col_set):
            continue

        ant_mask = col_arrays[ant[0]]
        for item in ant[1:]:
            ant_mask = ant_mask & col_arrays[item]

        cons_mask = col_arrays[cons[0]]
        for item in cons[1:]:
            cons_mask = cons_mask & col_arrays[item]

        both_mask = ant_mask & cons_mask

        ant_sup = float(ant_mask.sum() / n_test)
        cons_sup = float(cons_mask.sum() / n_test)
        both_sup = float(both_mask.sum() / n_test)
        test_conf = (both_sup / ant_sup) if ant_sup > 0 else 0.0
        test_lift = (test_conf / cons_sup) if cons_sup > 0 else 0.0

        rows.append(
            {
                "rule": f"{', '.join(sorted(ant))} -> {', '.join(sorted(cons))}",
                "train_support": float(sup),
                "test_support": both_sup,
                "train_confidence": float(conf),
                "test_confidence": test_conf,
                "train_lift": float(lift),
                "test_lift": test_lift,
                "conviction": float(conv),
            }
        )

    return pd.DataFrame(rows)


def benchmark_algorithms(
    df_bool: pd.DataFrame,
    support_thresholds: list[float],
    max_len: int | None = 3,
) -> pd.DataFrame:
    """Compare runtime, peak memory, and frequent itemset count across support thresholds."""
    records: list[dict[str, object]] = []
    for sup in support_thresholds:
        for algo_name, runner in ALGORITHM_RUNNERS.items():
            freq, elapsed, peak_mb = _measure_algorithm(runner, df_bool, sup, max_len)
            records.append(
                {
                    "min_support": sup,
                    "algorithm": algo_name,
                    "runtime_sec": elapsed,
                    "peak_memory_mb": peak_mb,
                    "n_itemsets": len(freq),
                }
            )
    return pd.DataFrame(records)


def recommend_for_basket(
    basket_items: list[str],
    rules: pd.DataFrame,
    popular_items_df: pd.DataFrame,
    top_k: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Recommend companion products from association rules alongside Most Popular baseline."""
    basket_set = set(basket_items)

    # Baseline: Most Popular items not already in basket
    baseline_df = (
        popular_items_df[~popular_items_df["item"].isin(basket_set)]
        .head(top_k)
        .copy()
    )
    baseline_df["confidence_est"] = baseline_df["support_pct"] / 100.0
    baseline_df["lift"] = 1.00

    if not basket_set or rules.empty:
        return pd.DataFrame(), baseline_df

    matched: list[dict[str, object]] = []
    for _, row in rules.iterrows():
        ant = set(row["antecedents"])
        cons = set(row["consequents"])
        if ant.issubset(basket_set) and not cons.intersection(basket_set):
            matched.append(
                {
                    "recommended_item": ", ".join(sorted(cons)),
                    "triggered_by": ", ".join(sorted(ant)),
                    "confidence": float(row["confidence"]),
                    "lift": float(row["lift"]),
                    "support": float(row["support"]),
                    "conviction": float(row["conviction"]),
                }
            )

    if not matched:
        return pd.DataFrame(), baseline_df

    rec_df = pd.DataFrame(matched)
    # Keep strongest rule per recommended product bundle
    rec_df = (
        rec_df.sort_values(["lift", "confidence", "support"], ascending=False)
        .drop_duplicates(subset=["recommended_item"])
        .head(top_k)
        .reset_index(drop=True)
    )
    return rec_df, baseline_df


def compute_shelf_zones(rules: pd.DataFrame, max_zones: int = 4) -> list[dict[str, object]]:
    """Cluster strongly co-purchased individual items into retail shelf zones via modularity."""
    if rules.empty:
        return []

    import networkx as nx

    g = nx.Graph()
    for _, row in rules.iterrows():
        for a in row["antecedents"]:
            for b in row["consequents"]:
                if a == b:
                    continue
                weight = float(row["lift"])
                if g.has_edge(a, b):
                    g[a][b]["weight"] = max(g[a][b]["weight"], weight)
                else:
                    g.add_edge(a, b, weight=weight)

    if g.number_of_nodes() == 0:
        return []

    communities = list(nx.community.greedy_modularity_communities(g, weight="weight"))
    zones: list[dict[str, object]] = []
    for idx, comm in enumerate(communities[:max_zones], start=1):
        items_sorted = sorted(comm, key=lambda n: g.degree(n, weight="weight"), reverse=True)
        sub = g.subgraph(comm)
        avg_lift = (
            float(np.mean([d["weight"] for _, _, d in sub.edges(data=True)]))
            if sub.number_of_edges() > 0
            else 1.0
        )
        zones.append(
            {
                "zone_id": idx,
                "anchor_item": items_sorted[0],
                "items": items_sorted,
                "avg_lift": avg_lift,
                "n_links": sub.number_of_edges(),
            }
        )
    return zones


def format_rules_display(rules: pd.DataFrame) -> pd.DataFrame:
    """Format association rules DataFrame for clean UI presentation."""
    if rules.empty:
        return pd.DataFrame()
    return pd.DataFrame(
        {
            "Sản phẩm đã mua (Vế trái X)": rules["antecedents"].apply(lambda s: ", ".join(sorted(s))),
            "Gợi ý mua kèm (Vế phải Y)": rules["consequents"].apply(lambda s: ", ".join(sorted(s))),
            "Support (%)": (rules["support"] * 100.0).round(2),
            "Confidence (%)": (rules["confidence"] * 100.0).round(2),
            "Lift": rules["lift"].round(2),
            "Conviction": rules["conviction"].replace([np.inf, -np.inf], np.nan).round(2),
            "Độ dài luật": rules["rule_len"],
        }
    )
