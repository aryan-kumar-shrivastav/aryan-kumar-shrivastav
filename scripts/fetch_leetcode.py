#!/usr/bin/env python3
"""Fetch LeetCode stats -> docs/data/leetcode.json (keeps last good data on failure)."""
import json, pathlib, sys
from datetime import datetime, timezone
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config.json").read_text())
OUT = ROOT / "docs" / "data" / "leetcode.json"
URL = "https://leetcode.com/graphql"

QUERY = """
query userStats($username: String!) {
  matchedUser(username: $username) {
    username
    profile { ranking reputation }
    submitStatsGlobal { acSubmissionNum { difficulty count } }
  }
  userContestRanking(username: $username) { rating globalRanking attendedContestsCount }
}
"""


def fetch(username):
    resp = requests.post(
        URL,
        json={"query": QUERY, "variables": {"username": username}},
        headers={
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/u/{username}/",
            "User-Agent": "Mozilla/5.0 (portfolio-stats-bot)",
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json().get("data") or {}
    user = data.get("matchedUser")
    if not user:
        raise ValueError(f"LeetCode user '{username}' not found")
    solved = {r["difficulty"].lower(): r["count"] for r in user["submitStatsGlobal"]["acSubmissionNum"]}
    contest = data.get("userContestRanking") or {}
    return {
        "username": user["username"],
        "total": solved.get("all", 0),
        "easy": solved.get("easy", 0),
        "medium": solved.get("medium", 0),
        "hard": solved.get("hard", 0),
        "ranking": user["profile"]["ranking"],
        "contest_rating": round(contest["rating"]) if contest.get("rating") else None,
        "contests_attended": contest.get("attendedContestsCount", 0),
    }


def main():
    try:
        stats = fetch(CONFIG["leetcode_username"])
    except Exception as exc:
        print(f"::warning::LeetCode fetch failed: {exc}")
        return 0
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    if {k: v for k, v in old.items() if k != "updated_at"} == stats:
        print("LeetCode: no changes")
        return 0
    stats["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    OUT.write_text(json.dumps(stats, indent=2) + "\n")
    print(f"LeetCode: updated ({stats['total']} solved)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
