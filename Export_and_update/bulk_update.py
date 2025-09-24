#!/usr/bin/env python3
# Bulk update prices on eBay FixedPriceItem listings from listings.csv

import csv, json, sys, requests, xml.etree.ElementTree as ET

TOKEN_FILE = "tokens.json"
SITE_ID = "0"          # US
COMPAT_LEVEL = "1147"

def load_access_token():
    try:
        with open(TOKEN_FILE) as f:
            return json.load(f)["access_token"]
    except:
        print("Missing tokens.json. Run auth_flow.py first.")
        sys.exit(1)

def revise_price(token, item_id, new_price):
    url = "https://api.ebay.com/ws/api.dll"
    headers = {
        "X-EBAY-API-SITEID": SITE_ID,
        "X-EBAY-API-COMPATIBILITY-LEVEL": COMPAT_LEVEL,
        "X-EBAY-API-CALL-NAME": "ReviseFixedPriceItem",
        "X-EBAY-API-IAF-TOKEN": token,
        "Content-Type": "text/xml",
    }
    body = f"""<?xml version="1.0" encoding="utf-8"?>
<ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <Item>
    <ItemID>{item_id}</ItemID>
    <StartPrice>{new_price}</StartPrice>
  </Item>
</ReviseFixedPriceItemRequest>"""
    r = requests.post(url, headers=headers, data=body.encode("utf-8"), timeout=60)
    if r.status_code != 200:
        return False, f"HTTP {r.status_code}"
    root = ET.fromstring(r.text)
    ack = root.find(".//{urn:ebay:apis:eBLBaseComponents}Ack")
    if ack is not None and ack.text in ("Success", "Warning"):
        return True, "ok"
    else:
        err = root.find(".//{urn:ebay:apis:eBLBaseComponents}LongMessage")
        return False, err.text if err is not None else r.text[:200]

def main():
    token = load_access_token()
    with open("listings.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_id = row["ItemID"].strip()
            new_price = row["StartPrice"].strip()
            if not new_price:
                print(f"skip {item_id} (no price)")
                continue
            ok, msg = revise_price(token, item_id, new_price)
            if ok:
                print(f"✓ updated {item_id} → ${new_price}")
            else:
                print(f"✗ fail {item_id}: {msg}")

if __name__ == "__main__":
    main()
