"""Data loading, cleaning, EDA statistics, and train/test splitting for Market Basket Analysis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from sklearn.model_selection import train_test_split


DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "groceries.csv"
VN_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sieu_thi_viet_nam.csv"


@dataclass
class DatasetBundle:
    """Container for raw, cleaned, split, and one-hot encoded transaction data."""

    raw_baskets: list[list[str]]
    clean_baskets: list[list[str]]
    filtered_baskets: list[list[str]]
    train_baskets: list[list[str]]
    test_baskets: list[list[str]]
    df_train: pd.DataFrame
    df_test: pd.DataFrame
    stats: dict[str, float | int]


def parse_csv_lines(lines: Iterable[str]) -> list[list[str]]:
    """Parse basket-per-line CSV or tabular InvoiceNo/Description CSV (Online Retail style)."""
    raw_lines = [line.strip() for line in lines if line.strip()]
    if not raw_lines:
        return []

    # Auto-detect tabular Online Retail / Invoice-Item CSV with header
    first_cols = [c.strip().lower() for c in raw_lines[0].split(",")]
    invoice_col_names = {"invoiceno", "invoice", "transaction", "transactionid", "tid", "order_id"}
    item_col_names = {"description", "item", "product", "itemdescription"}
    inv_idx = next((i for i, c in enumerate(first_cols) if c in invoice_col_names), None)
    item_idx = next((i for i, c in enumerate(first_cols) if c in item_col_names), None)

    if inv_idx is not None and item_idx is not None and len(raw_lines) > 1:
        import csv

        grouped: dict[str, list[str]] = {}
        reader = csv.reader(raw_lines[1:])
        for row in reader:
            if len(row) <= max(inv_idx, item_idx):
                continue
            inv = row[inv_idx].strip()
            item = row[item_idx].strip()
            # Skip cancelled invoices (e.g., InvoiceNo starting with 'C' in Online Retail)
            if not inv or not item or inv.upper().startswith("C"):
                continue
            grouped.setdefault(inv, []).append(item)
        return list(grouped.values())

    # Standard Groceries basket-per-line format
    baskets: list[list[str]] = []
    for line in raw_lines:
        items = [item.strip() for item in line.split(",") if item.strip()]
        if items:
            baskets.append(items)
    return baskets


def load_raw_baskets(source: Path | str | Iterable[str] = DEFAULT_DATA_PATH) -> list[list[str]]:
    """Load transaction baskets from a CSV file path or line iterable."""
    if isinstance(source, (str, Path)):
        path = Path(source)
        with path.open("r", encoding="utf-8") as fh:
            return parse_csv_lines(fh)
    return parse_csv_lines(source)


def prepare_dataset(
    raw_baskets: list[list[str]],
    min_basket_size: int = 2,
    test_size: float = 0.20,
    random_state: int = 42,
) -> DatasetBundle:
    """Clean, deduplicate, filter short baskets, split 80/20, and one-hot encode without leakage."""
    # Deduplicate items within each basket while preserving deterministic ordering
    clean_baskets: list[list[str]] = []
    duplicate_items_removed = 0
    for basket in raw_baskets:
        unique_items = sorted(set(basket))
        duplicate_items_removed += len(basket) - len(unique_items)
        clean_baskets.append(unique_items)

    raw_lengths = np.array([len(b) for b in clean_baskets], dtype=int)
    single_item_count = int(np.sum(raw_lengths < min_basket_size))
    filtered_baskets = [b for b in clean_baskets if len(b) >= min_basket_size]

    train_baskets, test_baskets = train_test_split(
        filtered_baskets,
        test_size=test_size,
        random_state=random_state,
    )

    # Fit TransactionEncoder ONLY on train_baskets to prevent data leakage
    te = TransactionEncoder()
    train_matrix = te.fit(train_baskets).transform(train_baskets)
    df_train = pd.DataFrame(train_matrix, columns=te.columns_)

    # Transform test_baskets using the vocabulary learned from training data
    known_items = set(te.columns_)
    sanitized_test = [[item for item in b if item in known_items] for b in test_baskets]
    test_matrix = te.transform(sanitized_test)
    df_test = pd.DataFrame(test_matrix, columns=te.columns_)

    # Raw full-dataset one-hot stats for EDA
    te_full = TransactionEncoder()
    full_matrix = te_full.fit(clean_baskets).transform(clean_baskets)
    total_cells = full_matrix.shape[0] * full_matrix.shape[1]
    sparsity = 1.0 - (float(full_matrix.sum()) / total_cells) if total_cells else 0.0

    train_density = float(train_matrix.sum()) / (train_matrix.shape[0] * train_matrix.shape[1])
    test_density = float(test_matrix.sum()) / (test_matrix.shape[0] * test_matrix.shape[1])

    stats = {
        "n_raw_transactions": len(clean_baskets),
        "n_unique_items": len(te_full.columns_),
        "duplicate_items_removed": duplicate_items_removed,
        "single_item_count": single_item_count,
        "single_item_pct": (single_item_count / len(clean_baskets) * 100.0) if clean_baskets else 0.0,
        "n_filtered_transactions": len(filtered_baskets),
        "n_train": len(train_baskets),
        "n_test": len(test_baskets),
        "n_train_features": df_train.shape[1],
        "avg_basket_size": float(np.mean(raw_lengths)) if len(raw_lengths) else 0.0,
        "std_basket_size": float(np.std(raw_lengths, ddof=1)) if len(raw_lengths) > 1 else 0.0,
        "median_basket_size": float(np.median(raw_lengths)) if len(raw_lengths) else 0.0,
        "max_basket_size": int(np.max(raw_lengths)) if len(raw_lengths) else 0,
        "sparsity_pct": sparsity * 100.0,
        "train_density_pct": train_density * 100.0,
        "test_density_pct": test_density * 100.0,
    }

    return DatasetBundle(
        raw_baskets=raw_baskets,
        clean_baskets=clean_baskets,
        filtered_baskets=filtered_baskets,
        train_baskets=train_baskets,
        test_baskets=test_baskets,
        df_train=df_train,
        df_test=df_test,
        stats=stats,
    )


def compute_item_frequencies(baskets: list[list[str]]) -> pd.DataFrame:
    """Return item counts and support percentages sorted descending."""
    if not baskets:
        return pd.DataFrame(columns=["item", "count", "support_pct"])

    counts: dict[str, int] = {}
    for basket in baskets:
        for item in set(basket):
            counts[item] = counts.get(item, 0) + 1

    n_tx = len(baskets)
    df = pd.DataFrame(
        [
            {"item": item, "count": cnt, "support_pct": cnt / n_tx * 100.0}
            for item, cnt in counts.items()
        ]
    )
    return df.sort_values("count", ascending=False).reset_index(drop=True)


def compute_cooccurrence_matrix(baskets: list[list[str]], top_n: int = 8) -> pd.DataFrame:
    """Compute percentage co-occurrence matrix for the top N most frequent items."""
    freq_df = compute_item_frequencies(baskets)
    top_items = freq_df["item"].head(top_n).tolist()
    if not top_items or not baskets:
        return pd.DataFrame()

    te = TransactionEncoder()
    mat = te.fit(baskets).transform(baskets).astype(int)
    df_oh = pd.DataFrame(mat, columns=te.columns_)[top_items]
    cooc = (df_oh.T @ df_oh) / len(baskets) * 100.0
    return cooc
