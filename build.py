#!/usr/bin/env python3
"""soul-languages build — generate static HTML pages from data/content.json

Usage:
  python3 build.py              # Full build
  python3 build.py --watch      # Watch mode (rebuild on changes)
"""

import json, pathlib, sys, time, os, argparse

PROJECT = pathlib.Path(__file__).parent.resolve()
DIST    = PROJECT / "dist"
DATA    = PROJECT / "data" / "content.json"
JS_SRC  = PROJECT / "js"
CSS_SRC = PROJECT / "css"
JS_DST  = DIST / "js"
CSS_DST = DIST / "css"
PAGES_DST = DIST / "pages"

(DIST / "pages").mkdir(parents=True, exist_ok=True)
JS_DST.mkdir(parents=True, exist_ok=True)
CSS_DST.mkdir(parents=True, exist_ok=True)

# ── 0. Content validation ───────────────────────────────────────
errors = []
warnings = []

def validate_content(data):
    """Validate content.json structure and required fields."""
    # Check top-level keys
    for key in ["site", "nav", "episodes", "pages"]:
        if key not in data:
            errors.append(f"MISSING required top-level key: '{key}'")

    if "site" in data:
        site = data["site"]
        for field in ["name", "url"]:
            if field not in site or not site[field]:
                errors.append(f"MISSING: site.{field} is required")
        if "description" not in site or not site["description"]:
            warnings.append("WARNING: site.description is empty")
        if "lang" not in site:
            warnings.append("WARNING: site.lang not set, defaulting to zh-Hant")

    # Validate nav entries
    nav_ids = set()
    if "nav" in data:
        for i, item in enumerate(data["nav"]):
            if "id" not in item or not item["id"]:
                errors.append(f"nav[{i}] missing 'id' field")
            else:
                nav_ids.add(item["id"])
            if "zh" not in item or not item["zh"]:
                warnings.append(f"nav[{i}] ({item.get('id','?')}) missing 'zh' label")

    # Validate pages
    if "pages" in data:
        for pid, pdata in data["pages"].items():
            if pid not in nav_ids and pid != "home":
                warnings.append(f"WARNING: page '{pid}' has no corresponding nav entry")
            if "title" not in pdata or not pdata.get("title", "").strip():
                warnings.append(f"WARNING: page '{pid}' has empty title")
            desc = pdata.get("description", "")
            if not desc:
                warnings.append(f"WARNING: page '{pid}' has empty description")

    # Validate episodes
    if "episodes" in data:
        if not data["episodes"]:
            warnings.append("WARNING: episodes array is empty")
        for i, ep in enumerate(data["episodes"]):
            if "num" not in ep:
                warnings.append(f"episodes[{i}] missing 'num' field")
            if "yt" not in ep or not ep.get("yt"):
                errors.append(f"episodes[{i}] missing YouTube URL (yt)")
            if "thumb" not in ep or not ep.get("thumb"):
                warnings.append(f"episodes[{i}] missing thumbnail URL (thumb)")
            if "title" not in ep:
                warnings.append(f"episodes[{i}] missing 'title' object")
            else:
                t = ep["title"]
                if "en" not in t or not t.get("en"):
                    warnings.append(f"episodes[{i}] missing English title")
                if "zh" not in t or not t.get("zh"):
                    warnings.append(f"episodes[{i}] missing Chinese title")

    # Print results
    for w in warnings:
        print(f"  ⚠  {w}")
    for e in errors:
        print(f"  ✗  {e}")
    if errors:
        print(f"\n❌ {len(errors)} critical error(s) found. Aborting build.")
        sys.exit(1)
    if warnings:
        print(f"  ⚠  {len(warnings)} warning(s) — continuing build\n")
    else:
        print("  ✓ Content validation passed\n")


