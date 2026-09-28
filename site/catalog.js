/* ==========================================================================
   MARSITA THE ULTRA — THE CATALOG
   This is the only file you normally edit. Every song page, the song
   switcher (top right), the "more songs" grid and the share previews are
   all built from it.

   ADD A SONG
     1. Make its images:  python3 site/tools/art.py <slug> "<cover.png>"
     2. Copy the TEMPLATE at the bottom of this file into SONGS (newest first)
     3. Run:              node site/build.js
        (creates site/<slug>/index.html with that song's share preview)
     4. Commit + push. The GitHub Action publishes the site.

   CHANGE A LINK / TEXT ON AN EXISTING SONG
     Edit it here, commit, push. Re-run build.js only if you changed the
     title, share text or the featured song.

   PATHS
     repo('Song 27 - .../file.mp3')  -> direct file link from this GitHub repo
     tree('Song 27 - .../STEMS')     -> GitHub folder page
     'songs/<slug>/cover.jpg'        -> file inside site/ (no helper needed)
   ========================================================================== */

var REPO = 'PlanetaryCouncil/marsita-the-ultra';

function repo(path) {
  return 'https://raw.githubusercontent.com/' + REPO + '/main/' +
    path.split('/').map(encodeURIComponent).join('/');
}
function tree(path) {
  return 'https://github.com/' + REPO + '/tree/main/' +
    path.split('/').map(encodeURIComponent).join('/');
}


/* ==========================================================================
   SITE-WIDE SETTINGS
   ========================================================================== */
var SITE = {
  artist:   'Marsita the Ultra',
  url:      'https://marsita.planetarycouncil.org/',  // !!! final domain, trailing slash
  featured: 'soundsystem',                             // what the home page shows
  email:    'email@genesis.re',
  repo:     'https://github.com/' + REPO,

  /* EMAIL SIGNUP
     Until a mailing-list provider is set up, the form opens the visitor's
     mail app with a ready-to-send "add me" message to SITE.email.
     To switch to a real list (Buttondown, Mailchimp, ConvertKit...), paste
     the provider's form action URL + the name of its email field:
       action: 'https://buttondown.com/api/emails/embed-subscribe/YOURNAME',
       field:  'email'                                                     */
  signup: {
    action: '',
    field:  'email',
    hidden: {}          // extra fields some providers want, e.g. { tag: 'marsita' }
  },

  /* FOLLOW — shown at the bottom of every page.
     types: telegram x instagram tiktok youtube spotify facebook github wavlake email */
  socials: [
    { type: 'telegram',  href: 'https://t.me/MarsitaTheUltra' },           // !!! CHECK — unverified handle
    { type: 'x',         href: 'https://x.com/MarsitaTheUltra' },
    { type: 'instagram', href: 'https://www.instagram.com/MarsitaTheUltra' },
    { type: 'tiktok',    href: 'https://www.tiktok.com/@marsrobertson' },
    { type: 'spotify',   href: 'https://open.spotify.com/playlist/7lu83IHHSAOOC3qoRfoBUr', label: 'Playlist' },
    { type: 'github',    href: 'https://github.com/' + REPO, label: 'Stems' }
  ]
};


/* ==========================================================================
   SONGS — newest first. This order is the order of the switcher + grid.

   status:  'new'  New drop        'wip'  Work in progress
            'out'  Out now         'soon' Coming soon

   theme:   a = title top / labels     b = title middle / icons
            c = title bottom / quote   night = page background
            cta (optional) = big button colour, default gold

   blocks:  the page, top to bottom, after the title. Mix and match:
     { type: 'audio',     src, note }
     { type: 'youtube',   id, label }         (label = what screen readers hear)
     { type: 'quote',     text, note }
     { type: 'listen',    label, links: [{ type, href, label }] }
     { type: 'downloads', label, items: [{ label, meta, href, kind }], note }
                          kind: 'file' (default) | 'stems' | 'source' | 'soon'
     { type: 'card',      title, html }
     { type: 'specs',     title, items: [['Runtime', '4:16'], ...] }
     { type: 'vote',      title, intro, candidates: [{ name, thumb, full }] }
     { type: 'countdown', to: '2026-11-01T18:00:00Z', label, done }
     { type: 'signup',    title, text }     (puts the email form here
                                             instead of only at the bottom)
     { type: 'cta',       title, label, href, image }
   ========================================================================== */
