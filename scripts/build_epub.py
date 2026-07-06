#!/usr/bin/env python3
# Build an EPUB 3 from the Myanmar Agentic Coding book.
import os, re, sys, zipfile, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _fonts import extract_fonts
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build")
DIST = os.path.join(ROOT, "dist")
os.makedirs(BUILD, exist_ok=True)
os.makedirs(DIST, exist_ok=True)
OUT_EPUB = os.path.join(DIST, "agentic-coding-basic-mm.epub")

TITLE = "Agentic Coding Basic for Junior Developers"
SUBTITLE = "ကုဒ်မရေးတတ်သေးခင် ကုဒ်ရေးခိုင်းတတ်အောင် သင်ပေးမည့် စာအုပ်"
AUTHOR = "Soe Thura"
LANG = "my"
BOOK_ID = "urn:uuid:myaree-store-agentic-coding-basic-2026"

CHAPTERS = [
    "01-what-is-agentic-coding",
    "02-meet-claude-code",
    "03-how-to-instruct-agents",
    "04-starting-the-project",
    "05-building-features",
    "06-bugs-and-testing",
    "07-skills",
    "08-context-window-and-tokens",
    "09-final-words",
]

REG_TTF, BOLD_TTF = extract_fonts(BUILD)

# ---- Markdown -> XHTML ----
md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "attr_list"])

def rewrite_links(body):
    def repl(m):
        href = m.group(1)
        base = os.path.basename(href)
        if base.lower().endswith(".md"):
            stem = base[:-3]
            target = "nav.xhtml" if stem.lower() == "readme" else stem + ".xhtml"
            return 'href="%s"' % target
        return m.group(0)
    return re.sub(r'href="([^"]+)"', repl, body)

def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

