#!/usr/bin/env python3
"""Regenerate the block between <!--STATS:START--> and <!--STATS:END--> in README.md."""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "data"
cfg = json.loads((ROOT / "config.json").read_text())
load = lambda n: json.loads((DATA / n).read_text()) if (DATA / n).exists() else {}
lc, htb, dsa = load("leetcode.json"), load("htb.json"), load("dsa_tracker.json")


def bar(done, total, width=20):
    n = round(width * done / total) if total else 0
    return "█" * n + "░" * (width - n)


def fmt(v):
    return f"{v:,}" if isinstance(v, int) else (v if v not in (None, "") else "—")


def build():
    out = ["### 🧩 DSA", "",
           "| LeetCode | Solved |", "|---|---|",
           f"| Total | **{fmt(lc.get('total'))}** |",
           f"| Easy / Medium / Hard | {fmt(lc.get('easy'))} / {fmt(lc.get('medium'))} / {fmt(lc.get('hard'))} |",
           f"| Contest rating | {fmt(lc.get('contest_rating'))} |",
           f"| Global rank | {fmt(lc.get('ranking'))} |", ""]
    topics = [t for t in dsa.get("topics", []) if t.get("solved")]
    if topics:
        s = dsa.get("summary", {})
        pct = f" ({s['percent']}%)" if s.get("percent") is not None else ""
        out += [f"**Striver's A-to-Z:** {s.get('striver_solved', 0)} problems tracked{pct}", "",
                "| Topic | Solved | Progress |", "|---|---|---|"]
        for t in topics:
            tot = t.get("total")
            prog = f"`{bar(t['solved'], tot)}` {t['solved']}/{tot}" if tot else "—"
            out.append(f"| {t['name']} | {t['solved']} | {prog} |")
        out.append("")
    user = cfg["tryhackme_username"]
    out += ["### 🔐 Cybersecurity", "",
            f'<a href="https://tryhackme.com/p/{user}"><img src="https://tryhackme-badges.s3.amazonaws.com/{user}.png" alt="TryHackMe" height="150"></a>',
            "", "| HackTheBox | |", "|---|---|",
            f"| Rank | {fmt(htb.get('rank'))} |", f"| Points | {fmt(htb.get('points'))} |",
            f"| User / System owns | {fmt(htb.get('user_owns'))} / {fmt(htb.get('system_owns'))} |",
            f"| Profile | [{htb.get('username', 'HTB')}]({htb.get('profile_url', '#')}) |", ""]
    gh = cfg["github_username"]
    out.append(f"🌐 **[Full portfolio](https://{gh}.github.io/{gh}/)**"
               + (f" · _synced {lc['updated_at'][:10]}_" if lc.get("updated_at") else ""))
    return "\n".join(out)


readme = ROOT / "README.md"
text = readme.read_text()
new = re.sub(r"(<!--STATS:START-->).*?(<!--STATS:END-->)",
             lambda m: f"{m.group(1)}\n{build()}\n{m.group(2)}", text, flags=re.S)
if new != text:
    readme.write_text(new)
    print("README updated")
else:
    print("README: no changes")
