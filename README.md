# eBay Automation Scripts

A small toolkit of Python scripts I built to automate my resale business on eBay.  
Instead of clicking through Seller Hub and dealing with the annoying UI, these scripts let me manage listings, run bulk updates, and pull useful analytics from the command line.

## Why I Built This

I run an online resale business (>$200k sales in 2024), and eBay’s interface wasn’t built for scale.  
These scripts started as quick utilities, but grew into a set of tools that saved me a ton of time by automating repetitive work and giving me better visibility into sales data.

## Features

- **auth_flow.py** → Handles eBay OAuth2 login + token refresh, stores `tokens.json`
- **export_listings.py** → Exports active listings (ItemID, Title, Price, Quantity)
- **bulk_update.py** → Bulk edit prices via the Trading API’s `ReviseFixedPriceItem`
- **fee_calc.py** → Estimates eBay fees (store vs. non-store, category-based rules)
- **repeat_buyers.py** → Parses order data CSVs that can be pulled from eBay, counts repeat customers
- **location_summary.py** → Aggregates orders by state and country

## Example Outputs

Repeat buyers:
```
computermonkey: 11 purchases
```

Location summary:
```
FL, United States: 58 orders
CA, United States: 26 orders
IL, United States: 18 orders
```

Fee calculator:
```
Item price: $129.99
Estimated fees: $15.47
```

## Structure

- **export_and_update/** → Scripts for pulling listings and pushing updates back to eBay  
- **utilities/** → Analysis scripts (buyers, fees, locations)

## Getting Started

Clone the repo:
```bash
git clone https://github.com/yourusername/ebay-automation-tools.git
cd ebay-automation-tools
pip install -r requirements.txt
```

Run a script:
```bash
python utilities/repeat_buyers.py ebay2024orders.csv
```

## Requirements

- Python 3.x  
- `requests` for API calls  
- Standard library modules (`csv`, `json`, etc.)  

> Note: export/update scripts require an [eBay Developer Account](https://developer.ebay.com/) + API credentials.  
> Keep `tokens.json` private — it contains access tokens.  


## License

MIT — free to use and modify.
