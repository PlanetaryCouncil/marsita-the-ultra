#!/usr/bin/env python3
"""
update_tools.py — regenerate _tools.html from whatever is actually on disk.

Reads every .html here, pulls its <title>, groups files into lineages by their
trailing version number, and marks the highest number in each lineage as the
head. Run it after adding a version; nothing is hand-maintained.

    python3 update_tools.py
"""
import os, re, glob, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "_tools.html")

# Files whose story the filename cannot tell.
NOTES = {
    "___lyrics_aligner_v5_02.html": ("dead end", "energy auto-align — 10s errors, kept as archaeology"),
    "index.html": ("default", "opens when you browse the folder with no filename"),
}
HIDE = {"_tools.html"}

VER = re.compile(r"^(?P<stem>.+?)[_ ]v?(?P<maj>\d+)(?:[_.](?P<min>\d+))?$", re.I)

def title_of(path):
    try:
        head = open(path, encoding="utf-8", errors="replace").read(4000)
    except OSError:
        return ""
    m = re.search(r"<title>(.*?)</title>", head, re.S | re.I)
    if not m:
        return ""
    # titles are HTML — &rarr; etc. must come back as characters
    return re.sub(r"\s+", " ", html.unescape(m.group(1))).strip()

def lineage(name):
    base = os.path.splitext(name)[0]
    m = VER.match(base)
    if not m:
        return base, (0, 0), "—"
    maj, mn = m.group("maj"), m.group("min")
    # keep the written form: v5_08 reads 5.08, not 5.8
    label = maj if mn is None else "%s.%s" % (maj, mn)
    return m.group("stem"), (int(maj), int(mn or 0)), label

def collect():
    groups = {}
    for p in sorted(glob.glob(os.path.join(HERE, "*.html"))):
        n = os.path.basename(p)
        if n in HIDE:
            continue
        stem, ver, label = lineage(n)
        groups.setdefault(stem, []).append(
            {"file": n, "ver": ver, "label": label, "title": title_of(p),
             "mtime": os.path.getmtime(p)})
    for g in groups.values():
        g.sort(key=lambda x: (x["ver"], x["mtime"]), reverse=True)
    return groups

def bucket(stem):
    s = stem.lower()
    if "aligner" in s:                    return "aligner"
    if "visualizer" in s or "visualiser" in s or stem == "index": return "artwork"
    return "other"

def desc(e):
    tag, note = NOTES.get(e["file"], ("", ""))
    d = note or e["title"]
    if not note and "—" in d:
        d = d.split("—", 1)[1].strip()
    return d or e["file"]

