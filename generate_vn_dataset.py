"""Generate a realistic Vietnamese supermarket transaction dataset (CSV) for MBA demo."""

from __future__ import annotations

import random
from pathlib import Path

from src.algorithms import compute_shelf_zones, mine_with_metrics
from src.data_pipeline import compute_item_frequencies, load_raw_baskets, prepare_dataset

OUT_PATH = Path(__file__).resolve().parent / "data" / "sieu_thi_viet_nam.csv"

# Core Vietnamese supermarket items with base single-item purchase weights
ALL_ITEMS = [
    "Sữa tươi Vinamilk",
    "Mì tôm Hảo Hảo",
    "Nước mắm Nam Ngư",
    "Dầu ăn Neptune",
    "Gạo ST25",
    "Trứng gà ta",
    "Thịt ba chỉ",
    "Rau muống",
    "Cà chua",
    "Hành lá",
    "Tỏi ta",
    "Đậu phụ",
    "Sữa chua Vinamilk",
    "Bánh mì sandwich",
    "Xúc xích Vissan",
    "Cà phê hòa tan G7",
    "Sữa đặc Ông Thọ",
    "Thịt bò Úc",
    "Nấm kim châm",
    "Rau cải thảo",
    "Gia vị lẩu Thái",
    "Bún tươi",
    "Bia Tiger",
    "Nước ngọt Coca-Cola",
    "Snack Oishi",
    "Lạc rang",
    "Chuối tiêu",
    "Cam sành",
    "Táo nhập khẩu",
    "Thanh long",
    "Nước suối Lavie",
    "Trà xanh Không Độ",
    "Hạt nêm Knorr",
    "Đường trắng Biên Hòa",
    "Muối i-ốt",
    "Nước tương Maggi",
    "Nước rửa chén Sunlight",
    "Nước giặt Omo",
    "Nước xả Comfort",
    "Giấy vệ sinh Pulppy",
    "Kem đánh răng P/S",
    "Bàn chải đánh răng",
    "Dầu gội Clear",
    "Túi đựng thực phẩm",
]

# Realistic co-occurrence shopping patterns (anchor -> companion candidates with probabilities)
PATTERNS: list[tuple[list[str], list[tuple[str, float]], float]] = [
    # (core items, [(companion, prob)], weight)
    (["Thịt ba chỉ", "Rau muống"], [("Tỏi ta", 0.72), ("Nước mắm Nam Ngư", 0.55), ("Gạo ST25", 0.40)], 14),
    (["Cà chua", "Trứng gà ta"], [("Hành lá", 0.75), ("Đậu phụ", 0.52), ("Dầu ăn Neptune", 0.45)], 13),
    (["Gạo ST25", "Nước mắm Nam Ngư"], [("Dầu ăn Neptune", 0.62), ("Hạt nêm Knorr", 0.50), ("Trứng gà ta", 0.35)], 12),
    (["Bánh mì sandwich", "Xúc xích Vissan"], [("Trứng gà ta", 0.58), ("Sữa tươi Vinamilk", 0.48), ("Nước tương Maggi", 0.35)], 12),
    (["Cà phê hòa tan G7"], [("Sữa đặc Ông Thọ", 0.68), ("Đường trắng Biên Hòa", 0.32), ("Bánh mì sandwich", 0.25)], 10),
    (["Mì tôm Hảo Hảo"], [("Xúc xích Vissan", 0.60), ("Trứng gà ta", 0.52), ("Rau cải thảo", 0.28)], 14),
    (["Sữa tươi Vinamilk"], [("Sữa chua Vinamilk", 0.60), ("Bánh mì sandwich", 0.38), ("Chuối tiêu", 0.32)], 13),
    (["Gia vị lẩu Thái", "Thịt bò Úc"], [("Nấm kim châm", 0.80), ("Rau cải thảo", 0.75), ("Bún tươi", 0.65)], 9),
    (["Bia Tiger"], [("Snack Oishi", 0.68), ("Lạc rang", 0.58), ("Nước ngọt Coca-Cola", 0.30)], 10),
    (["Nước ngọt Coca-Cola"], [("Snack Oishi", 0.62), ("Mì tôm Hảo Hảo", 0.30)], 10),
    (["Nước giặt Omo"], [("Nước xả Comfort", 0.78), ("Giấy vệ sinh Pulppy", 0.40), ("Nước rửa chén Sunlight", 0.32)], 9),
    (["Kem đánh răng P/S"], [("Bàn chải đánh răng", 0.68), ("Dầu gội Clear", 0.42), ("Giấy vệ sinh Pulppy", 0.35)], 8),
    (["Cam sành", "Chuối tiêu"], [("Táo nhập khẩu", 0.55), ("Sữa chua Vinamilk", 0.45), ("Thanh long", 0.40)], 9),
    (["Đậu phụ", "Hành lá"], [("Cà chua", 0.65), ("Nước mắm Nam Ngư", 0.42), ("Rau muống", 0.35)], 10),
    (["Nước suối Lavie"], [("Trà xanh Không Độ", 0.45), ("Snack Oishi", 0.38), ("Bánh mì sandwich", 0.28)], 9),
]