# ── JSON-LD structured data ─────────────────────────────────────
def json_ld(page_id, title, desc, site):
    """Generate JSON-LD structured data for a given page."""
    url = site.get("url", "https://soullanguages.com")
    lang = site.get("lang", "zh-Hant")
    author_name = site.get("author", site.get("name", "靈語堂"))

    if page_id == "home":
        # Organization + WebSite
        ld = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Organization",
                    "@id": f"{url}/#organization",
                    "name": site.get("name", "靈語堂"),
                    "url": url,
                    "logo": site.get("logo", ""),
                    "description": site.get("description", ""),
                    "sameAs": ["https://www.youtube.com/@soullanguages"]
                },
                {
                    "@type": "WebSite",
                    "@id": f"{url}/#website",
                    "url": url,
                    "name": site.get("name", "靈語堂"),
                    "description": site.get("description", ""),
                    "inLanguage": lang,
                    "publisher": {"@id": f"{url}/#organization"}
                }
            ]
        }
    elif page_id in ("scriptures", "repentance"):
        # Article schema for scripture/repentance pages
        ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "@id": f"{url}/pages/{page_id}.html",
            "headline": title,
            "description": desc or site.get("description", ""),
            "inLanguage": lang,
            "author": {"@type": "Person", "name": author_name},
            "publisher": {"@type": "Organization", "name": site.get("name", "靈語堂")},
            "mainEntityOfPage": f"{url}/pages/{page_id}.html",
            "dateModified": "2024-01-01"
        }
    else:
        # WebPage schema for all other pages
        ld = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "@id": f"{url}/pages/{page_id}.html",
            "name": title,
            "description": desc or site.get("description", ""),
            "inLanguage": lang,
            "publisher": {"@type": "Organization", "name": site.get("name", "靈語堂")},
            "url": f"{url}/pages/{page_id}.html"
        }

    return f'<script type="application/ld+json">\n{json.dumps(ld, ensure_ascii=False, indent=2)}\n</script>'


# ── Load data ───────────────────────────────────────────────────
try:
    raw = DATA.read_text(encoding="utf-8")
    data = json.loads(raw)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"❌ Failed to load {DATA}: {e}")
    sys.exit(1)

site = data["site"]
nav_items = [
    ("home",          "主頁"),    ("scriptures",    "經文與分享"),
    ("repentance",    "懺悔偈"),   ("tara",          "綠度母心咒"),
    ("bodhicitta",    "發菩提心義訣"), ("heart-sutra",   "般若波羅蜜多心經"),
    ("ksitigarbha",   "地藏菩薩本願經心要頌"), ("emptiness",     "關於空性"),
    ("mind-buddha",   "心佛頌"),   ("downloads",     "下載"),
    ("contact",       "聯絡我們"),
]

EP_PAGES = ["scriptures","heart-sutra","bodhicitta","ksitigarbha","tara","emptiness","mind-buddha","repentance"]
PAGE_BODIES = {}

# ── page contents ──────────────────────────────────────────
def hero_block(title, subtitle, desc_lines, cta_label, cta_anchor):
    lines = ''.join(f'<p>{l}</p>' for l in (desc_lines if isinstance(desc_lines, list) else [desc_lines]))
    return f"""<section class="hero" aria-labelledby="ht">
<h1 id="ht">{title}</h1><p>{subtitle}</p>{lines}
<a href="#{cta_anchor}" class="cta-btn">{cta_label} ↓</a></section>"""

def eps_block(episodes):
    cards = ""
    for ep in episodes:
        t = ep["title"]
        cards += (f'<article class="ep-card">'
                  f'<img class="ep-thumb" src="{ep["thumb"]}" alt="{t["en"]}"'
                  f' loading="lazy" data-video="{ep["yt"]}">'
                  f'<div class="ep-body"><span class="ep-num">EP{ep["num"]}</span>'
                  f'<p class="ep-title">{t["en"]}</p>'
                  f'<p class="ep-sub">{t["zh"]}</p></div></article>\n')
    return f'<section id="episodes" aria-labelledby="et"><h2 id="et" class="section-title">系列影片</h2><div class="episodes-grid" id="episodes-grid">{cards}</div></section>'

def zen(label, body):
    return f'<div class="zen-box"><p class="label">{label}</p><p>{body}</p></div>'

def build_page_body(page_id, pdata):
    if page_id == "home":
        return (
            hero_block(site["name"],
                "身體生病可以吃藥，心靈受傷也可以說靈語。",
                ["靈語是自然流露，不需要刻意學習。",
                 "想探索靈語的奧秘、靈修的力量、以及靈界的世界？"],
                "觀看系列影片", "episodes")
            + eps_block(data["episodes"])
            + '<section class="prose" aria-labelledby="intro"><h2 id="intro" class="section-title">關於靈語</h2>'
            + zen("靈語是什麼？","靈語是自然流露，不需要刻意學習。")
            + "<p>有人會說靈語，卻不明白自己在說什麼？<br>"
            + "想探索靈語的奧秘、靈修的力量、以及靈界的世界？<br>"
            + "<strong>是外靈在說話，還是你內在的本性</strong>？</p>"
            + "<p>想了解更多，追蹤我們，並訂閱我們的 <strong>YouTube 頻道</strong>。</p>"
            + "</section>"
        )

    body = pdata.get("body", [])
    parts = ""
    for tag, content in body:
        if tag:
            parts += f"<{tag}>{content or ''}</{tag}>\n"
        else:
            parts += f"{content or ''}\n"
    return parts

