#!/usr/bin/env python3
# Export only Buy It Now (FixedPriceItem) listings → listings.csv
# Fields: ItemID, Title, StartPrice, AvailableQty

import csv, json, sys, requests, xml.etree.ElementTree as ET

TOKEN_FILE = "tokens.json"
OUTPUT_FILE = "listings.csv"
SITE_ID = "0"          # US
COMPAT_LEVEL = "1147"

def load_access_token():
    with open(TOKEN_FILE) as f:
        return json.load(f)["access_token"]

def call_get_my_ebay_selling(token, page):
    url = "https://api.ebay.com/ws/api.dll"
    headers = {
        "X-EBAY-API-SITEID": SITE_ID,
        "X-EBAY-API-COMPATIBILITY-LEVEL": COMPAT_LEVEL,
        "X-EBAY-API-CALL-NAME": "GetMyeBaySelling",
        "X-EBAY-API-IAF-TOKEN": token,
        "Content-Type": "text/xml",
    }
    body = f"""<?xml version="1.0" encoding="utf-8"?>
<GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <DetailLevel>ReturnAll</DetailLevel>
  <ActiveList>
    <Sort>TimeLeft</Sort>
    <Pagination>
      <EntriesPerPage>200</EntriesPerPage>
      <PageNumber>{page}</PageNumber>
    </Pagination>
    <Include>true</Include>
  </ActiveList>
</GetMyeBaySellingRequest>"""
    r = requests.post(url, headers=headers, data=body.encode("utf-8"), timeout=60)
    r.raise_for_status()
    return r.text

def text(node, path, ns):
    el = node.find(path, ns)
    return el.text.strip() if el is not None and el.text else ""

def to_int(x):
    try: return int(float(x))
    except: return 0

def parse_page(xml_text):
    ns = {"e": "urn:ebay:apis:eBLBaseComponents"}
    root = ET.fromstring(xml_text)
    total_pages = int(text(root, ".//e:ActiveList/e:PaginationResult/e:TotalNumberOfPages", ns) or "1")
    rows = []

    for it in root.findall(".//e:ActiveList/e:ItemArray/e:Item", ns):
        ltype = text(it, "e:ListingType", ns)
        if ltype != "FixedPriceItem":
            continue  # skip auctions

        item_id = text(it, "e:ItemID", ns)
        title   = text(it, "e:Title", ns)
        start_price = text(it, "e:SellingStatus/e:CurrentPrice", ns) or text(it, "e:StartPrice", ns)

        qty_total = to_int(text(it, "e:Quantity", ns))
        qty_sold  = to_int(text(it, "e:SellingStatus/e:QuantitySold", ns))
        available = max(qty_total - qty_sold, 0)

        rows.append({
            "ItemID": item_id,
            "Title": title,
            "StartPrice": start_price,
            "AvailableQty": available,
        })

    return total_pages, rows

def main():
    token = load_access_token()
    all_rows, page = [], 1
    while True:
        xml_text = call_get_my_ebay_selling(token, page)
        total_pages, rows = parse_page(xml_text)
        all_rows.extend(rows)
        if page >= total_pages: break
        page += 1

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ItemID","Title","StartPrice","AvailableQty"])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Exported {len(all_rows)} fixed-price listings → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
