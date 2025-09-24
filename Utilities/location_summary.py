#!/usr/bin/env python3
# location_summary_fixed.py

import csv, sys
from collections import Counter

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 location_summary_fixed.py ebay2024orderreport.csv")
        sys.exit(1)

    path = sys.argv[1]

    with open(path, newline="", encoding="utf-8") as f:
        sample = f.read(4096)
        f.seek(0)
        delimiter = "\t" if sample.count("\t") > sample.count(",") else ","
        reader = csv.reader(f, delimiter=delimiter)
        rows = list(reader)

    headers = rows[1]
    data = rows[3:]

    # Find indices
    try:
        state_idx = headers.index("Ship To State")
        country_idx = headers.index("Ship To Country")
    except ValueError:
        print("Could not find location columns in headers:", headers)
        return

    locations = []
    for row in data:
        if state_idx < len(row) and country_idx < len(row):
            state = row[state_idx].strip()
            country = row[country_idx].strip()
            if country and country != "--":
                loc = f"{state}, {country}" if state else country
                locations.append(loc)

    counts = Counter(locations)

    print("\n=== Top Buyer Locations ===")
    if not counts:
        print("No location data found.")
    else:
        for loc, count in counts.most_common(20):
            print(f"{loc}: {count} orders")

if __name__ == "__main__":
    main()
