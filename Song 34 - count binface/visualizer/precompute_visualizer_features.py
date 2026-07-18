#!/usr/bin/env python3
"""Precompute lightweight, frame-aligned stem features for visualiser_ultra.html."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
OUTPUT = ROOT / "visualizer-features.json"
VIDEO_SOURCE = PROJECT_ROOT / "video.mp4"
VIDEO_OUTPUT = ROOT / "video-visualizer-720.mp4"
VIDEO_META = ROOT / "video-visualizer-720.source.json"
SAMPLE_RATE = 12_000
FPS = 30
HOP = SAMPLE_RATE // FPS
WINDOW = 1024
GROUPS = {
    "VOICE": ["STEMS/12 Vocals.mp3"],
    "CHOIR": ["STEMS/11 Backing_Vocals.mp3", "STEMS/13 my own background vocal.mp3"],
    "RHYTHM": ["STEMS/10 Drums.mp3", "STEMS/6 Percussion.mp3"],
    "BASS": ["STEMS/9 Bass.mp3"],
    "MUSIC": ["STEMS/4 Synth.mp3", "STEMS/8 Guitar.mp3", "STEMS/1 Woodwinds.mp3", "STEMS/3 FX.mp3"],
}
BAND_EDGES = np.array([25, 70, 140, 280, 560, 1100, 2200, 3800, 5900], dtype=np.float32)


def decode_mono(path: Path) -> np.ndarray:
    command = [
        "ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1",
        "-ar", str(SAMPLE_RATE), "-f", "f32le", "pipe:1",
    ]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE)
    return np.frombuffer(result.stdout, dtype="<f4").copy()


def mix_group(paths: list[str]) -> np.ndarray:
    decoded = [decode_mono(PROJECT_ROOT / path) for path in paths]
    length = max(map(len, decoded))
    mix = np.zeros(length, dtype=np.float32)
    for audio in decoded:
        mix[: len(audio)] += audio
    return mix / max(1, len(decoded))


def frame_features(audio: np.ndarray) -> np.ndarray:
    frame_count = max(1, int(np.ceil(len(audio) / HOP)))
    padded_length = (frame_count - 1) * HOP + WINDOW
    padded = np.pad(audio, (0, max(0, padded_length - len(audio))))
    frames = np.lib.stride_tricks.as_strided(
        padded,
        shape=(frame_count, WINDOW),
        strides=(padded.strides[0] * HOP, padded.strides[0]),
        writeable=False,
    )
    windowed = frames * np.hanning(WINDOW).astype(np.float32)
    rms = np.sqrt(np.mean(frames * frames, axis=1) + 1e-10)
    spectrum = np.abs(np.fft.rfft(windowed, axis=1)).astype(np.float32)
    frequencies = np.fft.rfftfreq(WINDOW, 1 / SAMPLE_RATE)
    bands = np.stack([
        spectrum[:, (frequencies >= low) & (frequencies < high)].mean(axis=1)
        for low, high in zip(BAND_EDGES[:-1], BAND_EDGES[1:])
    ], axis=1)

    rms_scale = max(float(np.percentile(rms, 98)), 1e-6)
    rms = np.clip(rms / rms_scale, 0, 1)
    band_scale = np.maximum(np.percentile(bands, 98, axis=0), 1e-6)
    bands = np.clip(bands / band_scale, 0, 1)
    previous = np.concatenate(([rms[0]], rms[:-1]))
    onset = np.clip((rms - previous * 0.86) * 4.5, 0, 1)
    envelope = np.empty_like(rms)
    envelope[0] = rms[0]
    for index in range(1, len(rms)):
        coefficient = 0.48 if rms[index] > envelope[index - 1] else 0.12
        envelope[index] = envelope[index - 1] + (rms[index] - envelope[index - 1]) * coefficient
    return np.column_stack((rms, onset, bands, envelope)).astype(np.float32)


def build_scene_features(features: dict[str, np.ndarray]) -> np.ndarray:
    """Bake the cross-stem visual choreography so seeking is deterministic."""
    voice, choir = features["VOICE"], features["CHOIR"]
    rhythm, bass, music = features["RHYTHM"], features["BASS"], features["MUSIC"]
    ve, ce, re, be, me = (values[:, 10] for values in (voice, choir, rhythm, bass, music))
    onset = np.maximum.reduce([voice[:, 1], choir[:, 1], rhythm[:, 1], bass[:, 1], music[:, 1]])
    rhythm_high = rhythm[:, 8:10].mean(axis=1)
    music_mid = music[:, 4:8].mean(axis=1)
    music_high = music[:, 8:10].mean(axis=1)
    choir_high = choir[:, 8:10].mean(axis=1)
    bass_low = bass[:, 2:4].mean(axis=1)
    rgb_spread = .30 * re + .23 * be + .27 * rhythm[:, 1] + .20 * music_high
    shape_pulse = .34 * bass_low + .28 * re + .25 * rhythm[:, 1] + .13 * me
    twist = .36 * music_mid + .24 * ce + .23 * ve + .17 * music[:, 1]
    turbulence = .42 * rhythm_high + .31 * music_high + .27 * onset
    fusion = np.maximum.reduce([
        np.sqrt(ve * ce), np.sqrt(ce * me), np.sqrt(me * re),
        np.sqrt(re * be), np.sqrt(be * ve),
    ])
    impact = np.maximum(onset, rhythm[:, 1] * .72 + re * .28)
    air = .55 * music_high + .45 * choir_high
    return np.column_stack((rgb_spread, shape_pulse, twist, turbulence, fusion, impact, air)).astype(np.float32)


def quantized_rows(values: np.ndarray) -> list[list[int]]:
    return np.rint(np.clip(values, 0, 1) * 255).astype(np.uint8).tolist()


def source_signature(path: Path) -> dict[str, int]:
    stat = path.stat()
    return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def build_visualizer_video() -> None:
    signature = source_signature(VIDEO_SOURCE)
    if VIDEO_OUTPUT.exists() and VIDEO_META.exists():
        try:
            if json.loads(VIDEO_META.read_text(encoding="utf-8")) == signature:
                print(f"Using current {VIDEO_OUTPUT.name}")
                return
        except (OSError, ValueError):
            pass
    print(f"Building {VIDEO_OUTPUT.name}")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(VIDEO_SOURCE), "-an",
        "-vf", "fps=30,scale=720:720:flags=lanczos", "-c:v", "libx264", "-preset", "fast",
        "-crf", "25", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(VIDEO_OUTPUT),
    ], check=True)
    VIDEO_META.write_text(json.dumps(signature, separators=(",", ":")), encoding="utf-8")


def main() -> None:
    build_visualizer_video()
    features: dict[str, np.ndarray] = {}
    for name, paths in GROUPS.items():
        print(f"Analysing {name}: {len(paths)} source(s)")
        features[name] = frame_features(mix_group(paths))

    frame_count = max(len(values) for values in features.values())
    for name, values in features.items():
        if len(values) < frame_count:
            features[name] = np.pad(values, ((0, frame_count - len(values)), (0, 0)))

    scene = build_scene_features(features)
    payload = {
        "version": 3,
        "fps": FPS,
        "scale": 255,
        "duration": round(frame_count / FPS, 3),
        "layout": ["energy", "onset", "band0", "band1", "band2", "band3", "band4", "band5", "band6", "band7", "envelope"],
        "sceneLayout": ["rgbSpread", "shapePulse", "twist", "turbulence", "fusion", "impact", "air"],
        "scene": quantized_rows(scene),
        "groups": {name: quantized_rows(values) for name, values in features.items()},
    }
    OUTPUT.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUTPUT.name}: {OUTPUT.stat().st_size / 1_000_000:.2f} MB, {frame_count} frames")


if __name__ == "__main__":
    main()