# ── navigation HTML ──────────────────────────────────────
TARGET = {
    "scriptures":  ("經文與分享","scriptures.html"),
    "repentance":  ("懺悔偈",  "repentance.html"),
    "tara":        ("綠度母心咒","tara.html"),
    "bodhicitta":  ("發菩提心義訣","bodhicitta.html"),
    "heart-sutra": ("般若波羅蜜多心經","heart-sutra.html"),
    "ksitigarbha": ("地藏菩薩本願經心要頌","ksitigarbha.html"),
    "emptiness":   ("關於空性", "emptiness.html"),
    "mind-buddha": ("心佛頌",  "mind-buddha.html"),
    "downloads":   ("下載",    "downloads.html"),
    "contact":     ("聯絡我們","contact.html"),
}

def nav_block(active):
    items = []
    for pid, zh in nav_items:
        cls = ' class="active-nav"' if pid == active else ''
        if pid == "home":
            items.append(f'<li><a href="index.html"{cls}>{zh}</a></li>')
        else:
            target = TARGET.get(pid, (pid, pid+".html"))
            items.append(f'<li><a href="{target[1]}"{cls}>{zh}</a></li>')
    inner = "\n".join(f"        {x}" for x in items)
    return (f'<header class="site-header" role="banner"><div class="header-inner">'
            f'<a href="index.html" class="logo">靈語<em>堂</em></a>'
            f'<button class="mobile-nav-toggle" aria-label="選單" aria-expanded="false">☰</button>'
            f'<nav aria-label="主要導航"><ul class="nav-items" role="list">\n{inner}\n'
            f'</ul></nav>'
            f'<button class="lang-toggle" aria-label="切換簡體中文">簡</button>'
            f'<button id="theme-toggle" class="theme-toggle" aria-label="切換深色模式"></button>'
            f'</div></header>')

def footer_(page_id="home"):
    lightbox = ('<div id="lightbox" hidden role="dialog" aria-modal="true" aria-label="影片播放">'
                '<button id="lightbox-close" aria-label="關閉影片">✕</button>'
                '<div id="lightbox-inner"></div></div>')
    js_path = "js/main.min.js" if page_id == "home" else "../js/main.min.js"
    return (lightbox
            + '<footer class="site-footer" role="contentinfo"><div class="footer-inner">'
            '<nav aria-label="頁尾導航"><a href="index.html">主頁</a>'
            '<a href="scriptures.html">經文與分享</a>'
            '<a href="contact.html">聯絡我們</a>'
            '<a href="https://www.youtube.com/@soullanguages">YouTube</a></nav>'
            '<p class="copyright">© 2024 靈語堂 Soul Languages. All rights reserved.</p>'
            f'</div></footer><script src="{js_path}" defer></script>')

def head_html(page_id, title, desc):
    og_img = site.get("og_image","og-cover.jpg")
    page_url = site["url"]
    if page_id == "home":
        canonical = page_url + "/"
    else:
        canonical = page_url + f"/pages/{page_id}.html"
    # Generate JSON-LD
    ld_html = json_ld(page_id, title, desc, site)
    return (f'<!DOCTYPE html><html lang="zh-Hant"><head>'
            '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><meta name="description" content="{desc}">'
            '<meta name="robots" content="index,follow">'
            f'<link rel="canonical" href="{canonical}">'
            f'<meta property="og:title" content="{title}">'
            f'<meta property="og:description" content="{desc}">'
            '<meta property="og:type" content="website">'
            f'<meta property="og:url" content="{canonical}">'
            f'<meta property="og:image" content="{og_img}"><meta property="og:locale" content="zh_TW">'
            '<meta name="twitter:card" content="summary_large_image">'
            f'<meta name="twitter:title" content="{title}">'
            f'<meta name="twitter:description" content="{desc}">'
'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
'<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+TC:wght@400;600;700&family=Noto+Serif+TC:wght@400;700&display=swap" rel="stylesheet">'
            '<link rel="icon" href="data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 32\'><text y=\'28\' font-size=\'24\'>\u171E</text></svg>">'
            '<link rel="stylesheet" href="../css/styles.css"><link rel="stylesheet" href="../css/layout.css">'
            f'{ld_html}'
            '</head><body>'
            '<a href="#main" class="skip-link">跳至主要內容</a>')

def make_html(page_id, title, desc, inner):
    return head_html(page_id, title, desc) + nav_block(page_id) + inner + footer_(page_id) + "</body></html>"


# ── Copy static assets ──────────────────────────────────────────
def minify_js(text):
    """Simple JS minification: strip comments and whitespace.

    Uses negative lookbehind to avoid matching ``//`` inside URL strings
    (e.g. ``https://``). Comments are stripped BEFORE whitespace collapse
    to prevent single-line ``//`` from swallowing the rest of the file.
    """
    import re
    # Remove single-line comments (but not // inside URLs like https://)
    text = re.sub(r'(?<!:)//[^\n]*\n', '\n', text)
    # Remove multi-line comments
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove space around certain chars
    text = re.sub(r'\s*([{}();,=+\-*/%!<>?:&|])\s*', r'\1', text)
    return text.strip()