def main():
    groups = collect()
    flat = [e for g in groups.values() for e in g]
    flat.sort(key=lambda e: e["mtime"], reverse=True)

    # The hero is the CURRENT TOOL, not whatever file was touched last — a stray
    # mtime must never bury the thing he is actually working in. Highest version
    # of the newest aligner lineage wins; recency only breaks ties.
    al = sorted([k for k in groups if bucket(k) == "aligner"],
                key=lambda k: (groups[k][0]["ver"], groups[k][0]["mtime"]), reverse=True)
    now = groups[al[0]][0] if al else flat[0]
    recent = [e for e in flat if e["file"] != now["file"]][:4]

    def card(e):
        return ('<a class="now" href="%s"><small>Open the latest</small>'
                '<b>%s</b><em>v%s · %s</em></a>'
                % (html.escape(e["file"]), html.escape(e["title"].split("—")[0].strip() or e["file"]),
                   html.escape(e["label"]), html.escape(desc(e))))

    def line(e):
        return ('<a class="row" href="%s"><b>%s</b><span>%s</span>'
                '<span class="when">%s</span></a>'
                % (html.escape(e["file"]),
                   html.escape(e["title"].split("—")[0].strip()[:26] or e["file"]),
                   html.escape(desc(e)), ago(e["mtime"])))

    body = [card(now)]
    if recent:
        body.append('<h2>Also recent</h2>')
        body += [line(e) for e in recent]

    # the archive, one fold, nothing shouting
    arch = ['<details class="arch"><summary>Everything else — %d files, %d lineages</summary>'
            % (len(flat) - 1 - len(recent), len(groups))]
    shown = {now["file"]} | {e["file"] for e in recent}
    for key in ("aligner", "artwork", "other"):
        keys = sorted([k for k in groups if bucket(k) == key],
                      key=lambda k: groups[k][0]["mtime"], reverse=True)
        if not keys:
            continue
        arch.append('<h3>%s</h3>' % {"aligner": "Lyrics aligner",
                                     "artwork": "The artwork",
                                     "other": "Everything else"}[key])
        for k in keys:
            g = [e for e in groups[k] if e["file"] not in shown]
            if not g:
                continue
            arch.append('<div class="lin">%s</div>' % html.escape(k))
            arch += [line(e) for e in g]
    arch.append('</details>')
    body += arch

    # say out loud what is already loaded, so nothing looks like a chore
    sess = '<div class="sess">No song staged yet</div>'
    try:
        import json
        m = json.load(open(os.path.join(HERE, "_session", "session.json"), encoding="utf-8"))
        n = len(json.load(open(os.path.join(HERE, "_session", m["asr"]), encoding="utf-8"))["words"]) \
            if m.get("asr") else 0
        sess = ('<div class="sess"><b>Loaded and ready:</b> %s'
                '<span>mix + vocals staged · %d words already transcribed · '
                'the aligner opens with all of it in place</span></div>'
                % (html.escape(m["name"]), n))
    except Exception:
        pass

    doc = (TPL.replace("{{SESSION}}", sess)
              .replace("{{BODY}}", "\n".join(body))
              .replace("{{STAMP}}", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
              .replace("{{COUNT}}", "%d files" % len(flat)))
    open(OUT, "w", encoding="utf-8").write(doc)
    print("wrote _tools.html — latest is %s" % now["file"])

def ago(t):
    d = datetime.datetime.now() - datetime.datetime.fromtimestamp(t)
    m = int(d.total_seconds() // 60)
    if m < 1:   return "just now"
    if m < 60:  return "%dm ago" % m
    if m < 1440:return "%dh ago" % (m // 60)
    return "%dd ago" % (m // 1440)

TPL = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tools — Marsita the Ultra</title>
<style>
:root{--void:#010207;--pink:#ff2bd6;--cyan:#25dcff;--gold:#ffe56b;--acid:#63ff9d}
*{box-sizing:border-box;margin:0}
body{background:var(--void);color:#e8ecf7;font:500 13px/1.6 ui-monospace,Menlo,monospace;padding:40px 22px 90px}
main{max-width:620px;margin:0 auto}
a.now{display:block;text-decoration:none;border:1px solid var(--acid);background:rgba(99,255,157,.09);
  padding:26px 26px 24px;margin-bottom:8px}
a.now:hover{background:rgba(99,255,157,.16)}
a.now small{display:block;font-size:9px;letter-spacing:.3em;text-transform:uppercase;color:var(--acid);margin-bottom:12px}
a.now b{display:block;font:1000 clamp(26px,6.4vw,40px)/1 "Arial Black",Impact,sans-serif;
  text-transform:uppercase;letter-spacing:-.03em;color:#fff;text-shadow:-3px 0 var(--pink),3px 0 var(--cyan)}
a.now em{display:block;font-style:normal;color:rgba(255,255,255,.66);font-size:12px;margin-top:12px}
h2{font:700 9px/1 ui-monospace,monospace;letter-spacing:.3em;text-transform:uppercase;color:var(--gold);
   margin:34px 0 8px}
a.row{display:flex;gap:11px;align-items:baseline;text-decoration:none;color:#e8ecf7;
  padding:8px 11px;border:1px solid rgba(255,255,255,.13);margin-bottom:4px}
a.row:hover{border-color:var(--acid);color:var(--acid)}
a.row b{font-weight:700;font-size:12px;white-space:nowrap}
a.row span{opacity:.55;font-size:11px;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
a.row .when{margin-left:auto;opacity:.3;font-size:10px;white-space:nowrap}
details.arch{margin-top:42px;border-top:1px solid rgba(255,255,255,.12);padding-top:14px}
details.arch summary{cursor:pointer;color:rgba(255,255,255,.3);font-size:11px;list-style:none;padding:4px 0}
details.arch summary::-webkit-details-marker{display:none}
details.arch summary:before{content:"▸ "}
details.arch[open] summary:before{content:"▾ "}
details.arch[open] summary{color:var(--cyan)}
h3{font:700 9px/1 ui-monospace,monospace;letter-spacing:.26em;text-transform:uppercase;
   color:rgba(255,255,255,.34);margin:26px 0 8px}
.lin{font-size:9px;letter-spacing:.12em;color:rgba(255,255,255,.22);margin:12px 0 4px;word-break:break-all}
p.note{color:rgba(255,255,255,.42);font-size:11px;margin:12px 0 0;line-height:1.9}
.sess{margin:30px 0 0;padding:14px 16px;border:1px solid rgba(37,220,255,.35);background:rgba(37,220,255,.06);font-size:12px}
.sess b{color:var(--cyan);font-weight:700}
.sess span{display:block;color:rgba(255,255,255,.55);font-size:11px;margin-top:5px}
code{color:var(--gold)}
footer{margin-top:16px;color:rgba(255,255,255,.24);font-size:10px}
</style>
<main>
{{BODY}}
{{SESSION}}
<details class="arch"><summary>How this got here (nothing for you to run)</summary>
<p class="note">Claude runs these when the song changes — they are already done for the song above.<br>
<code>transcribe_vocals.py STEMS -o asr_words.json</code> — stems in, word timings out<br>
<code>stage_session.py MIX VOCALS ASR</code> — park a song so browser reloads are free<br>
<code>update_tools.py</code> — rebuild this page</p></details>
<footer>{{COUNT}} · generated {{STAMP}} · newest first, always</footer>
</main>
"""

if __name__ == "__main__":
    main()