var SONGS = [

  /* ------------------------------------------------------------------------
     SOUND SYSTEM — Truth Not Hate
     ------------------------------------------------------------------------ */
  {
    slug:     'soundsystem',
    title:    'Truth Not Hate',
    lines:    ['Truth', 'Not Hate'],           // how the big title breaks
    status:   'wip',
    runtime:  '7:23',
    cover:    'songs/soundsystem/cover.jpg',
    theme:    { a: '#2fe6ff', b: '#8b7bff', c: '#ff2fb3', night: '#0a0616' },
    share: {
      title:       'TRUTH NOT HATE — Marsita the Ultra',
      description: 'The only good system is the sound system. Free MP3, WAV + stems for DJs. Work in progress — released rough on purpose. Come vote on the cover.',
      image:       'songs/soundsystem/preview.jpg'
    },
    kicker: 'New drop · Work in progress',
    sub:    'The sound system song · 7:23',
    hook:   'The only good system is <b>the sound system</b>.',

    blocks: [
      { type: 'audio',
        src:  repo('Song 35 - soundsystem/Marsita the Ultra — TRUTH NOT HATE (the only good system is the sound system).mp3'),
        note: 'Full track · free · no sign-up' },

      { type: 'quote',
        text: '“We party till we win — we occupy with love”',
        note: 'the drop, mid-song · built to be looped' },

      { type: 'downloads', label: 'Download & remix — everything is open',
        items: [
          { label: 'MP3',    meta: 'Audio · 11 MB',
            href: repo('Song 35 - soundsystem/Marsita the Ultra — TRUTH NOT HATE (the only good system is the sound system).mp3') },
          { label: 'WAV',    meta: 'Lossless · soon',       href: tree('Song 35 - soundsystem'), kind: 'soon' },
          { label: 'Stems',  meta: 'Dropping soon',         href: tree('Song 35 - soundsystem'), kind: 'soon' },
          { label: 'Source', meta: 'GitHub · all files',    href: tree('Song 35 - soundsystem'), kind: 'source' }
        ],
        note: 'Everything lands in the open GitHub repo — audio, artwork, eventually the stems and project files. Remix it, cut it, sample it, play it out.' },

      { type: 'card', title: 'Released rough, on purpose',
        html: '<p>Honesty first: the <b>intro is a little rough</b> and the <b>ending is a little rough</b>. The middle 90% — the build, the drop, <i>we party till we win, we occupy with love</i> — is exactly where it should be.</p>' +
              '<p>If you’re a DJ, you were never going to play my intro anyway. You’re going to <b>mix in, loop your favourite moment, and mix out</b>. So instead of sitting on the track for another month polishing thirty seconds nobody hears in the club, it’s out now. Perfecting an intro that gets blended away is a bad trade against a dance floor tonight.</p>' +
              '<p>When the final master lands, it lands here first. Same page, same links.</p>' },

      { type: 'specs', title: 'The details',
        items: [['Runtime', '7:23'], ['Status', 'Work in progress'], ['Best bit', 'The middle 90%'], ['Licence', 'Open · remix it']] },

      { type: 'vote', title: 'Vote for the cover',
        intro: '<b>13 candidates.</b> One becomes the cover. Tap to zoom, hit <b>vote</b> on your favourite, then fire it at me on Telegram, X or email. Got a better idea entirely? Even better — send that.',
        candidates: [
          ['Warehouse WOW',       'grok WOW.png'],
          ['Neon Cathedral',      'grok chat NICE.png'],
          ['Laser Temple',        'grok chat v2.png'],
          ['Big Rig',             'grok chat v3.png'],
          ['Boombox Wall',        'grok chat v4.png'],
          ['Heart Stack',         'grok chat v5.png'],
          ['Rainbow Type',        'soundssystem 02 d7e9df10-b2d0-429e-b3f2-69b58a15fa8f.png'],
          ['Widescreen Rig',      'soundssystem d7e9df10-b2d0-429e-b3f2-69b58a15fa8f.png'],
          ['Doves & Butterflies', 'soundssystem initial improved d7e9df10-b2d0-429e-b3f2-69b58a15fa8f.png'],
          ['Sky Towers',          'soundsyste m0bb19da1-1408-491e-b159-79318d9b5f1f.png'],
          ['Planet Heart',        'soundsystem 04 e32f9f8f-ec33-4726-86be-302275c1a36b.png'],
          ['The Listener',        'techno rave 877f848c-c5f2-4a6e-bc13-1315188ee92c.png'],
          ['Listener II',         'techno rave title speaker 877f848c-c5f2-4a6e-bc13-1315188ee92c.png']
        ].map(function (c, i) {
          var n = i + 1;
          return { name: c[0],
                   thumb: 'songs/soundsystem/art/art' + (n < 10 ? '0' : '') + n + '.jpg',
                   full:  repo('Song 35 - soundsystem/ARTWORK COVER/' + c[1]) };
        }) },

      { type: 'card', title: 'Open for business',
        html: '<p>This page is a <b>sound system</b>, not a billboard. Suggest ideas, send edits, claim a remix, book the track, put it in a mix, put it in a set, put it in a film.</p>' +
              '<p>Collabs, DJ plays, radio, playlists, clips, press — <b>always open</b>. The fastest way in is a message.</p>' },

      { type: 'cta', title: 'Then do the thing',
        label: '🔊 Book it · remix it · suggest something wild',
        href:  'mailto:email@genesis.re?subject=SOUND%20SYSTEM%20%E2%80%94%20let%27s%20talk' }
    ],

    footnote: 'Work in progress, shared early on purpose. Truth, not hate. Party till we win.'
  },


  /* ------------------------------------------------------------------------
     VOTE FOR THE BIN
     ------------------------------------------------------------------------ */
  {
    slug:     'vote-for-the-bin',
    title:    'Vote for the Bin',
    lines:    ['Vote for', 'the Bin'],
    status:   'out',
    runtime:  '4:16',
    cover:    'songs/vote-for-the-bin/cover.jpg',
    theme:    { a: '#ffd23f', b: '#ff5a1f', c: '#ff2fb3', night: '#08091c' },
    share: {
      title:       'Vote for the Bin — Marsita the Ultra',
      description: '34 candidates in the Clacton by-election. One of them was a bin. This is his unofficial anthem.',
      image:       'songs/vote-for-the-bin/preview.jpg'
    },
    kicker: 'Clacton by-election · 13 August 2026',
    sub:    'Count Binface vs Farage · 174 BPM · 4:16',
    hook:   '34 candidates. One was <b>a bin</b>. This is his unofficial anthem.',

    blocks: [
      { type: 'youtube', id: '2drwqfG5Rps', label: 'Vote for the Bin — Marsita the Ultra' },

      { type: 'listen', label: 'Watch & listen',
        links: [
          { type: 'youtube',   href: 'https://youtu.be/2drwqfG5Rps' },
          { type: 'shorts',    href: 'https://www.youtube.com/shorts/6gNfW0Nmyoc' },
          { type: 'instagram', href: 'https://www.instagram.com/p/DbJafQYM61y/' },
          { type: 'tiktok',    href: 'https://www.tiktok.com/@marsrobertson/video/7665805801113586966' },
          { type: 'x',         href: 'https://x.com/MarsitaTheUltra/status/2080347524305445363' },
          { type: 'facebook',  href: 'https://www.facebook.com/reel/3621099188047638' },
          { type: 'spotify',   href: 'https://open.spotify.com/track/6JD6IedcWhLJQA99o0w7iF' }
        ] },

      { type: 'downloads', label: 'Download & remix — everything is open',
        items: [
          { label: 'Video 16:9',  meta: 'MP4 · 83 MB', href: 'https://planetarycouncil.org/binface/marsita-the-ultra-vote-for-the-bin.mp4' },
          { label: 'Vertical 3m', meta: 'MP4 · 58 MB', href: 'https://planetarycouncil.org/binface/marsita-the-ultra-vote-for-the-bin-3m.mp4' },
          { label: 'Hook 28s',    meta: 'MP4 · 20 MB', href: 'https://planetarycouncil.org/binface/marsita-the-ultra-vote-for-the-bin-SHORT.mp4' },
          { label: 'WAV',    meta: 'Lossless · 48 MB', href: repo('Song 34 - count binface/FINAL AUDIO/Marsita the Ultra — Vote for the Bin (Count Binface vs Farage).wav') },
          { label: 'MP3',    meta: 'Audio · 5.7 MB',   href: repo('Song 34 - count binface/FINAL AUDIO/Marsita the Ultra — Vote for the Bin (Count Binface vs Farage).mp3') },
          { label: 'Stems',  meta: '10 tracks',        href: tree('Song 34 - count binface/STEMS'), kind: 'stems' },
          { label: 'Source', meta: 'GitHub · all files', href: tree('Song 34 - count binface'), kind: 'source' }
        ],
        note: 'Stems, project files, the visualiser code and every rejected version — all public on GitHub. Remix it, cut it, sample it.' },

      { type: 'card', title: 'The story',
        html: '<p>On 13 August 2026, Clacton held the strangest by-election in British history. Nigel Farage resigned his seat and immediately stood again in the vacancy he created. A record <b>34 candidates</b> ran against him — one of them Count Binface, a man with a bin on his head.</p>' +
              '<p>This is the unofficial anthem of that moment. Funny, not partisan. Engineered to make you smile.</p>' },

      { type: 'specs', title: 'The details',
        items: [['Runtime', '4:16'], ['Tempo', '174 BPM'], ['Formats', '16:9 · 9:16 · 1:1'], ['Master', '1920×1080']] },

      { type: 'cta', title: 'Then do the thing',
        image: 'https://binface.planetarycouncil.org/voting-card.png',
        label: '🗳️ Where do YOU stand? — 10 questions, 60 seconds',
        href:  'https://planetarycouncil.org/vote' }
    ],

    footnote: 'Unofficial & independent. Not affiliated with Count Binface, any candidate or campaign. Satirical music, not campaign material.'
  },


  /* ------------------------------------------------------------------------
     GLOBAL PEACE
     ------------------------------------------------------------------------ */
  {
    slug:     'global-peace',
    title:    'Global Peace',
    lines:    ['Global', 'Peace'],
    status:   'out',
    runtime:  '7:56',
    cover:    'songs/global-peace/cover.jpg',
    theme:    { a: '#ffe3a3', b: '#ffae42', c: '#ff5f3d', night: '#0d0812' },
    share: {
      title:       'Global Peace — Marsita the Ultra',
      description: 'Global pause. Global peace. Peace is now. Stream it on Spotify or WavLake — WAV + stems free on GitHub.',
      image:       'songs/global-peace/preview.jpg'
    },
    kicker: 'Out now',
    sub:    'Marsita the Ultra · 7:56',
    hook:   'Global pause. Global peace. <b>Peace is now.</b>',

    blocks: [
      { type: 'audio', src: repo('Song 27 - Global Pause/Marsita the Ultra — Global Peace.mp3'), note: 'Full track · free' },

      { type: 'listen', label: 'Stream it',
        links: [
          { type: 'spotify', href: 'https://open.spotify.com/track/6xHqj6pSYViFns3U764Mt1' },
          { type: 'wavlake', href: 'https://wavlake.com/track/2a0a0fd9-ed6d-4396-a08f-697c6ea1c118' }
        ] },

      { type: 'quote', text: '“Starting now. Hope is now. This is hope.”', note: 'verse 2' },

      { type: 'downloads', label: 'Download & remix',
        items: [
          { label: 'MP3',    meta: 'Audio · 11 MB',      href: repo('Song 27 - Global Pause/Marsita the Ultra — Global Peace.mp3') },
          { label: 'WAV',    meta: 'Lossless · 88 MB',   href: repo('Song 27 - Global Pause/Marsita the Ultra — Global Peace.wav') },
          { label: 'Stems',  meta: '7 tracks',           href: tree('Song 27 - Global Pause/STEMS'), kind: 'stems' },
          { label: 'Source', meta: 'GitHub · all files', href: tree('Song 27 - Global Pause'), kind: 'source' }
        ] }
    ]
  },


  /* ------------------------------------------------------------------------
     SANCTION REALITY
     ------------------------------------------------------------------------ */
  {
    slug:     'sanction-reality',
    title:    'Sanction Reality',
    lines:    ['Sanction', 'Reality'],
    status:   'out',
    runtime:  '3:50',
    cover:    'songs/sanction-reality/cover.jpg',
    theme:    { a: '#c6ff3a', b: '#3dff8b', c: '#ff5a1f', night: '#060d08' },
    share: {
      title:       'Sanction Reality — Marsita the Ultra',
      description: 'Sanction reality — it’s easier that way. Music video on YouTube, WAV + stems free on GitHub.',
      image:       'songs/sanction-reality/preview.jpg'
    },
    kicker: 'Out now · music video',
    sub:    'Marsita the Ultra · 3:50',
    hook:   'Sanction reality. <b>It’s easier that way.</b>',

    blocks: [
      { type: 'youtube', id: 'F--SWFQ6M9c', label: 'Sanction Reality — Marsita the Ultra' },

      { type: 'listen', label: 'Watch & listen',
        links: [
          { type: 'youtube', href: 'https://www.youtube.com/watch?v=F--SWFQ6M9c' },
          { type: 'spotify', href: 'https://open.spotify.com/playlist/7lu83IHHSAOOC3qoRfoBUr', label: 'Playlist' }
        ] },

      { type: 'card', title: 'From the lyrics',
        html: '<p><i>Sanction the judges<br>War crimes disappear<br>Livestreamed in 4K<br>Still don’t see clear</i></p>' +
              '<p><i>That was a verse<br>Now this is refrain<br>Follow the narrative<br>From truth refrain.</i></p>' },

      { type: 'downloads', label: 'Download & remix',
        items: [
          { label: 'MP3',    meta: 'Audio · 4.9 MB',     href: repo('Song 22 - Sanction Reality/Marsita the Ultra - Sanction Reality.mp3') },
          { label: 'WAV',    meta: 'Lossless · 43 MB',   href: repo('Song 22 - Sanction Reality/Marsita the Ultra – Sanction Reality.wav') },
          { label: 'Stems',  meta: '5 tracks + MIDI',    href: tree('Song 22 - Sanction Reality/stems v2 Marsita the Ultra – Sanction Reality Stems'), kind: 'stems' },
          { label: 'Source', meta: 'GitHub · all files', href: tree('Song 22 - Sanction Reality'), kind: 'source' }
        ] }
    ]
  },


  /* ------------------------------------------------------------------------
     GREENLAND IS NOT A GREEN LAND
     ------------------------------------------------------------------------ */
  {
    slug:     'greenland',
    title:    'Greenland Is Not a Green Land',
    lines:    ['Greenland', 'Is Not a', 'Green Land'],
    status:   'out',
    runtime:  '5:04',
    cover:    'songs/greenland/cover.jpg',
    theme:    { a: '#b8fff0', b: '#2fe6ff', c: '#4dff9a', night: '#040d16' },
    share: {
      title:       'Greenland Is Not a Green Land — Marsita the Ultra',
      description: 'It’s a land of ice. But it’s not Iceland either. Drum & bass — on Spotify and WavLake, WAV stems free on GitHub.',
      image:       'songs/greenland/preview.jpg'
    },
    kicker: 'Out now · drum & bass',
    sub:    'Marsita the Ultra · 5:04',
    hook:   'It’s a land of ice. <b>But it’s not Iceland either.</b>',

    blocks: [
      { type: 'audio', src: repo('Song 06 - Greenland Is Not Green Land/Greenland Is Not a Green Land (latest and final).mp3'), note: 'Full track · free' },

      { type: 'listen', label: 'Stream it',
        links: [
          { type: 'spotify', href: 'https://open.spotify.com/track/78eHfZrGRXHFyXXdYgALhi' },
          { type: 'wavlake', href: 'https://wavlake.com/album/49be3032-13a8-438d-addf-7a400815aebf' }
        ] },

      { type: 'quote', text: '“Every dude in Greenland gets a Cybertruck as prize”', note: 'verse 3 · totally not a bribe' },

      { type: 'downloads', label: 'Download & remix',
        items: [
          { label: 'MP3',    meta: 'Audio · 6.9 MB',     href: repo('Song 06 - Greenland Is Not Green Land/Greenland Is Not a Green Land (latest and final).mp3') },
          { label: 'WAV',    meta: 'Lossless · 56 MB',   href: repo('Song 06 - Greenland Is Not Green Land/Greenland Is Not a Green Land (latest and final).wav') },
          { label: 'Stems',  meta: '6 tracks · WAV',     href: tree('Song 06 - Greenland Is Not Green Land/STEMS'), kind: 'stems' },
          { label: 'Source', meta: 'GitHub · all files', href: tree('Song 06 - Greenland Is Not Green Land'), kind: 'source' }
        ] }
    ]
  }

];


