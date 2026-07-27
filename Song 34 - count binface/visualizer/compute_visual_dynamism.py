#!/usr/bin/env python3
"""
compute_visual_dynamism.py — VIDEO-derived dynamism, from the pixels.

Implements the IMPLEMENTED ideas in visual-metrics-strategy.json (grid
differentiation, motion, colourfulness, global contrast) and writes a per-frame
signal to visual-dynamism.json.

The core is frame_metrics(rgb) — it scores ONE image and is reused per video
frame, so the exact same metric runs on a still later:
    python3 compute_visual_dynamism.py --image path/to/pic.jpg
    python3 compute_visual_dynamism.py            # process the 720 proxy

Nothing here touches the visualizer. This is exploration — the output is data.
numpy only (no opencv); frames are piped raw from ffmpeg.
"""
import subprocess, json, sys, os, io
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.join(HERE, "video-visualizer-720.mp4")
OUT   = os.path.join(HERE, "visual-dynamism.json")
FPS   = 30          # match the audio-feature timeline (30fps / 7719 frames)
SIZE  = 200         # decode frames at 200x200 → 10x10 grid = 20x20px cells
GRID  = 10

CHANNELS = ["grid_busyness", "grid_diff", "grid_palette",
            "colorfulness", "global_contrast", "motion"]

def frame_metrics(rgb, grid=GRID, prev_lum=None):
    """rgb: HxWx3 uint8/float. Returns (raw_metrics dict, luminance) — RAW, unnormalized."""
    x = rgb.astype(np.float32)
    R, G, B = x[..., 0], x[..., 1], x[..., 2]
    lum = 0.299 * R + 0.587 * G + 0.114 * B          # 0..255

    H, W = lum.shape
    ch, cw = H // grid, W // grid
    Hc, Wc = ch * grid, cw * grid                    # crop to a clean multiple
    # ---- GRID (idea 1): reshape into grid×grid cells ----
    Lc  = lum[:Hc, :Wc].reshape(grid, ch, grid, cw)
    cell_contrast = Lc.std(axis=(1, 3))              # within-cell luminance texture
    cell_mean_L   = Lc.mean(axis=(1, 3))             # per-cell brightness
    # per-cell colour spread (palette richness inside the cell)
    def cells(c): return c[:Hc, :Wc].reshape(grid, ch, grid, cw)
    Rc, Gc, Bc = cells(R), cells(G), cells(B)
    cell_color_spread = (Rc.std(axis=(1, 3)) + Gc.std(axis=(1, 3)) + Bc.std(axis=(1, 3))) / 3.0
    cell_mean_R, cell_mean_G, cell_mean_B = Rc.mean(axis=(1, 3)), Gc.mean(axis=(1, 3)), Bc.mean(axis=(1, 3))

    grid_busyness = float(cell_contrast.mean())      # avg within-cell texture ("items per cell")
    grid_palette  = float(cell_color_spread.mean())  # avg within-cell colour variety
    # DIFFERENTIATION: how different the cells are from EACH OTHER (the user's
    # "different palettes on different squares") — spread of cell means.
    grid_diff = float(cell_mean_L.std()
                      + (cell_mean_R.std() + cell_mean_G.std() + cell_mean_B.std()) / 3.0)

    # ---- colourfulness (idea 3): Hasler-Susstrunk ----
    rg = R - G
    yb = 0.5 * (R + G) - B
    colorfulness = float(np.sqrt(rg.std()**2 + yb.std()**2)
                         + 0.3 * np.sqrt(rg.mean()**2 + yb.mean()**2))

    # ---- global contrast (idea 4) ----
    global_contrast = float(lum.std())

    # ---- motion (idea 2): frame-to-frame luma diff ----
    motion = float(np.abs(lum - prev_lum).mean()) if prev_lum is not None else 0.0

    return {
        "grid_busyness": grid_busyness, "grid_diff": grid_diff, "grid_palette": grid_palette,
        "colorfulness": colorfulness, "global_contrast": global_contrast, "motion": motion,
    }, lum


def process_video(video=VIDEO, fps=FPS, size=SIZE):
    if not os.path.exists(video):
        sys.exit("missing video: " + video)
    cmd = ["ffmpeg", "-v", "error", "-i", video,
           "-vf", f"fps={fps},scale={size}:{size}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=10**8)
    frame_bytes = size * size * 3
    rows, prev = [], None
    n = 0
    while True:
        buf = proc.stdout.read(frame_bytes)
        if len(buf) < frame_bytes:
            break
        rgb = np.frombuffer(buf, np.uint8).reshape(size, size, 3)
        m, prev = frame_metrics(rgb, prev_lum=prev)
        rows.append([m[c] for c in CHANNELS])
        n += 1
        if n % 600 == 0:
            print(f"  {n} frames…", flush=True)
    proc.stdout.close(); proc.wait()
    raw = np.array(rows, dtype=np.float32)            # (frames, channels)

    # normalize each channel to 0..1 over the video's own 2nd–98th percentile
    lo = np.percentile(raw, 2, axis=0)
    hi = np.percentile(raw, 98, axis=0)
    span = np.maximum(hi - lo, 1e-6)
    norm = np.clip((raw - lo) / span, 0, 1)

    # provisional blend (weights live in the strategy file; re-weightable from `norm`)
    w = {"grid_busyness": .30, "grid_diff": .25, "motion": .25, "colorfulness": .20}
    dyn = np.zeros(len(raw), np.float32)
    for c, wt in w.items():
        dyn += wt * norm[:, CHANNELS.index(c)]
    dyn = np.clip(dyn, 0, 1)

    out = {
        "_doc": "Per-frame video dynamism. channels are 0..1 (normalized per-video, 2–98 pct). "
                "'dynamism' is a provisional blend — re-weight from the channels without re-processing. "
                "See visual-metrics-strategy.json. raw_stats let you re-normalize / compare across videos.",
        "source": os.path.basename(video), "fps": fps, "size": size, "grid": GRID,
        "frames": len(raw), "channels": CHANNELS,
        "raw_stats": {c: {"min": float(raw[:, i].min()), "max": float(raw[:, i].max()),
                          "mean": float(raw[:, i].mean()), "p2": float(lo[i]), "p98": float(hi[i])}
                      for i, c in enumerate(CHANNELS)},
        "weights_provisional": w,
        "data": [[round(float(v), 4) for v in row] for row in norm],
        "dynamism": [round(float(v), 4) for v in dyn],
    }
    with io.open(OUT, "w") as f:
        json.dump(out, f)
    return out


def process_image(path):
    # decode a single still to RGB via ffmpeg (any format), score it
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={SIZE}:{SIZE}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    buf = subprocess.run(cmd, capture_output=True).stdout
    rgb = np.frombuffer(buf[:SIZE*SIZE*3], np.uint8).reshape(SIZE, SIZE, 3)
    m, _ = frame_metrics(rgb)
    print(json.dumps({"image": os.path.basename(path), "raw_metrics": m}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--image":
        process_image(sys.argv[2])
    else:
        print("processing", os.path.basename(VIDEO), "…")
        o = process_video()
        print(f"wrote {os.path.basename(OUT)} — {o['frames']} frames, {len(o['channels'])} channels")
