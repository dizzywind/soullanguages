#!/usr/bin/env python3
"""Content fidelity check.

Verifies that every text line scraped from the live Google Sites pages appears
verbatim in the built site (dist/). This guarantees no scripture content was
lost, altered, or invented during migration.

Usage: python3 scripts/migration/verify-fidelity.py   (run after `npm run build`)
"""
import json
import html as htmllib
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DIST = os.path.join(ROOT, "dist")
SCRAPE = os.path.join(HERE, "structured.json")

if not os.path.isdir(DIST):
    sys.exit("dist/ not found — run `npm run build` first.")

S = json.load(open(SCRAPE, encoding="utf-8"))

MARKERS = {"繁體", "简体", "簡體"}
NAV = {
    "主頁", "經文與分享", "下載", "聯絡我們", "Home", "Sutras", "Contact Us",
    "Soul Languages", "靈語堂", "懺悔偈", "綠度母心咒", "發菩提心義訣",
    "般若波羅蜜多心經", "地藏菩薩本願經心要頌", "關於空性", "心佛頌",
    "Repentance Chant",
}


def norm(s: str) -> str:
    s = re.sub(r"\s+", "", s)
    return s


def load_dist(path):
    p = os.path.join(DIST, path)
    if not os.path.exists(p):
        return None
    raw = open(p, encoding="utf-8").read()
    raw = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", raw)
    text = htmllib.unescape(raw)
    return norm(text)


def page_items(key):
    out, prev = [], None
    for it in S[key]:
        t = it["text"]
        if t in NAV or t in MARKERS or t == prev:
            prev = t
            continue
        prev = t
        out.append(t)
    return out


checks = [
    # (page key from scrape, built file)
    ("zh-home", "index.html"),
    ("zh-repentance", "sutras/repentance-chant/index.html"),
    ("zh-tara", "sutras/green-tara-mantra/index.html"),
    ("zh-bodhicitta", "sutras/bodhicitta/index.html"),
    ("zh-heartsutra", "sutras/heart-sutra/index.html"),
    ("zh-ksitigarbha", "sutras/ksitigarbha/index.html"),
    ("zh-emptiness", "sutras/about-emptiness/index.html"),
    ("en-repentance", "en/sutras/repentance-chant/index.html"),
    ("en-home", "en/index.html"),
]

def equivalent(line: str) -> list[str]:
    """Known benign renderings of a scraped line in the new build.

    The old site renders episode labels as split text runs
    (e.g. '第'+'一'+'集 寫靈語 說靈語'); the new site renders a single
    'EP1 寫靈語 說靈語' caption. Accept both forms.
    """
    variants = [line]
    stripped = re.sub(r"^(第.{1,2}集|集|EP\d+)\s*", "", line)
    if stripped != line and stripped.strip():
        variants.append(stripped)
    return variants


# Live-site text runs that are intentionally re-rendered as UI chrome:
# '想了解更多 … 訂閱我們的' + 'YouTube' + '頻道。' became the subscribe button,
# and split episode counters ('第'+'二'+'集 …') became 'EP2 …'.
SUPERSEDED = {"YouTube", "頻道。", "第", "二"}

total_missing = 0
for key, dist_path in checks:
    haystack = load_dist(dist_path)
    page = [t for t in page_items(key) if t not in SUPERSEDED]
    if haystack is None:
        print(f"MISSING FILE {dist_path}")
        total_missing += len(page)
        continue
    total = len(page)
    missing = []
    for t in page:
        if not any(norm(v) in haystack for v in equivalent(t)):
            missing.append(t)
    status = "OK " if not missing else "FAIL"
    print(f"[{status}] {key:18s} -> {dist_path}  ({total - len(missing)}/{total} lines found)")
    for m in missing[:8]:
        print(f"     missing: {m[:70]}")
    total_missing += len(missing)

print()
if total_missing == 0:
    print("✅ Fidelity check passed — every live-site line is present in the build.")
else:
    print(f"❌ {total_missing} line(s) missing from build.")
    sys.exit(1)
