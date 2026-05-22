# Soul Languages — Deployment Test Plan

Run this checklist after every deployment. Each check must pass before declaring the deployment complete.

---

## Phase 1: Server-Side Checks

### 1.1 Build passes
- [ ] `python3 build.py` exits 0
- [ ] All 11 pages generated in `dist/` (index.html + 10 in `pages/`)

### 1.2 Path audit — root page
- [ ] CSS: `href="css/styles.css"` — resolves correctly
- [ ] JS: `src="js/main.min.js"` — resolves correctly
- [ ] Nav home link: `href="index.html"`
- [ ] Nav other links: `href="pages/SLUG.html"` (e.g., `pages/scriptures.html`)
- [ ] Logo link: `href="index.html"`

### 1.3 Path audit — sub-page (e.g., `pages/scriptures.html`)
- [ ] CSS: `href="../css/styles.css"` — resolves correctly
- [ ] JS: `src="../js/main.min.js"` — resolves correctly
- [ ] Nav home link: `href="../index.html"`
- [ ] Nav other links: `href="SLUG.html"` (same directory, e.g., `repentance.html`)
- [ ] Logo link: `href="../index.html"`

### 1.4 Footer links — root
- [ ] All footer `<a>` hrefs point to correct relative paths

### 1.5 Footer links — sub-page
- [ ] All footer `<a>` hrefs use `../` prefix

---

## Phase 2: Visual Checks (browser or screenshot)

### 2.1 Dark theme
- [ ] Body background is `#0f0d0a` (dark brown/black)
- [ ] Text is `#e8ddd0` (warm off-white)
- [ ] Gold accents appear on headings, borders, active nav

### 2.2 Light theme toggle
- [ ] Clicking theme toggle button switches to light mode
- [ ] Light mode: background `#f5f0e8`, text `#2c241e`
- [ ] Toggle icon changes (☀️ / 🌙)
- [ ] Setting persists on page reload (`localStorage`)

### 2.3 Navigation
- [ ] Sticky glassmorphism header visible on scroll
- [ ] Active nav item has gold highlight
- [ ] Logo "靈語堂" renders in serif font, gold + amber

### 2.4 Hero section (home page)
- [ ] ☸ icon visible
- [ ] Title "靈語堂" has gold-to-amber gradient text
- [ ] Gold divider line visible
- [ ] CTA button "觀看系列影片 ↓" has gold gradient background

### 2.5 Episode card grid
- [ ] Each card has thumbnail image (`card-img`)
- [ ] EP number visible (`card-num`)
- [ ] English title (`card-title`) + Chinese subtitle (`card-sub`)
- [ ] Cards lift on hover (translateY(-2px) + glow)

### 2.6 Content pages (e.g., scriptures.html)
- [ ] Page header visible with title + description
- [ ] Content in prose-section, readable
- [ ] Zen-box styled quotes where applicable

### 2.7 Footer
- [ ] Footer links (主頁, 經文與分享, 聯絡我們, YouTube)
- [ ] Copyright line visible
- [ ] No broken links

---

## Phase 3: Mobile / Responsive

### 3.1 Viewport < 768px
- [ ] Desktop nav items hidden
- [ ] ☰ hamburger button visible in header
- [ ] Clicking ☰ opens full-width dropdown nav
- [ ] Clicking a nav link closes the dropdown
- [ ] Tapping ✕ closes the dropdown
- [ ] Card grid collapses to single column
- [ ] Section title bar hidden
- [ ] Hero/typography scales proportionally

### 3.2 Touch targets
- [ ] All buttons ≥ 36×36px
- [ ] Nav links have adequate padding for tap

---

## Phase 4: Functional Checks

### 4.1 Video lightbox
- [ ] Clicking episode card thumbnail opens lightbox
- [ ] Lightbox overlay covers full viewport
- [ ] Close button works (✕)
- [ ] Clicking outside overlay closes it

### 4.2 Language toggle
- [ ] "簡" button toggles Simplified/Traditional Chinese
- [ ] Toggle persists on page reload

### 4.3 Navigation
- [ ] All nav links navigate to correct URL
- [ ] Active nav class highlights current page

---

## Phase 5: External Verification

### 5.1 Live site
- [ ] `curl -sI https://dizzywind.github.io/soullanguages/` → HTTP 200
- [ ] `curl -sI https://dizzywind.github.io/soullanguages/css/styles.css` → HTTP 200
- [ ] `curl -sI https://dizzywind.github.io/soullanguages/pages/scriptures.html` → HTTP 200
- [ ] `curl -sI https://dizzywind.github.io/soullanguages/js/main.min.js` → HTTP 200

### 5.2 GitHub Actions
- [ ] CI workflow completes with ✅ (build + deploy both pass)

---

## Quick CLI Verification Command

```bash
# After deployment — run from repo root
echo "=== ROOT CSS ===" && grep -o 'href="[^"]*css[^"]*"' dist/index.html
echo "=== SUB-PAGE CSS ===" && grep -o 'href="[^"]*css[^"]*"' dist/pages/scriptures.html
echo "=== NAV ROOT ===" && grep -o 'href="[^"]*\.html"' dist/index.html | grep -v youtube | grep -v canonical | grep -v og:
echo "=== NAV SUB ===" && grep -o 'href="[^"]*\.html"' dist/pages/scriptures.html | grep -v youtube | grep -v canonical | grep -v og: | head -8
echo "=== LIGHT THEME CSS ===" && grep -c '\[data-theme="light"\]' css/styles.css
echo "=== MOBILE NAV ===" && grep -c 'mobile-nav-toggle' dist/index.html
```