def generate_transactions(n_baskets: int = 3000, seed: int = 42) -> list[list[str]]:
    rng = random.Random(seed)
    pattern_weights = [p[2] for p in PATTERNS]
    baskets: list[list[str]] = []

    for _ in range(n_baskets):
        r = rng.random()
        if r < 0.16:
            # Realistic ~16% quick single-item convenience purchases
            item = rng.choice(ALL_ITEMS[:25])
            baskets.append([item])
            continue

        chosen_core, companions, _ = rng.choices(PATTERNS, weights=pattern_weights, k=1)[0]
        basket = list(chosen_core)
        for comp, prob in companions:
            if rng.random() < prob:
                basket.append(comp)

        # Occasional cross-category random impulse items (1-3 items) to reflect real mixed carts
        if rng.random() < 0.70:
            n_extra = rng.choice([1, 2, 2, 3])
            for extra in rng.sample(ALL_ITEMS, k=n_extra):
                if extra not in basket:
                    basket.append(extra)

        # Rare duplicate item inside basket (simulating scanned twice before cleaning)
        if rng.random() < 0.02 and basket:
            basket.append(basket[0])

        rng.shuffle(basket)
        baskets.append(basket)

    return baskets


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    baskets = generate_transactions(n_baskets=3000, seed=42)
    with OUT_PATH.open("w", encoding="utf-8") as fh:
        for b in baskets:
            fh.write(",".join(b) + "\n")

    # Verify via our actual MBA pipeline
    raw = load_raw_baskets(OUT_PATH)
    bundle = prepare_dataset(raw, min_basket_size=2, test_size=0.20, random_state=42)
    res = mine_with_metrics(bundle.df_train, "FP-Growth (mlxtend)", min_support=0.008, min_confidence=0.25, min_lift=1.50, max_len=3)
    freq = compute_item_frequencies(bundle.clean_baskets)
    zones = compute_shelf_zones(res.rules, max_zones=4)

    print(f"Saved: {OUT_PATH} ({OUT_PATH.stat().st_size:,} bytes)")
    print("Stats:", bundle.stats)
    print("Top 5 items:\n", freq.head(5).to_string(index=False))
    print(f"Rules mined (min_sup=0.008, conf>=0.25, lift>=1.50, max_len=3): {len(res.rules)}, Avg Lift: {res.rules['lift'].mean():.2f}")
    print("Top 5 rules:")
    for idx, row in res.rules.head(5).iterrows():
        print(f"  {idx+1}. {', '.join(sorted(row['antecedents']))} => {', '.join(sorted(row['consequents']))} (Conf={row['confidence']*100:.1f}%, Lift={row['lift']:.2f})")
    print("Shelf zones:", len(zones))


if __name__ == "__main__":
    main()
