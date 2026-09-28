# Marsita the Ultra — the release site

One site for every song. Each song gets its own link (`/soundsystem/`,
`/greenland/` …) with its own colours and share preview; a switcher in
the top right jumps between songs; the bottom of every page is the same
funnel: **email signup → follow → more songs**.

Everything is driven by one file: **`catalog.js`**.

```
site/
  catalog.js            ← edit this: site settings + every song
  build.js              makes the per-song HTML (share previews) from catalog.js
  tools/art.py          makes cover.jpg + preview.jpg from a cover image
  assets/site.js        draws the page (switcher, blocks, signup, vote...)
  assets/site.css       the look
  songs/<slug>/         cover.jpg, preview.jpg, extra art
  index.html, <slug>/index.html, 404.html, sitemap.xml   ← generated
```

## Add a song

```sh
python3 site/tools/art.py next-song "Song 36 - next song/cover.png"   # needs: pip install pillow
# copy the TEMPLATE at the bottom of catalog.js into SONGS, fill it in
node site/build.js
git add site && git commit -m "Add next song" && git push
```

`build.js` checks the catalog (missing covers, duplicate slugs, bad featured
song) and refuses to build if something is broken.

**Launch week:** use the `status: 'soon'` template (countdown + signup at the
top), set `SITE.featured` to its slug so the home page promotes it, then flip
it to `status: 'new'` with the real player/links on release day.

## Change something

- **Links, text, downloads** — edit `catalog.js`, push. That's it.
- **Title, share text, featured song** — edit `catalog.js`, run `node site/build.js`, push.
- **Page building blocks** — listed at the top of the `SONGS` section in `catalog.js`
  (audio, youtube, quote, listen, downloads, card, specs, vote, countdown, signup, cta).

## Publish (one-time setup)

The workflow in `.github/workflows/site.yml` publishes `site/` to GitHub Pages
on every push to `main` that touches it. It checks out only `site/`, so the
6 GB of audio in this repo doesn't matter.

1. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Same page, **Custom domain**: `marsita.planetarycouncil.org` (or whatever you pick —
   then also change `SITE.url` in `catalog.js`).
3. DNS: `CNAME marsita → planetarycouncil.github.io`.
4. Push to `main` (or run the workflow by hand from the Actions tab).

## Before launch

- [ ] **Telegram link** in `SITE.socials` is a guess (`t.me/MarsitaTheUltra`). `build.js` warns until it's changed.
- [ ] **Email list** — the signup currently opens the visitor's mail app with an "add me" message to
      `SITE.email`. For a real list, create a free Buttondown (or Mailchimp/ConvertKit) account and
      paste its form URL into `SITE.signup.action`.
- [ ] **Sound System WAV + stems** — two download tiles say "soon". Swap in `repo('...')` links once the files are pushed.

## Preview locally

```sh
cd site && python3 -m http.server 8000     # then open http://localhost:8000
```
