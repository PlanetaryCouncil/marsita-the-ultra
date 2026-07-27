# VOTE FOR THE BIN — Complete Project Handoff

*Marsita the Ultra — "Vote for the Bin (Count Binface vs Farage)" · updated 2026-07-20*
*Read this top to bottom and you can continue the work in a fresh context with nothing lost.*

---

## 1 · What this is

A serious audiovisual artwork: a **720×720 music video** sits untouched and full-bright at the center of an exact **1920×1080 stage**; everything around it is a sound-reactive dimensional field derived from that same video and from pre-baked stem analysis. The current head version is a scene-directed, gravity-warped, achievement-gamified single HTML file. It is **live on the internet** at `planetarycouncil.org/binface`.

**The four commandments** (violate none):
1. **The square is sacred** — full brightness, normal orientation, never inherits field transforms, nothing covers it.
2. **The data is real** — all reactivity comes from baked stem features; no fake randomness, no runtime FFT.
3. **Every version is kept** — NEVER edit a version file in place; copy to a new suffixed file first, update its `<title>`.
4. **Everything is deterministic in song time** — seek anywhere, the artwork is identical; captures reproduce exactly. No wall-clock, no unseeded `Math.random()` in anything that renders.

## 2 · Geography

- **Song folder**: `/Users/m/Code/marsita-the-ultra/Song 34 - count binface/`
  - `FINAL AUDIO/Marsita the Ultra — Vote for the Bin (Count Binface vs Farage).mp3` — the master (em-dash in name!), sync authority
  - `___lyricsJSON/07_binface_words_fine.json` — word timings (user hand-tunes; contains `*` boom stars)
  - `STEMS/` — ten stem mp3s; `video.mp4` — 657MB source (never ship, never re-encode casually)
  - `frames_final*/` — AI-generated transition clips (Seedance/Kling/Firefly) for the edit
- **Working dir**: `…/Song 34 - count binface/visualizer/` — ALL current work happens here.
  - `___` prefix = anointed favorites. Current head: `___visualiser_ultra_10_claude_ultima_16.html`
  - Local copies: `video-visualizer-720.mp4` (68MB proxy), `visualizer-features-voiceplus.json`, `visualizer-scenes.json`
  - `precompute_visualizer_features_voiceplus.py` — adapted to live here (reads `../video.mp4` + `../STEMS`, writes locally)
  - `lyrics_render_alpha.html` — offline true-alpha PNG-sequence renderer of the lyric layer
  - `HANDOFF-visualizer-2pager.md` — the older, mid-project brief (superseded by this file)
- **Release**: `/Users/m/Code/planetarycouncil.org/binface/` (GitHub Pages repo → planetarycouncil.org/binface). Contains `index.html` (= ultima_13, paths patched, web-safe names: `binface-master.mp3`, `binface-words.json`, `album-cover.jpg`), the 68MB proxy, features + scenes JSON. **Already pushed and shared by the user.** Also `achievements.html` — the user's separately-developed achievements page (source of the engine now integrated into ultima_15+).

## 3 · Data contracts

- **`visualizer-features-voiceplus.json`** — 30fps uint8 rows per group {VOICE, CHOIR, RHYTHM, BASS, MUSIC}; layout `[energy, onset, band0..band7, envelope]`; plus baked 7-channel `scene` choreography `[rgbSpread, shapePulse, twist, turbulence, fusion, impact, air]`. Interpolate at `t*fps`. Regenerate by running the precompute script (also re-encodes the 720 proxy when `../video.mp4` changes — signature-cached).
- **`visualizer-scenes.json`** — 47 real cuts baked via ffmpeg scene-detection (threshold 0.25 + 0.5s debounce) from the CURRENT video edit. Plus two **authoring arrays** (one slot per scene, `null` = automatic): `"cast"` (`"MIRROR"|"PORTAL"|"DROSTE"`) overrides the director's language choice; `"lyricPos"` (`"top"|"mid"`, null = bottom) moves lyrics clear of text baked into the footage. ⚠️ Re-baking cuts invalidates authored arrays — re-map before re-baking.
- **Lyrics JSON** — `[{t, w}]`. `"[-IN]"` bracket entries append to the previous subtitle (no space). Leading `*` (e.g. `"*IN"`, `"*[-IN]"`) = **STAR BOOM**: word centered mid-square, detonation entrance, shockwave from the square's heart per starred entry (crescendo along an append chain). Master currently has the 5-star IN-chain at 223.3s.
- Stem colors (stable identities): VOICE `#ffffff` (legend "2 SRC"), CHOIR `#ffe56b`, RHYTHM `#ff315f`, BASS `#735cff`, MUSIC `#25dcff`. **BPM 174.** Song 257.3s / 7719 baked frames / 187 words.

## 4 · Version genealogy (all files exist; one line each)

