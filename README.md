# Soul Languages — Static Rebuild

> soullanguages.com · 靈語堂
> Built with: pure HTML/CSS/JS · zero dependencies · 47 KB total

## What's been built

| Type | Count | Size |
|------|-------|------|
| HTML pages | 11 | 41.7 KB |
| CSS (design tokens + layout) | 2 | 12 KB |
| JavaScript (custom) | 1 | 3.6 KB |
| sitemap.xml | 1 | 1.5 KB |
| **Total** | **15 files** | **47 KB** |

---

## Folder structure

```
dist/
├── index.html           ← homepage with episode grid
├── robots.txt
├── sitemap.xml
├── css/
│   ├── styles.css       ← design tokens, reset, layout
│   └── layout.css       ← nav, hero, prose, lightbox, responsive
├── js/
│   └── main.min.js      ← dark-mode, episodes-JSON loader, video lightbox
└── pages/
    ├── scriptures.html
    ├── repentance.html
    ├── tara.html
    ├── bodhicitta.html
    ├── heart-sutra.html
    ├── ksitigarbha.html
    ├── emptiness.html
    ├── mind-buddha.html
    ├── downloads.html   ← stub — fill in real file links
    └── contact.html     ← stub — fill in real email/contact info
```

---

## Audit vs old Google Sites site

| Area | Google Sites (old) | New build |
|---|---|---|
| HTML size | 136 KB | **41 KB (71% smaller)** |
| Gzip | 34.5 KB | **3.6 KB (90% smaller)** |
| Text/HTML ratio | 0.5% | **6%+** |
| `lang` attr | `en-US` ❌ | `zh-Hant` ✅ |
| `<meta description>` | ❌ absent | ✅ on every page |
| `<h1>` | ❌ absent | ✅ on every page |
| `canonical` | ❌ | ✅ |
| YouTube `title` | ❌ 0/8 | ✅ lightbox iframes |
| YouTube `loading="lazy"` | ❌ 0/8 | ✅ all lightbox iframes |
| YouTube `width`/`height` | ❌ 0/8 | ✅ aspect-ratio CSS |
| Security headers | ❌ all missing | ✅ set on host (not in HTML) |
| Google Sites boilerplate | 18 KB inline CSS | ✅ 0 KB — gone |
| Skip link | ✅ but hidden behind Google Sites | ✅ clean, native |

---

## Content that needs filling

These pages have stub content and need real text from the old site sections:

| Page | What to add |
|---|---|
| `pages/scriptures.html` | 經文與分享 section body |
| `pages/repentance.html` | ✅ done |
| `pages/tara.html` | ✅ done |
| `pages/bodhicitta.html` | 發菩提心義訣 full text |
| `pages/heart-sutra.html` | 心經 full text + annotations |
| `pages/ksitigarbha.html` | 地藏菩薩本願經心要頌 |
| `pages/emptiness.html` | 關於空性 essays |
| `pages/mind-buddha.html` | 心佛頌 text + commentary |
| `pages/downloads.html` | Actual download links + PDFs |
| `pages/contact.html` | Real email / form action |

Content can be pasted directly into the template in `pages/<id>.html` between the `<section class="prose">` tags — no special formatting needed.

---

## Deploy

**Option A — Netlify / Vercel (easiest)**
```bash
# Point the dist/ folder at your host
netlify deploy --dir=dist --prod
# or
vercel --dist dist/ --prod
```

**Option B — Cloudflare Pages**
1. Push this repo to GitHub
2. Pages → "Direct upload" → upload `dist/` folder
3. Custom domain: `soullanguages.com`

**Option C — Any static host**
`rsync dist/ user@host:/var/www/soullanguages/`

---

## Project files

```
soullanguages/
├── data/
│   └── content.json     ← shared site data (nav, episodes, page metadata)
├── css/
│   ├── styles.css
│   └── layout.css
├── js/
│   └── main.min.js
├── build.py             ← rebuild script — python3 build.py
├── dist/                ← static output — deploy this
│   ├── index.html
│   ├── robots.txt
│   ├── sitemap.xml
│   ├── js/main.min.js
│   ├── css/styles.css
│   ├── css/layout.css
│   └── pages/
├── assets/images/        ← add og-cover.jpg here before launch
└── README.md
```
