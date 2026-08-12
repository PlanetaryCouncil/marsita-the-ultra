# Sound System promo site

Single-file promo page for **TRUTH NOT HATE (the only good system is the sound system)** —
same recipe as [binface.planetarycouncil.org](https://binface.planetarycouncil.org)
([PlanetaryCouncil/binface](https://github.com/PlanetaryCouncil/binface)).

## What's here

- `index.html` — the whole site. No build step, no dependencies. Edit + upload.
- `art/art01.jpg … art13.jpg` — web-sized thumbnails of the 13 cover candidates
  (full-size PNGs are loaded from this repo via raw.githubusercontent.com when zoomed).
- `preview.jpg` — 1200×630 share card for X / WhatsApp / Discord embeds.

## To deploy (binface-style)

1. Create a repo (e.g. `PlanetaryCouncil/soundsystem`), copy this folder's contents to its root.
2. Add a `CNAME` file containing `soundsystem.planetarycouncil.org` and enable GitHub Pages.
3. Point the DNS CNAME record at `planetarycouncil.github.io`.
4. If the domain differs, update `SITE_URL` and the `og:` / `twitter:` meta URLs in `index.html`.

## Before/after launch checklist

- **Telegram handle** in the "Join the party" row is a guess (`t.me/MarsitaTheUltra`) — confirm or fix.
- When the **WAV + stems** land in this folder, swap the two "soon" download tiles
  for direct raw.githubusercontent.com file URLs (pattern shown in the MP3 tile).
- Artwork votes arrive via Telegram share / X posts / email — no backend, nothing stored.
