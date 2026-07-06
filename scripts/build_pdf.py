#!/usr/bin/env python3
# Build a single print-ready HTML from the Myanmar book (fonts embedded),
# for Chrome --print-to-pdf. build.sh runs Chrome on the emitted HTML.
import os, re, sys, html, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _fonts import extract_fonts
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build")
os.makedirs(BUILD, exist_ok=True)
OUT_HTML = os.path.join(BUILD, "book_print.html")

TITLE = "Agentic Coding Basic for Junior Developers"
SUBTITLE = "ကုဒ်မရေးတတ်သေးခင် ကုဒ်ရေးခိုင်းတတ်အောင် သင်ပေးမည့် စာအုပ်"
AUTHOR = "Soe Thura"
LANG = "my"

CHAPTERS = [
    "01-what-is-agentic-coding", "02-meet-claude-code", "03-how-to-instruct-agents",
    "04-starting-the-project", "05-building-features", "06-bugs-and-testing",
    "07-skills", "08-context-window-and-tokens", "09-final-words",
]

REG_TTF, BOLD_TTF = extract_fonts(BUILD)

def b64(path):
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode()

REG = b64(REG_TTF)
BOLD = b64(BOLD_TTF)
COVER = b64(os.path.join(ROOT, "imgs", "cover.png"))

md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "attr_list"])

def read(p):
    with open(p, encoding="utf-8") as fh: return fh.read()

def rewrite_links(body):
    def repl(m):
        href = m.group(1); base = os.path.basename(href)
        if base.lower().endswith(".md"):
            stem = base[:-3]
            return 'href="#toc"' if stem.lower() == "readme" else 'href="#%s"' % stem
        return m.group(0)
    return re.sub(r'href="([^"]+)"', repl, body)

# chapters -> html sections
sections = []
toc_entries = []
for stem in CHAPTERS:
    md.reset()
    body = rewrite_links(md.convert(read(os.path.join(ROOT, "chapters", stem + ".md"))))
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    ttl = re.sub("<[^>]+>", "", m.group(1)).strip() if m else stem
    toc_entries.append((stem, ttl))
    sections.append('<section class="chapter" id="%s">\n%s\n</section>' % (stem, body))

# title page + note + build flow from README
readme = read(os.path.join(ROOT, "README.md"))
m = re.search(r"## ဒီစာအုပ်က ဘာအကြောင်းလဲ\s*\n+(.*?)\n\n", readme, re.S)
intro = m.group(1).strip() if m else ""
mn = re.search(r"(## မှတ်ချက်.*?)\n## ", readme, re.S)
note = mn.group(1).strip() if mn else ""
m2 = re.search(r"(## ဘာဆောက်မလဲ.*?)\n## ", readme, re.S)
build = m2.group(1).strip() if m2 else ""
md.reset(); intro_html = md.convert(intro)
md.reset(); note_html = md.convert(note)
md.reset(); build_html = md.convert(build)

toc_html = "\n".join(
    '<li><a href="#%s">%s</a></li>' % (s, html.escape(t)) for s, t in toc_entries
)

DOC = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<style>
@font-face {{ font-family:"Noto Sans Myanmar"; font-weight:normal;
  src:url(data:font/ttf;base64,{reg}) format("truetype"); }}
@font-face {{ font-family:"Noto Sans Myanmar"; font-weight:bold;
  src:url(data:font/ttf;base64,{bold}) format("truetype"); }}
@page {{ size: A4; margin: 18mm 16mm 20mm; }}
* {{ box-sizing: border-box; }}
html {{ hyphens: none; }}
body {{ font-family:"Noto Sans Myanmar","Padauk",sans-serif; line-height:1.85;
  color:#1a1a1a; margin:0; word-break:keep-all; font-size:11pt; }}
h1,h2,h3 {{ line-height:1.5; font-weight:bold; break-after:avoid; }}
h1 {{ font-size:1.5em; margin:0 0 .7em; }}
h2 {{ font-size:1.24em; margin:1.5em 0 .5em; border-bottom:1px solid #ddd; padding-bottom:.2em; }}
h3 {{ font-size:1.06em; margin:1.2em 0 .4em; }}
p {{ margin:.65em 0; text-align:left; }}
a {{ color:#0645ad; text-decoration:none; }}
code,pre {{ font-family:"SF Mono",Menlo,Consolas,monospace,"Noto Sans Myanmar"; }}
code {{ background:#f2f2f2; padding:.08em .32em; border-radius:3px; font-size:.9em; }}
pre {{ background:#f6f8fa; border:1px solid #e1e4e8; border-radius:6px; padding:.8em .9em;
  overflow-x:auto; white-space:pre-wrap; word-break:break-word; line-height:1.5;
  font-size:.86em; break-inside:avoid; }}
pre code {{ background:none; padding:0; font-size:1em; }}
blockquote {{ margin:1em 0; padding:.4em 1em; border-left:4px solid #c8c8c8;
  background:#fafafa; color:#333; break-inside:avoid; }}
table {{ border-collapse:collapse; width:100%; margin:1em 0; font-size:.92em; break-inside:avoid; }}
th,td {{ border:1px solid #ccc; padding:.4em .55em; text-align:left; vertical-align:top; }}
th {{ background:#f0f0f0; font-weight:bold; }}
hr {{ border:none; border-top:1px solid #ddd; margin:1.6em 0; }}
li {{ margin:.25em 0; }}
.chapter {{ break-before:page; }}
.cover {{ text-align:center; margin:0; }}
.cover img {{ width:auto; max-width:100%; max-height:250mm; }}
.epigraph {{ font-style:italic; color:#555; border-left:4px solid #ccc;
  padding:.3em 1em; margin:1.5em 0; }}
.toc {{ break-before:page; }}
.toc ol {{ line-height:2; }}
</style>
</head>
<body>

<div class="cover">
  <img src="data:image/png;base64,{cover}" alt="Cover"/>
</div>

<section class="intro chapter">
<blockquote class="epigraph">
"ကျုပ်တို့ငယ်ငယ်က ကုဒ်ဆိုတာ ကိုယ်တိုင်ရေးမှ ရတယ်။<br/>
အခုခေတ်ကျတော့ ကုဒ်ကို စကားပြောပြီး ရေးခိုင်းလို့ရနေပြီ။<br/>
ဒါကို မသိရင် ခေတ်နောက်ကျတယ်။ သိပြီး မသုံးတတ်ရင် ပိုဆိုးတယ်။"
</blockquote>
{intro}
{note}
{build}
</section>

<section class="toc" id="toc">
<h1>မာတိကာ</h1>
<ol>
{toc}
</ol>
</section>

{sections}

</body>
</html>
""".format(lang=LANG, title=html.escape(TITLE), subtitle=html.escape(SUBTITLE),
           author=html.escape(AUTHOR), reg=REG, bold=BOLD, cover=COVER,
           intro=intro_html, note=note_html, build=build_html, toc=toc_html,
           sections="\n\n".join(sections))

with open(OUT_HTML, "w", encoding="utf-8") as fh:
    fh.write(DOC)
print("wrote", OUT_HTML, len(DOC), "chars,", len(CHAPTERS), "chapters")
