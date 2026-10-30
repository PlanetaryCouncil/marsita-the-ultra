#!/usr/bin/env python3
"""
bake_features.py — stems in, the visualiser's deterministic feature track out.

Same payload as precompute_visualizer_features_voiceplus.py, but the stems are
found by NAME instead of hard-coded, so it works on any song:

    python3 bake_features.py "/path/to/STEMS" -o features.json

VOICE / CHOIR / RHYTHM / BASS / MUSIC are matched off the filename; anything
unrecognised falls into MUSIC. Prints the grouping so you can check it.
"""
import sys, os, json, glob, subprocess
import numpy as np

SR, FPS = 12_000, 30
HOP, WINDOW = SR // FPS, 1024
BAND_EDGES = np.array([25,70,140,280,560,1100,2200,3800,5900], dtype=np.float32)
AUDIO_EXT = (".mp3",".wav",".m4a",".flac",".aif",".aiff",".ogg")

def classify(name):
    n = os.path.basename(name).lower()
    if any(k in n for k in ("backing","background","choir","harmon")): return "CHOIR"
    if any(k in n for k in ("vocal","voice","vox","lead")):            return "VOICE"
    if any(k in n for k in ("drum","percussion","kick","snare","beat")):return "RHYTHM"
    if "bass" in n and "brass" not in n:                                return "BASS"
    return "MUSIC"

def decode_mono(path):
    r = subprocess.run(["ffmpeg","-v","error","-i",path,"-vn","-ac","1","-ar",str(SR),
                        "-f","f32le","pipe:1"], check=True, stdout=subprocess.PIPE)
    return np.frombuffer(r.stdout, dtype="<f4").copy()

def mix_group(paths):
    if not paths: return np.zeros(SR, dtype=np.float32)
    dec = [decode_mono(p) for p in paths]
    n = max(map(len, dec))
    mix = np.zeros(n, dtype=np.float32)
    for a in dec: mix[:len(a)] += a
    return mix / max(1, len(dec))

def frame_features(audio):
    fc = max(1, int(np.ceil(len(audio)/HOP)))
    padded = np.pad(audio, (0, max(0, (fc-1)*HOP + WINDOW - len(audio))))
    frames = np.lib.stride_tricks.as_strided(
        padded, shape=(fc, WINDOW),
        strides=(padded.strides[0]*HOP, padded.strides[0]), writeable=False)
    win = frames * np.hanning(WINDOW).astype(np.float32)
    rms = np.sqrt(np.mean(frames*frames, axis=1) + 1e-10)
    spec = np.abs(np.fft.rfft(win, axis=1)).astype(np.float32)
    freqs = np.fft.rfftfreq(WINDOW, 1/SR)
    bands = np.stack([spec[:, (freqs>=lo)&(freqs<hi)].mean(axis=1)
                      for lo,hi in zip(BAND_EDGES[:-1], BAND_EDGES[1:])], axis=1)
    rms = np.clip(rms / max(float(np.percentile(rms,98)),1e-6), 0, 1)
    bands = np.clip(bands / np.maximum(np.percentile(bands,98,axis=0),1e-6), 0, 1)
    prev = np.concatenate(([rms[0]], rms[:-1]))
    onset = np.clip((rms - prev*0.86)*4.5, 0, 1)
    env = np.empty_like(rms); env[0] = rms[0]
    for i in range(1, len(rms)):
        c = 0.48 if rms[i] > env[i-1] else 0.12
        env[i] = env[i-1] + (rms[i]-env[i-1])*c
    return np.column_stack((rms, onset, bands, env)).astype(np.float32)

def build_scene(f):
    voice,choir,rhythm,bass,music = (f[k] for k in ("VOICE","CHOIR","RHYTHM","BASS","MUSIC"))
    ve,ce,re_,be,me = (v[:,10] for v in (voice,choir,rhythm,bass,music))
    onset = np.maximum.reduce([voice[:,1],choir[:,1],rhythm[:,1],bass[:,1],music[:,1]])
    rhythm_high = rhythm[:,8:10].mean(axis=1); music_mid = music[:,4:8].mean(axis=1)
    music_high = music[:,8:10].mean(axis=1);   choir_high = choir[:,8:10].mean(axis=1)
    bass_low = bass[:,2:4].mean(axis=1)
    return np.column_stack((
        .30*re_ + .23*be + .27*rhythm[:,1] + .20*music_high,
        .34*bass_low + .28*re_ + .25*rhythm[:,1] + .13*me,
        .36*music_mid + .24*ce + .23*ve + .17*music[:,1],
        .42*rhythm_high + .31*music_high + .27*onset,
        np.maximum.reduce([np.sqrt(ve*ce),np.sqrt(ce*me),np.sqrt(me*re_),
                           np.sqrt(re_*be),np.sqrt(be*ve)]),
        np.maximum(onset, rhythm[:,1]*.72 + re_*.28),
        .55*music_high + .45*choir_high)).astype(np.float32)

def q(v): return np.rint(np.clip(v,0,1)*255).astype(np.uint8).tolist()

def main():
    a=[x for x in sys.argv[1:] if x!="-o"]
    out="features.json"
    if "-o" in sys.argv: out=sys.argv[sys.argv.index("-o")+1]; a=[x for x in a if x!=out]
    if not a: sys.exit(__doc__)
    files=[]
    for p in a:
        files += ([f for f in sorted(glob.glob(os.path.join(p,"*")))
                   if f.lower().endswith(AUDIO_EXT)] if os.path.isdir(p) else [p])
    if not files: sys.exit("no audio found")
    groups={k:[] for k in ("VOICE","CHOIR","RHYTHM","BASS","MUSIC")}
    for f in files: groups[classify(f)].append(f)
    for k,v in groups.items():
        print("  %-7s %s" % (k, ", ".join(os.path.basename(x) for x in v) or "— (silent)"))
    feats={k:frame_features(mix_group(v)) for k,v in groups.items()}
    n=max(len(v) for v in feats.values())
    for k,v in feats.items():
        if len(v)<n: feats[k]=np.pad(v,((0,n-len(v)),(0,0)))
    payload={"version":3,"fps":FPS,"scale":255,"duration":round(n/FPS,3),
      "layout":["energy","onset","band0","band1","band2","band3","band4","band5","band6","band7","envelope"],
      "sceneLayout":["rgbSpread","shapePulse","twist","turbulence","fusion","impact","air"],
      "scene":q(build_scene(feats)),
      "groups":{k:q(v) for k,v in feats.items()}}
    open(out,"w").write(json.dumps(payload,separators=(",",":")))
    print("\nwrote %s — %d frames (%.1fs), %.1f MB" % (out,n,n/FPS,os.path.getsize(out)/1e6))

if __name__=="__main__": main()
