# VOTE FOR THE BIN — HANDOFF v2

*Updated 2026-08-04. Supersedes HANDOFF-binface-complete.md (which stops at ultima_16 and is kept as archaeology).*
*Read this and you can continue in a fresh session with nothing lost.*

---

## 0 · IT SHIPPED

The music video is **published on YouTube**. The playable artwork is **live at planetarycouncil.org/binface**.
Everything below is the machine that made it, and the tooling built after.

**Pending (needs the artist):**
- `cd /Users/m/Code/planetarycouncil.org && git push` — several commits are staged and unpushed
  (public play-only face, visitor flow, promo one-pager, WRAPPING UP 02 release).
- `binface/promo.html` still contains the literal `YOUTUBE_URL_HERE` — paste the real link before pushing.

---

## 1 · THE FOUR COMMANDMENTS (violate none)

1. **The square is sacred** — full brightness, nothing covers the footage.
   *Exception, chosen deliberately by the artist:* the MINDFUCK field feathers into the square's outer
   band (`ringIn = smoothstep(.86,1.0,boxR)`). That is the look they picked. Not a bug.
2. **The data is real** — reactions come from pre-baked stem analysis and pre-baked pixel analysis.
   No runtime FFT.
3. **Every version is kept** — NEVER edit a version in place. Copy → rename → edit the copy.
   Append-only numbers inside a branch; a new branch name when a lineage piles up.
   Names describe the feature (`GRADIENT_WINGS`, `wrapping_up`), not just a number.
4. **Deterministic in song time** — seek anywhere, identical artwork; captures reproduce.
   *One deliberate exception:* the field profile (band widths, opacities, angle) rolls **unseeded on every
   page load**. The artist ruled this a FEATURE — "first render is always the best", every visitor gets
   their own performance. Do not "fix" it.

---

## 2 · LINEAGE MAP (109 html files; heads only)

| branch | head | what it is |
|---|---|---|
| **MINDFUCK** | `___visualizer_ULTRA_PURE_VIDEO_MINDFUCK_08.html` | **the artist's chosen look.** Codex mirror mosaic + PURE echo, metric roulette, PLAY/RECORD home, countdown capture, 0.5× record. Both orientations via `?v=1`. |
| burpee_sync | `___visualizer_burpee_sync_04.html` | upload your own video into the artwork; two-track lyric aligner; crop → Horizontal/Vertical |
| reframe_studio | `___reframe_studio_04.html` | **standalone**: horizontal → vertical, exports real MP4 from the browser |
| lyrics_aligner | `___lyrics_aligner_v5_01.html` | **standalone**: paste Suno text + stems, tap to the vocals waveform, E splits words |
| wrapping_up | `___visualizer_wrapping_up_02.html` | field burns at frame edges, decays inward (per-axis) |
| GRADIENT_WINGS | `___visualizer_GRADIENT_WINGS_01.html` | inverse: bright at the square, dim at the edges |
| double_wide | `___visualizer_double_wide_02.html` | mirror-extend the square to fill full HD |
| PURE | `___visualizer_ultra_PURE_13.html` | minimal clean square, slowmo-safe |
| ultima | `___visualiser_ultra_10_claude_ultima_21.html` | the original main line (achievements removed at 19) |
| amoeba | `___visualizer_ultra_amoeba_03.html` | organic blob field (dormant, menu toggle) |
| vertical | `___visualizer_vertical_01.html` | superseded by MINDFUCK_07+ `?v=1` |
| (older) | `word_timeline_aligner_v4_4.html` | the artist's original aligner — preset list stops at 07 |

**The menu is the laboratory.** Every experiment ships as a checkbox inside the current head:
field, metric drive, metric roulette, lyric stem reaction, lyric per-letter, amoeba, square pulse,
achievements, waves, histograms, particles, morph. Versions are history; toggles are the lab.

---

## 3 · DATA CONTRACTS

