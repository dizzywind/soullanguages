import urllib.parse, urllib.request, os, time

BASE_ZH = "https://www.soullanguages.com"
BASE_EN = "https://en.soullanguages.com"

pages = [
    ("zh-home.html",        BASE_ZH + "/" + urllib.parse.quote("主頁")),
    ("zh-sutras.html",      BASE_ZH + "/sutras"),
    ("zh-repentance.html",  BASE_ZH + "/sutras/repentance-chant"),
    ("zh-tara.html",        BASE_ZH + "/sutras/" + urllib.parse.quote("綠度母心咒")),
    ("zh-bodhicitta.html",  BASE_ZH + "/sutras/" + urllib.parse.quote("發菩提心義訣")),
    ("zh-heartsutra.html",  BASE_ZH + "/sutras/" + urllib.parse.quote("般若波羅蜜多心經")),
    ("zh-ksitigarbha.html", BASE_ZH + "/sutras/" + urllib.parse.quote("地藏菩薩本願經心要頌")),
    ("zh-emptiness.html",   BASE_ZH + "/sutras/" + urllib.parse.quote("關於空性")),
    ("zh-mindbuddha.html",  BASE_ZH + "/sutras/" + urllib.parse.quote("心佛頌")),
    ("zh-downloads.html",   BASE_ZH + "/" + urllib.parse.quote("下載")),
    ("en-home.html",        BASE_EN + "/"),
    ("en-sutras.html",      BASE_EN + "/sutras"),
    ("en-repentance.html",  BASE_EN + "/repentance-chant"),
]

req_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

for name, url in pages:
    req = urllib.request.Request(url, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        with open(name, "wb") as f:
            f.write(data)
        print(f"OK   {name:24s} {len(data):>8d} bytes  <- {url}")
    except Exception as e:
        print(f"FAIL {name}: {e}")
    time.sleep(0.4)
