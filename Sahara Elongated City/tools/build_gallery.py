#!/usr/bin/env python3
"""Build gallery.html — numbered image carousels for review.

Usage: python3 tools/build_gallery.py img-candidates.json gallery.html

Images are hot-linked from Wikimedia Commons' own CDN via Special:FilePath,
which resolves any filename to a resized thumbnail without needing the
hashed upload path. Nothing is downloaded at build time.
"""
import json, sys, html
from urllib.parse import quote

SECTIONS = [
    ("hero",       "Landing hero",              "index.html — the full-screen opener behind SAHARA ELONGATED CITY"),
    ("vision",     "01 · The Vision",           "index.html — the Sahara itself: dunes, scale, emptiness as inventory"),
    ("gate",       "02 · The Gate",             "index.html — one gate, a really good one; desert fortresses and roads to nowhere"),
    ("sand",       "03 · The Sand",             "index.html — sand → silicon → spaceships"),
    ("machine",    "04 · The Machine",          "index.html — the 3D printer that makes one home per day"),
    ("water",      "05 · The Water",            "index.html — oases, aquifers, glacial meltwater; refill, baby, refill"),
    ("calendar",   "06 · The Calendar",         "index.html — 13 × 28, the Moon keeps time"),
    ("language",   "07 · The Language",         "index.html — Esperanto"),
    ("zone",       "08 · The Zone",             "index.html — enclaves, festivals, culture and vibes as tax"),
    ("lagoons",    "09 · The Lagoons",          "index.html — mangroves, atolls, new ecosystems from surplus sand"),
    ("ask",        "10 · The Ask",              "index.html — YC's desert-flooding RFS; phytoplankton oases from orbit"),
    ("credo",      "The Credo",                 "index.html — night sky over the dunes"),
    ("qattara",    "Qattara Depression",        "qattara.html — hero: the escarpment, the salt, the Western Desert"),
    ("lakechad",   "Lake Chad Refill",          "lake-chad.html — hero: the shrinking lake from orbit, the shore, the people"),
    ("saltonsea",  "Salton Sea Revival",        "salton-sea.html — hero: the sea from orbit, Bombay Beach, the salt shore"),
    ("kazakhstan", "Kazakhstan Deal",           "kazakhstan.html — hero: Soyuz off the pad at Baikonur, the steppe"),
    ("pipeline",   "Arctic Pipeline",           "pipeline.html — hero: Greenland melt, pipe-laying, the deep"),
    ("prospectus", "The Anti-Prospectus (new)", "index.html — artificial islands, bunkers, turquoise tax havens"),
]

def hotlink(fname, width=1000):
    f = fname.strip().replace(" ", "_")
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(f)}?width={width}"

