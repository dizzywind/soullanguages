import re, glob, json
from html.parser import HTMLParser

class StructExtractor(HTMLParser):
    TEXT_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "a", "span"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.skip_depth = 0
        self.items = []
        self.images = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1
            return
        a = dict(attrs)
        self.stack.append((tag, a.get("class", "")))
        if tag == "img":
            src = a.get("src", "")
            if "googleusercontent" in src and not src.startswith("data:"):
                self.images.append(src)

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"}:
            if self.skip_depth > 0: self.skip_depth -= 1
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_startendtag(self, tag, attrs):
        if tag == "img":
            src = dict(attrs).get("src", "")
            if "googleusercontent" in src and not src.startswith("data:"):
                self.images.append(src)

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        t = re.sub(r"\s+", " ", data).strip()
        if not t:
            return
        # find nearest meaningful ancestor
        best = None
        for tag, cls in reversed(self.stack):
            if tag in self.TEXT_TAGS or re.search(r"\bzfr3Q\b", cls):
                best = (tag, "zfr3Q" in cls)
                if re.search(r"\bzfr3Q\b", cls):
                    break
        if best is None:
            return
        tag, in_content = best
        is_marker = t in {"繁體", "简体", "简体", "簡體"}
        if not in_content and not is_marker:
            return
        # skip pure nav links (inside <a> without zfr3Q ancestor handled above)
        if t.startswith("Collapse") or t.startswith("Expand"):
            return
        self.items.append({"tag": tag, "text": t})

def extract(path):
    html = open(path, encoding="utf-8").read()
    p = StructExtractor()
    p.feed(html)
    # drop consecutive duplicates & nav noise
    out, prev = [], None
    NAV = {"主頁","經文與分享","下載","聯絡我們","Home","Sutras","Contact Us",
           "Soul Languages","靈語堂","懺悔偈","綠度母心咒","發菩提心義訣",
           "般若波羅蜜多心經","地藏菩薩本願經心要頌","關於空性","心佛頌",
           "Repentance Chant","Confirm","Visit Soul Languages English site",
           "Search this site","Embedded Files","More","Google Sites","Report abuse"}
    for it in p.items:
        t = it["text"]
        if t in NAV:
            continue
        if t == prev:
            continue
        prev = t
        out.append(it)
    return out

result = {}
for f in sorted(glob.glob("*.html")):
    result[f[:-5]] = extract(f)

json.dump(result, open("structured.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in result.items():
    print(f"== {k}: {len(v)} items")
