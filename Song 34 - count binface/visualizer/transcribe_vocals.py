#!/usr/bin/env python3
"""
transcribe_vocals.py — vocal stems in, word-level timings out.

Whisper listens to the singing and says WHERE each word is. The aligner then
matches your pasted lyrics against that transcript, so you nudge instead of
tapping 200 times.

    python3 transcribe_vocals.py "../stems/11 Backing_Vocals.mp3" "../stems/12 Vocals.mp3"
    python3 transcribe_vocals.py ../stems            # auto-picks vocal-ish stems
    python3 transcribe_vocals.py song.mp3 -o my_asr.json

Writes asr_words.json → load it in the aligner with "Load ASR".
Runs locally on the Mac's GPU. A 4-minute song takes about 20 seconds.
"""
import sys, os, json, glob, subprocess, tempfile

MODEL = "mlx-community/whisper-large-v3-turbo"
VOCALISH = ("vocal", "voice", "vox", "lead", "backing", "choir")

def pick(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            found = [f for f in sorted(glob.glob(os.path.join(p, "*")))
                     if os.path.splitext(f)[1].lower() in (".mp3",".wav",".m4a",".flac",".aiff",".aif")
                     and any(k in os.path.basename(f).lower() for k in VOCALISH)]
            if not found:
                sys.exit("no vocal-looking stems in %s — pass the files directly" % p)
            out += found
        else:
            out.append(p)
    return out

def mixdown(files, dst):
    """Sum the stems to one 16k mono wav. Quiet stems get levelled up so a
       buried backing vocal is still transcribed."""
    if len(files) == 1:
        cmd = ["ffmpeg","-v","error","-y","-i",files[0],
               "-af","dynaudnorm","-ar","16000","-ac","1",dst]
    else:
        ins = []
        for f in files: ins += ["-i", f]
        cmd = (["ffmpeg","-v","error","-y"] + ins +
               ["-filter_complex","[%s]amix=inputs=%d:normalize=0,dynaudnorm"
                % ("][".join("%d:a"%i for i in range(len(files))), len(files)),
                "-ar","16000","-ac","1",dst])
    subprocess.run(cmd, check=True)

def main():
    args = [a for a in sys.argv[1:] if a != "-o"]
    out = "asr_words.json"
    if "-o" in sys.argv:
        out = sys.argv[sys.argv.index("-o")+1]; args = [a for a in args if a != out]
    if not args:
        sys.exit(__doc__)
    files = pick(args)
    print("stems:"); [print("   ", os.path.basename(f)) for f in files]

    wav = os.path.join(tempfile.gettempdir(), "aligner_vox.wav")
    mixdown(files, wav)

    import mlx_whisper
    print("transcribing with %s …" % MODEL.split("/")[-1])
    r = mlx_whisper.transcribe(wav, path_or_hf_repo=MODEL,
                               word_timestamps=True, language="en", verbose=False)
    words = []
    for seg in r["segments"]:
        for w in seg.get("words", []):
            t = round(float(w["start"]), 3)
            words.append({"t": t, "e": round(float(w["end"]), 3), "w": w["word"].strip()})
    if not words:
        sys.exit("no words found — is there singing in these stems?")
    with open(out, "w") as f:
        json.dump({"source": [os.path.basename(x) for x in files],
                   "model": MODEL, "words": words}, f, indent=1)
    print("\nwrote %s — %d words, %.1fs .. %.1fs" % (out, len(words), words[0]["t"], words[-1]["t"]))
    print("preview:", " ".join(w["w"] for w in words[:18]))
    print("\nNow: open the aligner → Load ASR → pick this file → ⌁ Align.")

if __name__ == "__main__":
    main()