XHTML_TMPL = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{lang}" xml:lang="{lang}">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{body}
</body>
</html>
"""

def make_chapter_xhtml(stem):
    md.reset()
    raw = read(os.path.join(ROOT, "chapters", stem + ".md"))
    body = md.convert(raw)
    body = rewrite_links(body)
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    ttl = re.sub("<[^>]+>", "", m.group(1)).strip() if m else stem
    return XHTML_TMPL.format(lang=LANG, title=html.escape(ttl), body=body), ttl

# Title page built from README intro (custom, without the md TOC table / nav links)
def make_title_page():
    readme = read(os.path.join(ROOT, "README.md"))
    intro_para = ""
    m = re.search(r"## ဒီစာအုပ်က ဘာအကြောင်းလဲ\s*\n+(.*?)\n\n", readme, re.S)
    if m:
        intro_para = m.group(1).strip()
    mn = re.search(r"(## မှတ်ချက်.*?)\n## ", readme, re.S)
    note_section = mn.group(1).strip() if mn else ""
    m2 = re.search(r"(## ဘာဆောက်မလဲ.*?)\n## ", readme, re.S)
    build_section = m2.group(1).strip() if m2 else ""
    md.reset(); intro_html = md.convert(intro_para)
    md.reset(); note_html = md.convert(note_section)
    md.reset(); build_html = md.convert(build_section)
    body = (
        '<div class="titlepage">\n'
        '<h1 class="booktitle">%s</h1>\n'
        '<p class="subtitle">%s</p>\n'
        '<p class="author">%s</p>\n'
        '<p class="langnote">(မြန်မာဘာသာဖြင့် ရေးသားထားသည်)</p>\n'
        '</div>\n'
        '<hr/>\n'
        '%s\n%s\n%s\n'
    ) % (html.escape(TITLE), html.escape(SUBTITLE), html.escape(AUTHOR),
         intro_html, note_html, build_html)
    return XHTML_TMPL.format(lang=LANG, title=html.escape(TITLE), body=body)

def make_cover_page():
    body = '<div class="coverpage"><img src="images/cover.png" alt="Cover"/></div>'
    return XHTML_TMPL.format(lang=LANG, title="Cover", body=body)

# ---- CSS ----
CSS = """@font-face {
  font-family: "Noto Sans Myanmar";
  font-weight: normal;
  font-style: normal;
  src: url("fonts/NotoSansMyanmar-Regular.ttf");
}
@font-face {
  font-family: "Noto Sans Myanmar";
  font-weight: bold;
  font-style: normal;
  src: url("fonts/NotoSansMyanmar-Bold.ttf");
}
html { -epub-hyphens: none; hyphens: none; }
body {
  font-family: "Noto Sans Myanmar", "Padauk", "Myanmar Text", "Pyidaungsu", sans-serif;
  line-height: 1.85;
  margin: 5%;
  color: #1a1a1a;
  word-break: keep-all;
}
h1, h2, h3 { line-height: 1.5; font-weight: bold; }
h1 { font-size: 1.5em; margin: 1.2em 0 0.8em; }
h2 { font-size: 1.25em; margin: 1.6em 0 0.6em; border-bottom: 1px solid #ddd; padding-bottom: 0.2em; }
h3 { font-size: 1.08em; margin: 1.3em 0 0.5em; }
p { margin: 0.7em 0; text-align: left; }
a { color: #0645ad; text-decoration: none; }
strong { font-weight: bold; }
code, pre {
  font-family: "SF Mono", Menlo, Consolas, "DejaVu Sans Mono", monospace, "Noto Sans Myanmar";
}
code {
  background: #f2f2f2;
  padding: 0.1em 0.35em;
  border-radius: 3px;
  font-size: 0.92em;
}
pre {
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  padding: 0.9em 1em;
  overflow-x: auto;
  line-height: 1.55;
  white-space: pre;
  font-size: 0.9em;
}
pre code { background: none; padding: 0; border-radius: 0; font-size: 1em; }
blockquote {
  margin: 1em 0;
  padding: 0.5em 1em;
  border-left: 4px solid #c8c8c8;
  background: #fafafa;
  color: #333;
}
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.95em; }
th, td { border: 1px solid #ccc; padding: 0.45em 0.6em; text-align: left; vertical-align: top; }
th { background: #f0f0f0; font-weight: bold; }
hr { border: none; border-top: 1px solid #ddd; margin: 2em 0; }
.coverpage { text-align: center; margin: 0; padding: 0; }
.coverpage img { max-width: 100%; height: auto; }
.titlepage { text-align: center; margin: 2.5em 0; }
.booktitle { font-size: 1.7em; border: none; }
.subtitle { font-size: 1.1em; color: #444; }
.author { margin-top: 1.5em; font-weight: bold; }
.langnote { color: #777; font-style: italic; }
"""

# ---- Assemble EPUB ----
chapter_files = []   # (filename, title)
pages = {}           # filename -> xhtml string

pages["cover.xhtml"] = make_cover_page()
pages["title.xhtml"] = make_title_page()
for stem in CHAPTERS:
    xhtml, ttl = make_chapter_xhtml(stem)
    fn = stem + ".xhtml"
    pages[fn] = xhtml
    chapter_files.append((fn, ttl))

# nav.xhtml (EPUB3)
nav_items = '\n'.join(
    '    <li><a href="%s">%s</a></li>' % (fn, html.escape(ttl)) for fn, ttl in chapter_files
)
nav_xhtml = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{lang}" xml:lang="{lang}">
<head><meta charset="utf-8"/><title>မာတိကာ</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
<nav epub:type="toc" id="toc">
<h1>မာတိကာ</h1>
<ol>
{items}
</ol>
</nav>
</body>
</html>
""".format(lang=LANG, items=nav_items)

# toc.ncx (EPUB2 compat)
navpoints = []
for i, (fn, ttl) in enumerate(chapter_files, start=1):
    navpoints.append(
        '  <navPoint id="np%d" playOrder="%d"><navLabel><text>%s</text></navLabel>'
        '<content src="%s"/></navPoint>' % (i, i, html.escape(ttl), fn)
    )
ncx = """<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head>
<meta name="dtb:uid" content="{bid}"/>
<meta name="dtb:depth" content="1"/>
<meta name="dtb:totalPageCount" content="0"/>
<meta name="dtb:maxPageNumber" content="0"/>
</head>
<docTitle><text>{title}</text></docTitle>
<navMap>
{nav}
</navMap>
</ncx>
""".format(bid=BOOK_ID, title=html.escape(TITLE), nav="\n".join(navpoints))

# content.opf
manifest = [
    '<item id="css" href="style.css" media-type="text/css"/>',
    '<item id="font-reg" href="fonts/NotoSansMyanmar-Regular.ttf" media-type="font/ttf"/>',
    '<item id="font-bold" href="fonts/NotoSansMyanmar-Bold.ttf" media-type="font/ttf"/>',
    '<item id="cover-img" href="images/cover.png" media-type="image/png" properties="cover-image"/>',
    '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
    '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
    '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
    '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>',
]
spine = ['<itemref idref="cover"/>', '<itemref idref="title"/>']
for i, (fn, ttl) in enumerate(chapter_files, start=1):
    iid = "ch%02d" % i
    manifest.append('<item id="%s" href="%s" media-type="application/xhtml+xml"/>' % (iid, fn))
    spine.append('<itemref idref="%s"/>' % iid)

opf = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{lang}">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:identifier id="bookid">{bid}</dc:identifier>
  <dc:title>{title}</dc:title>
  <dc:creator>{author}</dc:creator>
  <dc:language>{lang}</dc:language>
  <dc:description>{subtitle}</dc:description>
  <meta name="cover" content="cover-img"/>
  <meta property="dcterms:modified">2026-07-06T00:00:00Z</meta>
</metadata>
<manifest>
{manifest}
</manifest>
<spine toc="ncx">
{spine}
</spine>
</package>
""".format(lang=LANG, bid=BOOK_ID, title=html.escape(TITLE), author=html.escape(AUTHOR),
           subtitle=html.escape(SUBTITLE), manifest="\n".join(manifest), spine="\n".join(spine))

container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""

# Write zip
if os.path.exists(OUT_EPUB):
    os.remove(OUT_EPUB)
with zipfile.ZipFile(OUT_EPUB, "w") as z:
    # mimetype MUST be first and stored (uncompressed)
    z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
    z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
    z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
    z.writestr("OEBPS/toc.ncx", ncx, compress_type=zipfile.ZIP_DEFLATED)
    z.writestr("OEBPS/nav.xhtml", nav_xhtml, compress_type=zipfile.ZIP_DEFLATED)
    z.writestr("OEBPS/style.css", CSS, compress_type=zipfile.ZIP_DEFLATED)
    for fn, page in pages.items():
        z.writestr("OEBPS/" + fn, page, compress_type=zipfile.ZIP_DEFLATED)
    with open(REG_TTF, "rb") as fh:
        z.writestr("OEBPS/fonts/NotoSansMyanmar-Regular.ttf", fh.read(), compress_type=zipfile.ZIP_DEFLATED)
    with open(BOLD_TTF, "rb") as fh:
        z.writestr("OEBPS/fonts/NotoSansMyanmar-Bold.ttf", fh.read(), compress_type=zipfile.ZIP_DEFLATED)
    with open(os.path.join(ROOT, "imgs", "cover.png"), "rb") as fh:
        z.writestr("OEBPS/images/cover.png", fh.read(), compress_type=zipfile.ZIP_DEFLATED)

print("wrote", OUT_EPUB, os.path.getsize(OUT_EPUB), "bytes")
print("chapters:", len(chapter_files))