def main(src, out):
    data = json.load(open(src))
    by_id = {}
    for s in data.get("sections", []):
        by_id.setdefault(s["id"], []).extend(s.get("images", []))

    parts = []
    parts.append("""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Image Review — Sahara Elongated City</title>
<style>
:root{--night:#0d0a14;--ink:#f5eede;--muted:#b9a98c;--sand:#e8c98a;--dusk:#ff7a3c;--glacier:#9be7ff}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--night);color:var(--ink);font-family:Georgia,serif;line-height:1.5}
.mono{font-family:'Courier New',monospace;letter-spacing:.08em}
header{padding:2.5rem 1.2rem 1.5rem;text-align:center;border-bottom:1px solid #2a2138}
header h1{font-size:clamp(1.6rem,5vw,2.6rem);text-transform:uppercase;letter-spacing:-.01em}
header p{color:var(--muted);max-width:44rem;margin:.8rem auto 0;font-size:.95rem}
header code{background:#1a1226;padding:.1em .4em;color:var(--sand)}
nav.toc{display:flex;flex-wrap:wrap;gap:.4rem;justify-content:center;padding:1rem;border-bottom:1px solid #2a2138}
nav.toc a{font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);text-decoration:none;border:1px solid #3a2f4a;border-radius:999px;padding:.3em .8em}
nav.toc a:hover{color:var(--dusk);border-color:var(--dusk)}
section{padding:2.5rem 0 1.5rem;border-bottom:1px solid #1f1a2e}
.sh{padding:0 1.2rem;max-width:72rem;margin:0 auto}
.sh h2{font-size:1.4rem;text-transform:uppercase;letter-spacing:.02em}
.sh .where{color:var(--muted);font-size:.85rem;font-style:italic;margin-top:.2rem}
.sh .count{color:var(--dusk);font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;margin-top:.5rem}
.wrap{position:relative;max-width:72rem;margin:1.2rem auto 0}
.track{display:flex;gap:.8rem;overflow-x:auto;scroll-snap-type:x mandatory;padding:0 1.2rem 1rem;scrollbar-width:thin}
.slide{flex:0 0 min(86vw,34rem);scroll-snap-align:start;background:#14101c;border:1px solid #2a2138}
.slide .im{position:relative;aspect-ratio:16/10;background:#1a1226;overflow:hidden}
.slide img{width:100%;height:100%;object-fit:cover;display:block}
.slide .num{position:absolute;top:.6rem;left:.6rem;background:var(--dusk);color:var(--night);font-weight:900;font-family:'Courier New',monospace;font-size:1.1rem;padding:.15em .6em;border-radius:4px}
.slide .meta{padding:.7rem .8rem .9rem;font-size:.8rem;color:var(--muted)}
.slide .meta b{color:var(--ink);font-weight:normal;display:block;font-size:.85rem;margin-bottom:.3rem}
.slide .meta .lic{color:var(--glacier);font-size:.72rem}
.slide .meta a{color:var(--sand);text-decoration:none;font-size:.72rem}
.btn{position:absolute;top:38%;width:2.4rem;height:2.4rem;border-radius:50%;border:1px solid var(--sand);background:rgba(13,10,20,.85);color:var(--sand);font-size:1.2rem;cursor:pointer;display:none}
@media(min-width:900px){.btn{display:block}}
.btn.l{left:.3rem}.btn.r{right:.3rem}
.empty{padding:0 1.2rem;color:var(--muted);font-style:italic}
footer{padding:2rem 1.2rem;text-align:center;color:#574c60;font-size:.75rem}
footer a{color:#8a5a1e}
</style></head><body>
<header>
  <h1>🖼 Image Review</h1>
  <p>Numbered candidates for every section, hot-linked from Wikimedia Commons (free licenses / public domain — final author + license get confirmed on the file page before we ship). Swipe or scroll each row. Then just tell me picks like <code>vision: 3, qattara: 7, hero: 2</code> — or "none, look again" for a section.</p>
</header>
""")
    parts.append('<nav class="toc mono">' + "".join(
        f'<a href="#{sid}">{html.escape(title)}</a>' for sid, title, _ in SECTIONS) + "</nav>")

    for sid, title, where in SECTIONS:
        imgs = by_id.get(sid, [])
        parts.append(f'<section id="{sid}"><div class="sh"><h2>{html.escape(title)}</h2>'
                     f'<div class="where">{html.escape(where)}</div>'
                     f'<div class="count mono">{len(imgs)} candidates</div></div>')
        if not imgs:
            parts.append('<p class="empty">No candidates found yet for this section.</p></section>')
            continue
        parts.append(f'<div class="wrap"><button class="btn l" data-t="{sid}" data-d="-1" aria-label="previous">‹</button>'
                     f'<div class="track" id="t-{sid}">')
        for i, im in enumerate(imgs, 1):
            f = im.get("file", "")
            page = im.get("page_url") or f"https://commons.wikimedia.org/wiki/File:{quote(f.replace(' ', '_'))}"
            lic = im.get("license_hint") or "license: see file page"
            auth = im.get("author_hint")
            note = im.get("note") or ""
            cred = html.escape(lic) + (f" · {html.escape(auth)}" if auth else "")
            parts.append(
                f'<figure class="slide"><div class="im"><span class="num">{i}</span>'
                f'<img loading="lazy" decoding="async" src="{hotlink(f)}" alt="{html.escape(note[:120])}"></div>'
                f'<figcaption class="meta"><b>{html.escape(note)}</b>'
                f'<span class="lic">{cred}</span><br>'
                f'<a href="{html.escape(page)}" target="_blank" rel="noopener">{html.escape(f)} ↗</a></figcaption></figure>')
        parts.append(f'</div><button class="btn r" data-t="{sid}" data-d="1" aria-label="next">›</button></div></section>')

    parts.append("""<footer>Sahara Elongated City · image review sheet · <a href="index.html">back to the city</a></footer>
<script>
document.querySelectorAll('.btn').forEach(b=>b.addEventListener('click',()=>{
  const t=document.getElementById('t-'+b.dataset.t);
  const w=t.querySelector('.slide').getBoundingClientRect().width+13;
  t.scrollBy({left:w*Number(b.dataset.d),behavior:'smooth'});
}));
</script></body></html>""")
    open(out, "w").write("\n".join(parts))
    total = sum(len(v) for v in by_id.values())
    print(f"wrote {out}: {len(by_id)} sections, {total} images")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
