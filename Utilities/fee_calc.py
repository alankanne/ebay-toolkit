#!/usr/bin/env python3
"""
Quick eBay fee calculator.
Covers categories I actually dealt with, not every weird edge case.

Notes:
- Fees apply to (item price + shipping).
- Store subscribers get lower rates.
- International buyers add +1.65% fee.
- This is a simplified version of the official table:
  https://www.ebay.com/help/selling/fees-credits-invoices/selling-fees?id=4822
"""

INTERNATIONAL_SURCHARGE = 0.0165

# fee rules (final value fee %), pulled from eBay fee tables
# key = category, value = dict with either tiered "tiers" or flat "threshold_whole"
RULES = {
    # fallback (most categories)
    "most": {
        "store": [(2500, 0.127), (None, 0.0235)],
        "non_store": [(7500, 0.136), (None, 0.0235)]
    },

    # clothing
    "clothing": {
        "store": [(2500, 0.127), (None, 0.0235)],
        "non_store": [(7500, 0.136), (None, 0.0235)]
    },
    "womens_bags": {
        "store": [(2000, 0.13), (None, 0.07)],
        "non_store": [(2000, 0.15), (None, 0.09)]
    },
    "athletic_shoes": {
        # whole-amount threshold: if >= $150, use lower rate
        "store_threshold": [(150, 0.07), (0, 0.127)],
        "non_store_threshold": [(150, 0.08), (0, 0.136)]
    },

    # media
    "books_movies_music": {
        "store": [(2500, 0.153), (None, 0.0235)],
        "non_store": [(7500, 0.153), (None, 0.0235)]
    },

    # electronics
    "electronics": {
        "store": [(2500, 0.0935), (None, 0.0235)],
        "non_store": [(7500, 0.1255), (None, 0.0235)]
    },

    # video games
    "video_games": {
        "store": [(2500, 0.0935), (None, 0.0235)],
        "non_store": [(7500, 0.1325), (None, 0.0235)]
    },
    "video_game_consoles": {
        "store": [(2500, 0.0735), (None, 0.0235)],
        "non_store": [(7500, 0.1325), (None, 0.0235)]
    },

    # collectibles
    "collectibles": {
        "store": [(2500, 0.127), (None, 0.0235)],
        "non_store": [(7500, 0.1325), (None, 0.0235)]
    },
    "trading_cards": {
        "store": [(2500, 0.1235), (None, 0.0235)],
        "non_store": [(7500, 0.1325), (None, 0.0235)]
    },

    # jewelry / watches
    "jewelry": {
        "store": [(5000, 0.13), (None, 0.07)],
        "non_store": [(5000, 0.15), (None, 0.09)]
    },
    "watches": {
        "store": [(1000, 0.125), (5000, 0.04), (None, 0.03)],
        "non_store": [(1000, 0.15), (7500, 0.065), (None, 0.03)]
    }
}


def _apply_tiers(amount, tiers):
    fee = 0
    last_cap = 0
    remaining = amount
    for cap, rate in tiers:
        if cap is None:  # final tier
            slab = remaining
        else:
            slab = min(remaining, cap - last_cap)
        if slab > 0:
            fee += slab * rate
            remaining -= slab
        if cap:
            last_cap = cap
        if remaining <= 0:
            break
    return fee


def _apply_threshold(amount, rules):
    # pick one rate for the entire amount, depending on threshold
    for threshold, rate in sorted(rules, key=lambda x: -x[0]):
        if amount >= threshold:
            return amount * rate
    return amount * rules[-1][1]


def calculate_fee(store, category, price, shipping=0, international=False):
    gross = price + shipping
    if category not in RULES:
        category = "most"  # fallback

    rule = RULES[category]

    if "threshold_whole" in rule or "store_threshold" in rule:
        key = "store_threshold" if store else "non_store_threshold"
        final_value_fee = _apply_threshold(gross, rule[key])
    else:
        key = "store" if store else "non_store"
        final_value_fee = _apply_tiers(gross, rule[key])

    intl_fee = gross * INTERNATIONAL_SURCHARGE if international else 0
    total = final_value_fee + intl_fee
    net = gross - total

    return {
        "category": category,
        "store": store,
        "gross": round(gross, 2),
        "fees": round(total, 2),
        "net": round(net, 2),
        "effective_rate": f"{round(total / gross * 100, 2)}%"
    }


if __name__ == "__main__":
    # a couple test cases
    print(calculate_fee(store=True, category="electronics",
                        price=200, shipping=10, international=False))
    print(calculate_fee(store=False, category="athletic_shoes",
                        price=180, shipping=0, international=True))
    print(calculate_fee(store=True, category="watches",
                        price=6000, shipping=20, international=False))
