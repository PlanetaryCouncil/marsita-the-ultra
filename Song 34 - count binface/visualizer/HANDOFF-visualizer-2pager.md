# VOTE FOR THE BIN — Visualizer Handoff (2-pager for the next AI)

*2026-07-17 · Marsita the Ultra — "Vote for the Bin (Count Binface vs Farage)" · Song 34*

## What this is

A serious audiovisual artwork, not a generic visualizer. A normal **720×720 square music video** sits untouched at the center of the screen; everything around it is a **sound-reactive dimensional field derived from that same video**. The artist records the page at **0.333333× playback speed** and speeds the capture 3× in edit — so ~40 rendered samples per real second become ~120 visual samples per final musical second. Everything must stay deterministic under seeking.

## The data (all in this folder — nothing external)

- **Master audio** = the sync authority: `FINAL AUDIO/Marsita the Ultra — Vote for the Bin (Count Binface vs Farage).mp3`. ⚠️ **Must be loaded via fetch→blob URL.** Direct-URL audio is unseekable under `python3 -m http.server` (no HTTP Range support; Chrome clamps every seek to 0).
- **Video**: `video-visualizer-720.mp4` (720×720@30, muted, looped, slaved to audio time).
- **Precomputed features**: `visualizer-features-voiceplus.json` — 30 fps uint8 rows per stem group `{VOICE, CHOIR, RHYTHM, BASS, MUSIC}`, layout `[energy, onset, band0..band7, envelope]`, plus a baked 7-channel `scene` choreography `[rgbSpread, shapePulse, twist, turbulence, fusion, impact, air]`. Interpolate rows at `t*fps`; **never run FFT at runtime**.
- **Lyrics**: `___lyricsJSON/07_binface_words_fine.json` — `[{t, w}]`; entries like `"[-ON]"` **append** their inner text to the previous subtitle (no space). The video also has **captions baked into its own frames** — never dim or cover the square.
- Stem identity colors (stable across all versions): VOICE white, CHOIR gold `#ffe56b`, RHYTHM red `#ff315f`, BASS violet `#735cff`, MUSIC cyan `#25dcff`. BPM 174.

## Version genealogy (all working, all kept — one idea per line)

1. `visualiser_ultra_10_chatgpt_04.html` — the reference: RGB-split shader extension + mosaic + physics. Rich but cluttered (~10 competing decorative systems). Audio seeking broken on range-less servers.
2. `visualiser_ultra_10_claude_enhance_01.html` — the refinement: decor opacity gated by baked energy (calm = genuinely dark), histograms centered on the five stem lanes, beat-quantized mosaic, collisions scheduled from the baked impact channel, all heavy per-frame costs removed (no shadowBlur, no allocations, ~40 trig calls/frame instead of ~4800).
3. `visualiser_ultra_10_claude_fresh_01.html` — the rebuild: exactly four systems (DOM video+lyrics · one mirror-tile RGB/mosaic shader field · one anatomy canvas · one pooled physics scene). The exterior is a mirror-tiled continuation of the live frame — seamless by construction.
4. User branch: `..._fresh_01_removed.html` → `..._removed_mirrorer.html` (adds four-way corner folds) → `..._mirrorer_fullbright.html` (newest: square at 100% brightness — edge-feather mask and lyric scrim removed).
5. `visualiser_ultra_10_claude_wild_01.html` — **CHRONO PORTAL**: the square is a hole in *time*. A ping-pong GPU feedback loop stamps the live frame at the square's footprint, then advects the past outward (zoom+rotation+decay). **R/G/B decay at different rates** — red = rhythm-strobed recent past, green = voice-trembled present, blue = bass-dragged deep past. Pointer = gravitational lens warping the field *and* the waveform lanes with the same math; clicks = shader shockwaves; each sung word is stamped once into the feedback so its ghost physically recedes into the portal. Smoke-tested clean; **not yet adversarially reviewed, and tuned too shy** (see below).

## Non-negotiables (every version must pass)

Square video: clear, normal, borderless, untrimmed, full brightness, never inherits field transforms. Real data only (histograms from baked bands — nothing fake). Seeking/scrubbing must never trigger explosions; reset all transient state on seek. Fixed pools, no allocations in the loop, ~40-sample frame gate, DPR capped. Master audio is the clock. Transport: scrub preview, ±5s, speed select defaulting to 0.333333, restart, fullscreen, hideable, draggable persisted timecode, `?start=` param, keyboard map (SPACE ←→ [ ] R L W V H F). Calm passages go dark; impacts earn their contrast. **Workflow rule: never edit a version in place — copy to a new descriptively-suffixed file first.**

## Where we're going

**Immediate:** `wild_02` — adversarial review of the feedback/shader code plus a tuning pass. The portal currently only opens on loud sections (calm decay floor ≈ 0.80 is too timid). The recursion trails should be *visibly devouring the present* most of the time; deepen chronochromatic separation so red/green/blue read as three distinct time-strata even at mid energy.

**The north star — more ultra-realistic AND more mindbending at once.** The paradox to chase: the impossible dimension should look *photographed*, not synthesized. Ideas for the next AI to push (in rough order of leverage):

1. **Real optics on impossible imagery.** Model the field's distortions on physical glass: barrel/pincushion lens warp, wavelength-dependent chromatic aberration at edges, thresholded bloom, subtle film grain and halation. If the portal looks like it was *shot through a real lens*, the brain accepts it as a place.
2. **Video-derived depth.** Run per-scene monocular depth estimation offline (bake to a small texture sequence, like the features JSON). Then the field gains true parallax: the past recedes with real 3D structure, the camera's bass-push becomes a genuine dolly, mosaic cells can occlude each other. This is the single biggest realism jump available.
3. **Scene-aware direction.** `music-video-square-images_scenes/` already contains shot boundaries. Bake scene IDs into the features and let each scene choose a field behavior (mirror fold / chrono recursion / mosaic shatter) so the artwork *edits itself* to the video, like a director rather than a filter.
4. **Space-time hybrid.** Fold wild's temporal recursion into mirrorer's spatial corner folds: a kaleidoscope where each mirrored wedge shows a different *moment*. One shader, both dimensions bent.
5. **Subject/background separation.** Offline person-segmentation matte (baked, low-res is fine): the background escapes into the dimension while Count Binface stays anchored — or occasionally *he* steps out of the square while the room stays put. Maximum mind-bend, still 100% video-derived.
6. **True 120 fps interior motion** needs an offline optical-flow interpolation pass on the video itself (RIFE/ffmpeg `minterpolate`); the browser can't invent frames. The procedural field already renders at full temporal density.

**Testing:** serve the folder over localhost (Range-capable server, or rely on the blob loading), play, seek hard, click the field, drag the timecode, watch the console. Note: hidden tabs suspend rAF — a frozen visual clock with advancing audio means the tab is occluded, not broken.

*Keep the square sacred. Keep the data real. Keep every version. Make the impossible look inevitable.*
