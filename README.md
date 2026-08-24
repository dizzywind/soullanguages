# Soul Languages 靈語堂

Bilingual (繁體中文 / English) static site for [soullanguages.com](https://www.soullanguages.com), migrated off Google Sites.

Built with [Astro](https://astro.build) — zero client-side framework, self-hosted fonts and assets, deployed to GitHub Pages at **https://dizzywind.github.io/soullanguages/**

## Structure

```
src/
├── content/… via src/data/content/*.json   ← scripture texts, episodes, downloads
├── data/site.ts            ← nav, UI strings, typed accessors
├── layouts/BaseLayout.astro ← SEO (canonical/hreflang/OG), header, footer
├── components/             ← Blocks renderer, EpisodeGrid (click-to-load YouTube), etc.
└── pages/                  ← zh at root, en under /en/
```

Content model: every sutra page carries its scraped variants — `hant` (繁體), `simp` (简体) and optional `en`. Line-level pinyin from the original site is preserved as `pair` blocks (Heart Sutra, Ksitigarbha). The Mind Buddha Hymn page is an image of the original calligraphy; a placeholder ships until the original is fetched (see below).

## Development

Requires Node 22+.

```bash
npm install
npm run dev        # http://localhost:4321/soullanguages/
npm run build      # outputs dist/
npm run preview
```

## Migration provenance

`scripts/migration/` documents how content was produced:

- `fetch.py`, `extract2.py` — scrape the live Google Sites into structured JSON
- `migrate.py` — convert the scrape into `src/data/content/*.json` (no hand-typed scripture)
- `verify-fidelity.py` — after build, asserts every live-site line appears verbatim in `dist/`
- `fetch-original-images.sh` — downloads the few images still hosted on Google's CDN (blocked from some datacenter networks); run once from any normal connection

## Deploy

Push to `main` → GitHub Actions builds with `withastro/action` and publishes to GitHub Pages.
Ensure *Settings ▸ Pages ▸ Source* is set to **GitHub Actions**.

To use the custom domain later: add a `public/CNAME` file and point DNS at GitHub Pages.
