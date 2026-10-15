#!/usr/bin/env python3
"""Recompute the DSA summary + daily history in docs/data/dsa_tracker.json.

Manual edits:  python scripts/update_dsa_tracker.py --set "Arrays=12" --total "Arrays=40"
"""
import argparse, json, pathlib, sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "data"
TRACKER = DATA / "dsa_tracker.json"


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def apply_edits(topics, pairs, field):
    for pair in pairs or []:
        name, _, val = pair.rpartition("=")
        match = [t for t in topics if t["name"].lower() == name.strip().lower()]
        if not match:
            sys.exit(f"Unknown topic: {name!r}")
        match[0][field] = int(val)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", action="append", metavar="TOPIC=N", help="set solved count")
    ap.add_argument("--total", action="append", metavar="TOPIC=N", help="set total problems")
    args = ap.parse_args()

    before = TRACKER.read_text()
    tracker = json.loads(before)
    topics = tracker.setdefault("topics", [])
    apply_edits(topics, args.set, "solved")
    apply_edits(topics, args.total, "total")

    solved = sum(t.get("solved") or 0 for t in topics)
    total = sum(t.get("total") or 0 for t in topics)
    tracker["summary"] = {
        "striver_solved": solved,
        "striver_total": total or None,
        "percent": round(100 * solved / total, 1) if total else None,
    }

    lc = load(DATA / "leetcode.json", {})
    entry = {"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
             "leetcode": lc.get("total"), "striver": solved}
    hist = tracker.setdefault("history", [])
    if hist and hist[-1]["date"] == entry["date"]:
        hist[-1] = entry
    elif not hist or {k: v for k, v in hist[-1].items() if k != "date"} != \
            {k: v for k, v in entry.items() if k != "date"}:
        hist.append(entry)          # only add a point when something changed
    tracker["history"] = hist[-365:]

    after = json.dumps(tracker, indent=2) + "\n"
    if after != before:
        TRACKER.write_text(after)
        print(f"DSA tracker updated: {solved} Striver problems tracked")
    else:
        print("DSA tracker: no changes")


if __name__ == "__main__":
    main()