**Ultra-10 lineage** (song folder + copies in visualizer/): `chatgpt_04` = pre-Claude reference. `claude_enhance_01` = refined reference. `claude_fresh_01` = 4-system rebuild, mirror-tile field → user branched `_removed`, `_removed_mirrorer` (+corner folds), `_mirrorer_fullbright` (mask+scrim removed). `claude_wild_01` = CHRONO PORTAL feedback dimension → `wild_02` = reviewed/fixed (GLSL pow-NaN, races) + portal opened. `ultra_11_codex_*` = parallel Codex line (not Claude's).

**Venus train lineage** (dormant but loved): `venus_train` = word-train spiral + user-editable scheduled achievements; `_menu` = 1× default + layer menu; `_dvd` = DVD-bounce train in exact 1920×1080 stage (closed-form fold math).

**Ultima lineage** (the main line, in visualizer/ with `___` prefix):
- `01` scene director (MIRROR/PORTAL/PURE per real cut, 0.7s crossfades, per-scene energy) + exact stage + layer menu
- `02` autopilot gravity (ghost-hand orbit, deterministic) · `03` square-echo beat rings + pow-NaN fix + calmer rotation
- `04` calm fullframe (user verdict: predictable = boring) · `05` HOUSE OF SQUARES: DROSTE infinite nested-square corridor replaces PURE (30/35/35)
- `06` bass pulse (~9% square throb, all rings follow) + 1.7× RGB split + liquid distortion · `07` lyric scrim removed
- `08` star-boom lyrics + `?words=` override · `09` per-append boom crescendo + **no-cache fetches** (critical) · `10` DIRECTOR'S CUT: authored cast/lyricPos + attention budget (background bows ~30% while words speak) + `?capture=1`
- `11` upright droste (no 90° ring rotation) · `12` wing lanes (11% steps centered on square's 45.5%, anatomy fades out across the middle) · `13` OCTOPUS GRAVITY (6 arms: ghost hand + five stem-driven orbits; lens warp in ALL languages + particles; **this is the released index.html**)
- `14` CLEAN STAGE: menu toggles for gravity circles + particle explosions; **H = help page**; **M = minimize all UI** for recording
- `15_achievements` — integrated the user's `achievements.html`: dual rails under the square (**TIME** % + **ACHV** pips, back-loaded 12-unlock schedule ending "100% · Full Impression · Certified Ultra"), toasts with easeOutBack + count, **honest relock on backward seek**, spring-mounted **UI physics** (toasts knock the dock, kicks thump the timer, square shoves neighbours — and the shader squares follow the shoved DOM square), Big Timer layer (default off), unlock celebrates in-field (square-echo ring + gravity blink)
- **`16` — CURRENT HEAD**: gravity circles default OFF (storage key bumped to `binface-ultima-layers-v2` to beat saved prefs), halos half-strength when re-enabled, burst rings dimmer.

## 5 · Head feature summary (ultima_16)

Exact 1920×1080 stage (STAGE_W/H consts; window scales/letterboxes; `?capture=1` for recording; **M** minimize UI; **H** help; full keyboard map on the help page). 1.00× default speed (0.05–2× menu). Blob-loaded audio+video, `{cache:'no-cache'}` on all assets. Scene director with three languages + authored overrides + scene HUD ("SC 22 — DROSTE", **A** toggles). Octopus gravity (autopilot; manual on mouse-move; capture mode locks to autopilot). Star-boom lyrics + scene lyric safe zones + attention budget. Five wing lanes + real mirrored 8-band histograms (full width, low bands central). Achievements + timer + UI physics (menu toggles, Lyrics-only / All-on presets, persisted). Layer menu is the master control of everything visible.

## 6 · Tools & recipes

- **`lyrics_render_alpha.html`** — renders ONLY the lyric layer, frame-by-frame, deterministic (seeded jitter, feature-driven glitch), to a **true-alpha PNG sequence** (File System Access folder pick; 30/60fps; test-frame + single-PNG buttons). For compositing lyrics separately: this beats chroma (the cyan fringe is ~86% green — no key color is safe on RGB-split typography).
- **Glow-on-black → transparency (the "Unmult" recipe)**: one ffmpeg pass — alpha = max(R,G,B) via `extractplanes` + `blend=all_mode=lighten` (never `geq`, too slow), `alphamerge`, `unpremultiply`, encode `prores_ks -profile:v 4444 -pix_fmt yuva444p10le` `.mov`. **MP4 cannot hold alpha.** Delivered: `frames_final_final/SCREENSHOT $K energy letters ALPHA.mov` (4K master, straight alpha), 720p sibling + tiny `.webm` (VP9 alpha) for web. Filenames may contain literal `$` — single-quote in shell.
- **Scene re-bake**: ffmpeg `select=gt(scene,0.25)` + metadata parse + 0.5s debounce → `visualizer-scenes.json` (preserve/remap authored arrays!).
- **Precompute**: `cd visualizer && python3 precompute_visualizer_features_voiceplus.py` — rebuilds 720 proxy (if `../video.mp4` changed) + features. ~2 min, five lines of output.

## 7 · Hard-won gotchas (each cost real debugging — do not relearn)

1. **`python3 -m http.server` has no HTTP Range support** → direct-URL `<audio>` is unseekable in Chrome (`seekable=[0,0]`, every seek snaps to 0). Fix: fetch → blob URL (all Claude-era files do this). Pre-Claude files still have the bug.
2. **Browser caching served stale JSON/media after user edits** (heuristic freshness on python-served files). Fix: `{cache:'no-cache'}` on every asset fetch (in since ultima_09). Symptom was "my starred words don't work".
3. **Hidden browser-pane suspends rAF** — visuals/timecode freeze while audio+video keep playing; feedback buffers starve. It's an environment artifact, NOT a page bug. Confirm with a rAF probe before hunting ghosts. Real fullscreen playback is unaffected.
4. **GLSL `pow(negative, 2.0)` is undefined** → NaN black discs on Metal/ANGLE. Write `k*k`. (Was in the shockwave ring; fixed in wild_02 and ultima_03+.)
5. **localStorage layer prefs override new code defaults** — changing a default requires bumping the storage key (`binface-ultima-layers-v2`) or migrating.
6. **When patching these HTML files with string replace**: CSS and JS have similar section banners — anchor precisely or your JS lands inside `<style>` (silently ignored, module half-broken). Also watch top-level evaluation order (TDZ): `updateTimeline`/`applyLayers` run during module eval via init calls; anything they reference must exist by then. Diagnose module-eval failures with a dynamic-import probe: copy module to a served `.mjs`, `import(...).catch(e=>e.stack)`.
7. **Versioning discipline is a user rule, not a preference** — "we always keep versions." Copy first, then edit. The user once gently corrected an in-place edit; don't repeat it.
8. **Timecode + layer prefs share localStorage keys per lineage** — pages on the same origin share them; ultima/venus have distinct keys.

## 8 · The artist (how to work with them)

Voice-typed messages — interpret generously, confirm by doing. Loves: **squares and nested geometry** ("I love the squares"), novelty over predictability ("predictable is bad, kind of boring"), gravity/warp effects ("energetic octopus"), full-bright video (no scrims, no masks), witty back-loaded achievements, hands-off deterministic capture at 1920×1080, owning the authoring surfaces (stars in lyrics JSON, cast/lyricPos in scenes JSON, achievement schedules). Dislikes: visual clutter ("waaay too busy"), circles/halos, anything covering the video or its baked captions. Wants small iterative "feel" changes over revolutions; grant yourself small polish freedoms but keep their engines intact when integrating. They share to `planetarycouncil.org`. They call versions by number ("make ultima_15"). Verify every change in the browser and show proof.

## 9 · Open threads (in rough priority)

1. **Refresh the release**: `/binface/index.html` is ultima_13; head is 16 (achievements + calm circles). Copy + re-patch paths (master/words/fallback names) + push on the user's word. Consider whether achievements belong in the public page (probably yes — they were built to incentivize completion).
2. **Binface segmentation matte** ("poor man's depth"): bake a person-matte offline, background escapes into the field while Binface stays anchored. Needs an offline segmentation pass — never started.
3. **Semantic cue words** (`visualizer-cues.json`: EVERYBODY→RGB expansion, BIN→implosion, etc.) and a **transition grammar** (cut type by musical context) — both from the Codex review, deliberately deferred.
4. **Venus train lineage** — dormant; the DVD-bounce + word-train + scheduled-achievements ideas live there if wanted again.
5. Cleanup candidates (ask first): `___lyricsJSON/07_binface_words_fine_STARTEST.json` (test file, 1 star), scratch `.mjs` files are in the session scratchpad (auto-cleaned).

## 10 · Quick start for the next session

```bash
# serve the song folder (assets resolve for visualizer/ pages via ../):
python3 -m http.server 8000 -d "/Users/m/Code/marsita-the-ultra/Song 34 - count binface"
# open:
http://localhost:8000/visualizer/___visualiser_ultra_10_claude_ultima_16.html
# recording mode: append  ?capture=1        start point: ?start=SECONDS
# lyric drafts:  ?words=../___lyricsJSON/your-draft.json
```
New version = `cp ___...ultima_16.html ___...ultima_17*.html`, retitle inside, edit the copy, `node --check` the extracted module, verify in a real browser, keep the old file byte-identical.

*Keep the square sacred. Keep the data real. Keep every version. Make the impossible look inevitable.* 🗑️👑
