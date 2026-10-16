#!/usr/bin/env python3
"""Fetch HackTheBox stats -> docs/data/htb.json.

Needs an App Token (HTB profile settings -> App Tokens) stored as the
GitHub secret HTB_TOKEN. Without it the script does nothing and your
manually edited htb.json stays as-is. HTB's API is not formally stable:
if the response shape changes, the script keeps your existing values.
"""
import json, os, pathlib, sys
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config.json").read_text())
OUT = ROOT / "docs" / "data" / "htb.json"


def fetch(user_id, token):
    r = requests.get(
        f"https://labs.hackthebox.com/api/v4/user/profile/basic/{user_id}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json",
                 "User-Agent": "portfolio-stats-bot"},
        timeout=20,
    )
    r.raise_for_status()
    p = r.json().get("profile") or {}
    if not p:
        raise ValueError("unexpected response shape")
    return {
        "username": p.get("name"),
        "rank": p.get("rank"),
        "points": p.get("points"),
        "user_owns": p.get("user_owns"),
        "system_owns": p.get("system_owns"),
        "profile_url": f"https://app.hackthebox.com/users/{user_id}",
    }


def main():
    token = os.environ.get("HTB_TOKEN")
    if not token:
        print("HTB: no HTB_TOKEN set, skipping (using manual htb.json)")
        return 0
    try:
        new = fetch(CONFIG["htb_user_id"], token)
    except Exception as exc:
        print(f"::warning::HTB fetch failed: {exc}")
        return 0
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    merged = {**old, **{k: v for k, v in new.items() if v is not None}}
    if merged == old:
        print("HTB: no changes")
        return 0
    OUT.write_text(json.dumps(merged, indent=2) + "\n")
    print("HTB: updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
