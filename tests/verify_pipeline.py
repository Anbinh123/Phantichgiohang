"""Verification script ensuring pipeline fidelity to Nhóm 23 report and algorithmic consistency."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.algorithms import (
    apriori_custom_with_trace,
    compute_shelf_zones,
    evaluate_rules_on_test,
    mine_with_metrics,
    recommend_for_basket,
)
from src.data_pipeline import (
    compute_item_frequencies,
    load_raw_baskets,
    parse_csv_lines,
    prepare_dataset,
)


def main() -> None:
    raw = load_raw_baskets()
    bundle = prepare_dataset(raw, min_basket_size=2, test_size=0.20, random_state=42)

    print("Stats:", bundle.stats)
    assert bundle.stats["n_raw_transactions"] == 9835
    assert bundle.stats["n_unique_items"] == 169
    assert bundle.stats["single_item_count"] == 2159
    assert bundle.stats["n_filtered_transactions"] == 7676
    assert bundle.stats["n_train"] == 6140
    assert bundle.stats["n_test"] == 1536

    # Check consistency across Apriori, ECLAT, and FP-Growth at min_support=0.008, min_lift=1.30
    res_fp_130 = mine_with_metrics(
        bundle.df_train,
        algorithm="FP-Growth (mlxtend)",
        min_support=0.008,
        min_confidence=0.25,
        min_lift=1.30,
        max_len=None,
    )
    res_apr_130 = mine_with_metrics(
        bundle.df_train,
        algorithm="Apriori (Python)",
        min_support=0.008,
        min_confidence=0.25,
        min_lift=1.30,
        max_len=None,
    )
    res_ecl_130 = mine_with_metrics(
        bundle.df_train,
        algorithm="ECLAT (Python)",
        min_support=0.008,
        min_confidence=0.25,
        min_lift=1.30,
        max_len=None,
    )

    fp_sets = set(res_fp_130.frequent_itemsets["itemsets"])
    apr_sets = set(res_apr_130.frequent_itemsets["itemsets"])
    ecl_sets = set(res_ecl_130.frequent_itemsets["itemsets"])
    assert fp_sets == apr_sets == ecl_sets, (
        f"Itemset mismatch: FP={len(fp_sets)}, Apr={len(apr_sets)}, Ecl={len(ecl_sets)}"
    )
    assert len(res_fp_130.rules) == len(res_apr_130.rules) == len(res_ecl_130.rules)

    print(
        f"[Lift>=1.30] Rules={len(res_fp_130.rules)}, "
        f"ConfTB={res_fp_130.rules['confidence'].mean()*100:.2f}%, "
        f"LiftTB={res_fp_130.rules['lift'].mean():.2f}, "
        f"Time(FP={res_fp_130.runtime_sec:.3f}s, ECLAT={res_ecl_130.runtime_sec:.3f}s, Apriori={res_apr_130.runtime_sec:.3f}s)"
    )

    # Optimal configuration: min_support=0.008, min_confidence=0.25, min_lift=1.50, max_len=3
    res_opt = mine_with_metrics(
        bundle.df_train,
        algorithm="FP-Growth (mlxtend)",
        min_support=0.008,
        min_confidence=0.25,
        min_lift=1.50,
        max_len=3,
    )
    eval_df = evaluate_rules_on_test(res_opt.rules, bundle.df_test)
    print(
        f"[Optimal Lift>=1.50, max_len=3] Rules={len(res_opt.rules)}, "
        f"Train ConfTB={res_opt.rules['confidence'].mean()*100:.2f}%, "
        f"Train LiftTB={res_opt.rules['lift'].mean():.2f}, "
        f"Test ConfTB={eval_df['test_confidence'].mean()*100:.2f}%, "
        f"Test LiftTB={eval_df['test_lift'].mean():.2f}"
    )

    freq_train = compute_item_frequencies(bundle.train_baskets)
    rec_df, base_df = recommend_for_basket(["root vegetables", "tropical fruit"], res_opt.rules, freq_train, top_k=5)
    assert not rec_df.empty, "Expected recommendations for ['root vegetables', 'tropical fruit']"
    assert not base_df.empty, "Expected baseline recommendations"
    print("Top recommendation:", rec_df.iloc[0].to_dict())

    # Test Apriori candidate trace and shelf zone clustering
    _, trace_df = apriori_custom_with_trace(bundle.df_train, min_support=0.008, max_len=3)
    assert not trace_df.empty and list(trace_df["k"]) == [1, 2, 3]
    print("Apriori trace:\n", trace_df.to_string(index=False))

    zones = compute_shelf_zones(res_opt.rules, max_zones=4)
    assert len(zones) > 0, "Expected shelf zones"
    print("Shelf zones:", len(zones), "Zone 1 anchor:", zones[0]["anchor_item"])

    # Test Online Retail tabular CSV auto-detection
    sample_online_retail = [
        "InvoiceNo,Description,Quantity",
        "536365,WHITE HANGING HEART T-LIGHT HOLDER,6",
        "536365,WHITE METAL LANTERN,6",
        "C536379,Discount,1",
        "536366,HAND WARMER UNION JACK,6",
    ]
    parsed_or = parse_csv_lines(sample_online_retail)
    assert len(parsed_or) == 2 and len(parsed_or[0]) == 2

    print("ALL VERIFICATIONS PASSED!")


if __name__ == "__main__":
    main()
