#!/usr/bin/env python3
# eBay OAuth flow with refresh support
# - If tokens.json exists → refresh using saved scopes
# - If not → run full authorization code flow and save tokens

import base64, json, os, requests, sys

CLIENT_ID = "YOUR CLIENT ID"
CLIENT_SECRET = "YOUR CLIENT SECRET"   # your Cert ID
RUNAME = "YOUR RU NAME"

# only used on FIRST auth
INITIAL_SCOPES = [
    "https://api.ebay.com/oauth/api_scope",
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
]

TOKEN_FILE = "tokens.json"


def refresh_tokens(refresh_token, scopes):
    print("Refreshing access token...")
    basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": " ".join(scopes),
    }
    r = requests.post(url, headers=headers, data=data)
    if r.status_code != 200:
        print("Refresh failed:", r.text)
        sys.exit(1)
    return r.json()


def save_tokens(base, new_tokens, scopes):
    merged = base.copy()
    merged["access_token"] = new_tokens["access_token"]
    if "refresh_token" in new_tokens:  # only present in full flow
        merged["refresh_token"] = new_tokens["refresh_token"]
    merged["scope"] = scopes
    with open(TOKEN_FILE, "w") as f:
        json.dump(merged, f, indent=2)
    print("Updated tokens.json")


def main():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            saved = json.load(f)
        if "refresh_token" in saved and "scope" in saved:
            tokens = refresh_tokens(saved["refresh_token"], saved["scope"])
            save_tokens(saved, tokens, saved["scope"])
            return
        else:
            print("tokens.json exists but missing refresh_token/scope. Delete it and re-run.")
            sys.exit(1)

    # full authorization code flow
    scope_str = "%20".join(INITIAL_SCOPES)
    consent_url = (
        "https://auth.ebay.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={RUNAME}"
        "&response_type=code"
        f"&scope={scope_str}"
    )
    print("\nGo here, log in with your SELLER account, approve:")
    print(consent_url)

    code = input("\nPaste ?code= from redirect URL: ").strip()

    basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": RUNAME,
    }
    r = requests.post(url, headers=headers, data=data)
    if r.status_code != 200:
        print("Auth failed:", r.text)
        sys.exit(1)

    tokens = r.json()
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": RUNAME,
        "refresh_token": tokens.get("refresh_token"),
        "access_token": tokens.get("access_token"),
        "scope": tokens.get("scope", INITIAL_SCOPES),
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(payload, f, indent=2)
    print("Saved tokens.json")


if __name__ == "__main__":
    main()
