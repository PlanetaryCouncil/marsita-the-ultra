#!/usr/bin/env python3
"""
stage_session.py — park the current song next to the aligner so a browser
reload costs nothing. Copies (and mp3-encodes where needed) into _session/
and writes a manifest the aligner auto-loads on boot.

    python3 stage_session.py MIX VOCALS [ASR.json]

    python3 stage_session.py \
      "../../Song 27 - Global Pause/versions various strange WIP finalizing/Marsita the Ultra - Global Peace (new hope vibing flowing mix).wav" \
      "../../Song 27 - Global Pause/STEMS (new hope)/15 Vocals.mp3" \
      "../../Song 27 - Global Pause/asr_words.json"

Throwaway working copies — delete _session/ whenever.
"""
import sys, os, json, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SESS = os.path.join(HERE, "_session")

def bring(src, dstname):
    """mp3 stays as-is; anything else gets encoded so the browser decodes fast."""
    dst = os.path.join(SESS, dstname + ".mp3")
    if os.path.splitext(src)[1].lower() == ".mp3":
        shutil.copyfile(src, dst)
    else:
        subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-b:a","192k",dst], check=True)
    return os.path.basename(dst), os.path.getsize(dst)

def main():
    a = sys.argv[1:]
    if len(a) < 2: sys.exit(__doc__)
    mix, vox = a[0], a[1]
    asr = a[2] if len(a) > 2 else None
    for p in [mix, vox] + ([asr] if asr else []):
        if not os.path.exists(p): sys.exit("missing: " + p)

    os.makedirs(SESS, exist_ok=True)
    man = {"name": os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(mix))))}
    for label, src in (("mix", mix), ("vocals", vox)):
        n, sz = bring(src, label)
        man[label] = n
        print("  %-7s %-22s %5.1f MB" % (label, n, sz/1e6))
    if asr:
        shutil.copyfile(asr, os.path.join(SESS, "asr_words.json"))
        man["asr"] = "asr_words.json"
        n = len(json.load(open(asr))["words"])
        print("  %-7s %-22s %5d words" % ("asr", "asr_words.json", n))
    man["sources"] = {"mix": os.path.abspath(mix), "vocals": os.path.abspath(vox),
                      "asr": os.path.abspath(asr) if asr else None}
    with open(os.path.join(SESS, "session.json"), "w") as f:
        json.dump(man, f, indent=1)
    print("\nstaged '%s' — the aligner now reloads with everything in place." % man["name"])

if __name__ == "__main__":
    main()
