"""Build the hosted site from site.html (source, Artifact format).

Outputs:
  index.html     English page at https://oneering.com/
  vi/index.html  Vietnamese page at https://oneering.com/vi/, pre-rendered from the VI dictionary
  sitemap.xml    both URLs with hreflang alternates
"""
import json, os, re, subprocess, datetime

SITE = "https://oneering.com"
TITLE = "Oneering | Engineering after Agile"
PAGES = {
    "en": {
        "path": "/", "file": "index.html", "locale": "en_US", "alt_locale": "vi_VN",
        "title": TITLE,
        "desc": "Oneering builds, improves and runs production software. AI agents do the work, a named engineer is accountable, and nothing ships until an independent check passes.",
    },
    "vi": {
        "path": "/vi/", "file": "vi/index.html", "locale": "vi_VN", "alt_locale": "en_US",
        "title": "Oneering | Engineering after Agile. Mô hình kỹ thuật phần mềm cho AI",
        "desc": "Oneering xây dựng, cải tiến và vận hành phần mềm production. AI agent làm việc, một kỹ sư đứng tên chịu trách nhiệm, và không gì được bàn giao khi chưa qua kiểm chứng độc lập.",
    },
}

src = open("site.html", encoding="utf-8").read()
# Artifact-only lines that do not belong on the hosted site.
src = src.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
src = re.sub(r'<title>.*?</title>\n', "", src, count=1)
src = re.sub(r'<meta name="description"[^>]*>\n', "", src, count=1)

# Read the VI dictionary straight from the page script, so there is one source of truth.
m = re.search(r"var VI = (\{.*?\n  \});", src, re.S)
VI = json.loads(subprocess.check_output(["node", "-e", f"process.stdout.write(JSON.stringify({m.group(1)}))"]))

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "path", "rect", "circle", "line", "polyline", "polygon", "stop", "use"}

def render_vi(html):
    """Replace the inner HTML of every element with data-i="key" by VI[key]."""
    out, pos, stack = [], 0, []  # stack items: (tag, key or None, inner_start)
    for t in re.finditer(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)([^>]*?)(/?)>", html):
        closing, tag, attrs, selfclose = t.group(1), t.group(2).lower(), t.group(3), t.group(4)
        if tag in ("script", "style") and not closing:
            continue
        if not closing:
            if tag in VOID or selfclose:
                continue
            k = re.search(r'data-i="([^"]+)"', attrs)
            stack.append((tag, k.group(1) if k else None, t.end()))
        else:
            while stack:
                otag, key, start = stack.pop()
                if otag == tag:
                    if key and key in VI and not any(s[1] in VI for s in stack):
                        out.append(html[pos:start]); out.append(VI[key]); pos = t.start()
                    break
    out.append(html[pos:])
    return "".join(out)

# Only the markup before the script is page content; keep the script untouched.
cut = src.index("<script>\n(function(){")
LD = json.dumps({"@context": "https://schema.org", "@graph": [
    {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Oneering", "url": f"{SITE}/", "logo": f"{SITE}/favicon.svg",
     "slogan": "Engineering after Agile.", "description": PAGES["en"]["desc"], "email": "one@oneering.com",
     "founder": {"@type": "Person", "name": "Nguyễn Long Nhật", "jobTitle": "Founder"},
     "knowsAbout": ["Outcome-Native Engineering", "AI-native software engineering", "Software delivery", "AI agents"]},
    {"@type": "WebSite", "@id": f"{SITE}/#site", "url": f"{SITE}/", "name": "Oneering", "inLanguage": ["en", "vi"],
     "publisher": {"@id": f"{SITE}/#org"}},
]}, ensure_ascii=False)

def head(lang):
    p = PAGES[lang]
    url = SITE + p["path"]
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{q["path"]}">\n' for l, q in PAGES.items())
    return f'''<!doctype html>
<html lang="{lang}" data-page-lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{p["title"]}</title>
<meta name="description" content="{p["desc"]}">
<link rel="canonical" href="{url}">
{alts}<link rel="alternate" hreflang="x-default" href="{SITE}/">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{p["title"]}">
<meta property="og:description" content="{p["desc"]}">
<meta property="og:image" content="{SITE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="Oneering">
<meta property="og:locale" content="{p["locale"]}">
<meta property="og:locale:alternate" content="{p["alt_locale"]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{p["title"]}">
<meta name="twitter:description" content="{p["desc"]}">
<meta name="twitter:image" content="{SITE}/og.png">
<meta name="robots" content="index, follow">
<script type="application/ld+json">{LD}</script>
<style>body{{margin:0}}[hidden]{{display:none!important}}img{{max-width:100%}}</style>
'''

for lang, p in PAGES.items():
    body = src if lang == "en" else render_vi(src[:cut]) + src[cut:]
    os.makedirs(os.path.dirname(p["file"]) or ".", exist_ok=True)
    open(p["file"], "w", encoding="utf-8").write(head(lang) + body + "\n</body>\n</html>\n")

today = datetime.date.today().isoformat()
alts = "".join(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{SITE}{q["path"]}"/>\n' for l, q in PAGES.items())
urls = "".join(f"  <url>\n    <loc>{SITE}{p['path']}</loc>\n    <lastmod>{today}</lastmod>\n{alts}  </url>\n" for p in PAGES.values())
open("sitemap.xml", "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + urls + "</urlset>\n")
print("built", ", ".join(p["file"] for p in PAGES.values()), "and sitemap.xml;", len(VI), "VI keys")