/* ==========================================================================
   TEMPLATE — an upcoming release with a countdown and the signup up top.
   Copy into SONGS (at the top, it's newest), fill in, set SITE.featured to
   its slug for launch week, run build.js.
   ==========================================================================

  {
    slug:     'next-song',
    title:    'Next Song',
    lines:    ['Next', 'Song'],
    status:   'soon',
    runtime:  '',
    cover:    'songs/next-song/cover.jpg',
    theme:    { a: '#2fe6ff', b: '#8b7bff', c: '#ff2fb3', night: '#0a0616' },
    share: {
      title:       'NEXT SONG — Marsita the Ultra',
      description: 'Drops 1 November. Get it first.',
      image:       'songs/next-song/preview.jpg'
    },
    kicker: 'Coming soon · 1 November 2026',
    sub:    'Marsita the Ultra',
    hook:   'One line that makes people want it.',

    blocks: [
      { type: 'countdown', to: '2026-11-01T18:00:00Z', label: 'until it drops', done: 'OUT NOW' },
      { type: 'signup', title: 'Get it first', text: 'One email the second it drops. Stems included.' },
      { type: 'card', title: 'What it is', html: '<p>...</p>' }
    ]
  },

   ========================================================================== */


var CATALOG = { site: SITE, songs: SONGS };
if (typeof module !== 'undefined') module.exports = CATALOG;
