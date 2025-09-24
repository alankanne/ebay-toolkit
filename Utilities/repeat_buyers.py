#!/usr/bin/env python3
# repeat_buyers_fixed.py

import csv, sys
from collections import Counter

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 repeat_buyers_fixed.py ebay2024orderreport.csv")
        sys.exit(1)

    path = sys.argv[1]
    buyers = []

    with open(path, newline="", encoding="utf-8") as f:
        # Try both comma and tab delimiters
        sample = f.read(4096)
        f.seek(0)
        delimiter = "\t" if sample.count("\t") > sample.count(",") else ","
        reader = csv.reader(f, delimiter=delimiter)

        rows = list(reader)

    # Row 0: junk, Row 1: headers, Row 2: blank, Row 3+: data
    headers = rows[1]
    data = rows[3:]

    # Find column index for "Buyer Username"
    try:
        buyer_idx = headers.index("Buyer Username")
    except ValueError:
        print("Could not find 'Buyer Username' in headers:", headers)
        return

    for row in data:
        if buyer_idx < len(row):
            buyer = row[buyer_idx].strip()
            if buyer and buyer != "--":
                buyers.append(buyer)

    counts = Counter(buyers)
    repeaters = {b: c for b, c in counts.items() if c > 1}

    print("\n=== Repeat Buyers ===")
    if not repeaters:
        print("No repeat buyers found.")
    else:
        for buyer, count in sorted(repeaters.items(), key=lambda x: -x[1]):
            print(f"{buyer}: {count} purchases")

if __name__ == "__main__":
    main()