- **`../___lyricsJSON/12_binface_words_pure_achievements.json`** — current lyrics. `[{t,w}]`.
  - `[X]` = **append/join** (no space): `TE` + `[CHNO]` + `[LOGY]` → TECHNOLOGY
  - `-` inside a word = prolongation, plain typography (`ON-ON-ON`), NOT a token
  - `*` prefix = **star boom** (centred, detonation, shockwave)
  - `@` prefix = **sudden achievement**, not a word: `@🌗 Halfway · No Refunds`
- **`visualizer-features-voiceplus.json`** — 30fps, 7719 frames, per stem `[energy,onset,band0..7,envelope]`.
  Regenerate: `python3 precompute_visualizer_features_voiceplus.py` (also rebuilds the 720 proxy).
- **`visualizer-scenes.json`** — **48 cuts** for the current edit + `cast`/`lyricPos` authoring arrays (all null).
- **`visual-dynamism.json`** — per-frame picture metrics (grid busyness/diff/palette, colourfulness, contrast, motion).
  Regenerate: `python3 compute_visual_dynamism.py` · single image: `--image path.jpg`
  Ideas registry: `visual-metrics-strategy.json`
- **`../video.mp4`** — 1080×1080 60fps master (690MB). `video-visualizer-720.mp4` = proxy.
- Stem colours: VOICE `#ffffff` · CHOIR `#ffe56b` · RHYTHM `#ff315f` · BASS `#735cff` · MUSIC `#25dcff`. **BPM 174.**

---

## 4 · RECORDING

`…MINDFUCK_08.html` → **⏺ Rec 1920×1080** or **⏺ Rec 1080×1920** → cursor hides, 3·2·1 slate, plays itself at **0.5×**.
Capture 60fps → **conform 2×** in the editor. Machine needs only 30fps sustained.
All wall-clock CSS animations scale with `--slow`, so the conform is frame-identical to real time.
`?auto=1` = record mode (PRESS SPACE gate on gesture-free loads). `M` clears all UI. `H`/Esc close panels.

---

## 5 · GOTCHAS (each cost real debugging)

1. **`python3 -m http.server` has no Range support** → direct-URL `<audio>` is unseekable. All modern files fetch→blob.
2. **Browser caching served stale JSON** → every asset fetch uses `{cache:'no-cache'}`.
3. **Hidden browser tabs suspend rAF/rVFC** — visuals freeze while audio plays. Environment artifact, not a bug.
   *But it is real for exports*: `reframe_studio` drives its canvas from `setInterval` and **verifies frames drawn**,
   refusing to call a starved capture a success.
4. **GLSL `pow(negative,2.0)` is undefined** → write `k*k`.
5. **localStorage layer prefs override new defaults** → bump `LAYERS_KEY` when changing a default.
6. **Anchor patches precisely** — CSS and JS have similar banners; check `count==1` before replacing.
   Watch for raw `&` vs `&amp;` in HTML strings, and **backticks inside GLSL comments terminate the template literal**.
7. **ScreenFlow 10.5.1 cannot import anything on macOS 14.8.2** — codec/container/brand/atom-order all ruled out;
   it is the app. Not worth re-debugging. Use Resolve or a newer ScreenFlow.
8. **The field shader divides by `uHalf`** (scalar = square only). `burpee_sync_03+` and `double_wide` use a
   per-axis `uHalf2` vec2 so the field can wrap rectangles.

---

## 6 · WORKING WITH THE ARTIST

Voice-typed, generous interpreter, moves fast. **The field language is the artwork** — RGB split, mirror,
morph, depth. Waveforms/histograms/particles read as clutter. Loves: novelty over predictability, the square
full-bright, achievements, wit. Verify in the browser and show proof; the composition judgment is theirs
(the preview pane is half-blind — say so honestly rather than guessing).
They are an experienced web dev: skip fundamentals, lead with the non-obvious.

**Keep the square sacred. Keep the data real. Keep every version. First render is always the best.** 🗑️👑