def copy_static_assets():
    """Copy JS and CSS from source to dist. Minify main.js on the fly."""
    # Minify main.js -> main.min.js
    main_src = JS_SRC / "main.js"
    main_dst = JS_DST / "main.min.js"
    if main_src.exists():
        js_text = main_src.read_text(encoding="utf-8")
        minified = minify_js(js_text)
        main_dst.write_text(minified, encoding="utf-8")
        saved = len(js_text) - len(minified)
        pct = (saved / len(js_text)) * 100 if len(js_text) else 0
        print(f"  ✓ js/main.min.js  ({len(minified)} bytes, saved {saved} bytes / {pct:.0f}%)")
    else:
        print("  ⚠  js/main.js not found in source, skipping minification")

    # Copy remaining JS files
    for js_file in ["cc.min.js", "opencc.min.js"]:
        src = JS_SRC / js_file
        dst = JS_DST / js_file
        if src.exists():
            dst.write_bytes(src.read_bytes())
            print(f"  ✓ js/{js_file}")
        else:
            print(f"  ⚠  js/{js_file} not found in source, skipping")

    # Copy CSS files
    for css_file in ["styles.css", "layout.css"]:
        src = CSS_SRC / css_file
        dst = CSS_DST / css_file
        if src.exists():
            dst.write_bytes(src.read_bytes())
            print(f"  ✓ css/{css_file}")
        else:
            print(f"  ⚠  css/{css_file} not found in source, skipping")


# ── BUILD ─────────────────────────────────────────────────
def build_all():
    print("🔨 Building Soul Languages site...\n")

    # Step 1: Validate content
    print("📋 Validating content.json...")
    validate_content(data)

    # Step 2: Copy static assets
    print("📦 Copying static assets...")
    copy_static_assets()

    # Step 3: Generate HTML pages
    print("\n📄 Generating pages...")
    count = 0

    # index.html
    (DIST/"index.html").write_text(
        make_html("home", site["name"]+" — Soul Languages", site["description"],
                  build_page_body("home", data["pages"]["home"])),
        encoding="utf-8")
    print(f"  ✓ index.html")
    count += 1

    # 11 section pages
    for pid, pdata in data["pages"].items():
        if pid == "home": continue
        body = build_page_body(pid, pdata)
        title = pdata.get("title","靈語堂") + " — Soul Languages"
        desc  = pdata.get("description","") or site["description"]
        out = PAGES_DST / f"{pid}.html"
        out.write_text(make_html(pid, title, desc,
                   f'<main id="main" class="page" role="main"><div class="page-inner"><section class="prose"><h1 class="section-title">{pdata.get("title","")}</h1>\n{body}</section></div></main>'),
                   encoding="utf-8")
        print(f"  ✓ pages/{pid}.html")
        count += 1

    print(f"\n✅ {count} pages → {DIST}/")


# ── WATCH MODE ──────────────────────────────────────────────────
def get_mtimes():
    """Get modification times of all source files."""
    mtimes = {}
    mtimes["content.json"] = DATA.stat().st_mtime if DATA.exists() else 0
    for f in ["main.js", "main.min.js", "cc.min.js", "opencc.min.js"]:
        p = JS_SRC / f
        mtimes[f"js/{f}"] = p.stat().st_mtime if p.exists() else 0
    for f in ["styles.css", "layout.css"]:
        p = CSS_SRC / f
        mtimes[f"css/{f}"] = p.stat().st_mtime if p.exists() else 0
    return mtimes


def watch():
    """Watch mode: rebuild when source files change."""
    print("👀 Watch mode enabled — polling every 2 seconds...")
    print("   Watching: content.json, js/*, css/*")
    print("   Press Ctrl+C to stop.\n")

    last_mtimes = get_mtimes()
    build_all()

    try:
        while True:
            time.sleep(2)
            current = get_mtimes()
            changed = []
            for key, mtime in current.items():
                if mtime != last_mtimes.get(key, 0):
                    changed.append(key)

            if changed:
                print(f"\n🔄 Change detected: {', '.join(changed)}")
                last_mtimes = current
                build_all()
                print("\n👀 Watching for changes...")
    except KeyboardInterrupt:
        print("\n\n👋 Watch mode stopped.")
        sys.exit(0)


# ── CLI ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Soul Languages static site builder")
    parser.add_argument("--watch", action="store_true", help="Watch mode: rebuild on file changes")
    args = parser.parse_args()

    if args.watch:
        watch()
    else:
        build_all()
