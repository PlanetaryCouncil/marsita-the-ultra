/* ==========================================================================
   MARSITA THE ULTRA — page renderer.
   Reads CATALOG (catalog.js) and builds the page for <body data-song="...">.
   You shouldn't need to edit this to add songs — see catalog.js.
   ========================================================================== */
(function () {
  'use strict';

  var SITE  = CATALOG.site;
  var SONGS = CATALOG.songs;
  var body  = document.body;
  var BASE  = body.getAttribute('data-base') || '';

  var song = find(body.getAttribute('data-song')) || find(SITE.featured) || SONGS[0];
  var signupShown = false;
  var uid = 0;

  var STATUS = { 'new': 'New drop', wip: 'Work in progress', out: 'Out now', soon: 'Coming soon' };


  /* ------------------------------------------------------------------------
     helpers
     ------------------------------------------------------------------------ */
  function find(slug) {
    for (var i = 0; i < SONGS.length; i++) if (SONGS[i].slug === slug) return SONGS[i];
    return null;
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function url(p) {                       // site-relative path -> works from any page depth
    if (!p) return '';
    return /^([a-z]+:|\/\/|#)/i.test(p) ? p : BASE + p;
  }
  function songHref(s) { return BASE + s.slug + '/'; }
  function pageUrl(s)  { return SITE.url + s.slug + '/'; }
  function chip(s) {
    return s.status ? '<span class="chip s-' + esc(s.status) + '">' + esc(STATUS[s.status] || s.status) + '</span>' : '';
  }
  function ext(href) { return /^https?:/.test(href) ? ' target="_blank" rel="noopener"' : ''; }
  function social(type) {
    for (var i = 0; i < SITE.socials.length; i++) if (SITE.socials[i].type === type) return SITE.socials[i];
    return null;
  }
  function xHandle() {
    var x = social('x');
    var m = x && x.href.match(/x\.com\/([^\/?#]+)/);
    return m ? '@' + m[1] : '';
  }
  function hexToRgb(h) {
    h = h.replace('#', '');
    if (h.length === 3) h = h.replace(/./g, '$&$&');
    var n = parseInt(h, 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255].join(',');
  }


  /* ------------------------------------------------------------------------
     icons — platform tiles. [label, brand colour (hover border), svg body]
     ------------------------------------------------------------------------ */
  var ICONS = {
    youtube:   ['YouTube', '#ff0000', '<path fill="#ff0000" d="M23 12s0-3.9-.5-5.8a3 3 0 0 0-2.1-2.1C18.5 3.6 12 3.6 12 3.6s-6.5 0-8.4.5a3 3 0 0 0-2.1 2.1C1 8.1 1 12 1 12s0 3.9.5 5.8a3 3 0 0 0 2.1 2.1c1.9.5 8.4.5 8.4.5s6.5 0 8.4-.5a3 3 0 0 0 2.1-2.1c.5-1.9.5-5.8.5-5.8z"/><path fill="#fff" d="M9.9 15.4V8.6l5.9 3.4z"/>'],
    shorts:    ['Shorts', '#ff2f4b', '<rect x="6" y="2" width="12" height="20" rx="5" fill="#ff2f4b"/><path fill="#fff" d="M10.5 8.4v7.2l5.2-3.6z"/>'],
    instagram: ['Instagram', '#e1306c', '<rect x="2.5" y="2.5" width="19" height="19" rx="5.5" fill="none" stroke="#e1306c" stroke-width="2"/><circle cx="12" cy="12" r="4.3" fill="none" stroke="#e1306c" stroke-width="2"/><circle cx="17.6" cy="6.4" r="1.35" fill="#e1306c"/>'],
    tiktok:    ['TikTok', '#25f4ee', '<path fill="#25f4ee" d="M15.8 2h-2.9v13.3a2.6 2.6 0 1 1-2.2-2.6v-3a5.6 5.6 0 1 0 5.1 5.6V8.9a7 7 0 0 0 4 1.3V7.3a4 4 0 0 1-4-4V2z"/>'],
    x:         ['X', '#ffffff', '<path fill="#fff" d="M17.7 3h3.2l-7 8 8.2 10h-6.4l-5-6.1L4.9 21H1.7l7.5-8.6L1.4 3H8l4.5 5.6L17.7 3zm-1.1 16.1h1.8L7.9 4.8H6l10.6 14.3z"/>'],
    facebook:  ['Facebook', '#0866ff', '<circle cx="12" cy="12" r="10" fill="#0866ff"/><path fill="#fff" d="M15.1 13.1l.44-2.9h-2.78V8.32c0-.79.39-1.56 1.63-1.56h1.27V4.29s-1.15-.2-2.25-.2c-2.3 0-3.8 1.39-3.8 3.91v2.2H6.96v2.9h2.65v7.02a10.5 10.5 0 0 0 3.15 0V13.1z"/>'],
    spotify:   ['Spotify', '#1db954', '<circle cx="12" cy="12" r="10" fill="#1db954"/><g stroke="#0b1020" stroke-width="1.7" stroke-linecap="round" fill="none"><path d="M7.1 9.3c3.3-.9 6.9-.6 9.6 1.1"/><path d="M7.7 12.6c2.7-.7 5.6-.4 7.8 1"/><path d="M8.3 15.6c2.1-.5 4.4-.3 6.1.8"/></g>'],
    telegram:  ['Telegram', '#2aabee', '<circle cx="12" cy="12" r="10" fill="#2aabee"/><path fill="#fff" d="M17.4 7.2 15.6 16c-.13.6-.5.74-1 .46l-2.8-2.06-1.35 1.3c-.15.15-.27.27-.56.27l.2-2.85 5.2-4.7c.23-.2-.05-.31-.35-.11l-6.4 4.03-2.77-.87c-.6-.19-.61-.6.13-.89l10.8-4.16c.5-.19.94.11.78.78z"/>'],
    github:    ['GitHub', '#b7aaff', '<path fill="#b7aaff" d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.8c-2.8.6-3.4-1.3-3.4-1.3-.5-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.3 1.1 2.9.8.1-.6.4-1.1.6-1.3-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.7 1a9.4 9.4 0 0 1 5 0c1.9-1.3 2.7-1 2.7-1 .5 1.4.2 2.4.1 2.7.6.7 1 1.6 1 2.7 0 3.9-2.4 4.7-4.6 5 .4.3.7.9.7 1.9v2.8c0 .3.2.6.7.5A10 10 0 0 0 12 2z"/>'],
    wavlake:   ['WavLake', '#e6ff5c', '<g stroke="#e6ff5c" stroke-width="2" stroke-linecap="round" fill="none"><path d="M3 12h1.5M6.5 8v8M10 5v14M13.5 9v6M17 6.5v11M20.5 10.5v3"/></g>'],
    email:     ['Email', '#ffd23f', '<rect x="2.5" y="5" width="19" height="14" rx="2.5" fill="none" stroke="#ffd23f" stroke-width="2"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5" fill="none" stroke="#ffd23f" stroke-width="2" stroke-linejoin="round"/>']
  };

  var GLYPH = {
    file:   '<svg viewBox="0 0 24 24" aria-hidden="true"><g stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"><path d="M12 3v11"/><path d="M7.5 10.5 12 15l4.5-4.5"/><path d="M4.5 19.5h15"/></g></svg>',
    stems:  '<svg viewBox="0 0 24 24" aria-hidden="true"><g stroke="currentColor" stroke-width="1.9" stroke-linecap="round" fill="none"><path d="M4 15V9M8 18V6M12 20V4M16 17V7M20 14v-4"/></g></svg>',
    soon:   '<svg viewBox="0 0 24 24" aria-hidden="true"><g stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></g></svg>',
    chevron:'<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  };
  GLYPH.source = '<svg viewBox="0 0 24 24" aria-hidden="true">' + ICONS.github[2].replace(/#b7aaff/g, 'currentColor') + '</svg>';

  function tiles(links) {
    return '<ul class="plat">' + links.map(function (l) {
      var ic = ICONS[l.type] || ICONS.email;
      var label = l.label || ic[0];
      return '<li><a href="' + esc(l.href) + '"' + ext(l.href) + ' style="--brand:' + ic[1] + '" title="' + esc(label) + '">' +
             '<svg viewBox="0 0 24 24" aria-hidden="true">' + ic[2] + '</svg><small>' + esc(label) + '</small></a></li>';
    }).join('') + '</ul>';
  }


  /* ------------------------------------------------------------------------
     theme
     ------------------------------------------------------------------------ */
  var T = song.theme || {};
  var root = document.documentElement.style;
  ['a', 'b', 'c', 'night', 'cta'].forEach(function (k) { if (T[k]) root.setProperty('--' + k, T[k]); });
  document.title = song.title + ' — ' + SITE.artist;


  /* ------------------------------------------------------------------------
     blocks
     ------------------------------------------------------------------------ */
  var BLOCKS = {

    audio: function (b) {
      return '<div class="player"><img src="' + esc(url(song.cover)) + '" alt="" width="64" height="64">' +
             '<div class="col"><audio controls preload="none" src="' + esc(url(b.src)) + '"></audio>' +
             (b.note ? '<p class="note">' + esc(b.note) + '</p>' : '') + '</div></div>';
    },

    youtube: function (b) {
      var name = b.label || song.title;
      var bg = "url('https://i.ytimg.com/vi/" + esc(b.id) + "/hqdefault.jpg'), url('" + esc(url(song.cover)) + "')";
      return '<div class="video"><button type="button" data-yt="' + esc(b.id) + '" data-title="' + esc(name) + '"' +
             ' style="background-image:' + bg + '" aria-label="Play video: ' + esc(name) + '"></button></div>';
    },

    quote: function (b) {
      return '<p class="drop">' + esc(b.text) + (b.note ? '<small>' + esc(b.note) + '</small>' : '') + '</p>';
    },

    listen: function (b) {
      return (b.label ? '<p class="rowlabel">' + esc(b.label) + '</p>' : '') + tiles(b.links);
    },

    downloads: function (b) {
      return (b.label ? '<p class="rowlabel">' + esc(b.label) + '</p>' : '') +
        '<ul class="files">' + b.items.map(function (f) {
          var k = f.kind || 'file';
          return '<li><a class="k-' + esc(k) + '" href="' + esc(url(f.href)) + '"' + (k === 'file' ? ' download' : '') + '>' +
                 (GLYPH[k] || GLYPH.file) +
                 '<span class="meta"><b class="fmt">' + esc(f.label) + '</b><span class="sz">' + esc(f.meta) + '</span></span></a></li>';
        }).join('') + '</ul>' +
        (b.note ? '<p class="openline">' + esc(b.note) + '</p>' : '');
    },

    card: function (b) { return '<div class="card">' + b.html + '</div>'; },

    specs: function (b) {
      return '<div class="specs">' + b.items.map(function (kv) {
        return '<div><b>' + esc(kv[0]) + '</b><span>' + esc(kv[1]) + '</span></div>';
      }).join('') + '</div>';
    },

    countdown: function (b) {
      return '<div class="count" data-to="' + esc(b.to) + '" data-done="' + esc(b.done || 'Out now') + '" aria-label="Countdown">' +
             '<div><span data-u="d">—</span><small>days</small></div>' +
             '<div><span data-u="h">—</span><small>hours</small></div>' +
             '<div><span data-u="m">—</span><small>mins</small></div></div>' +
             (b.label ? '<p class="count-label">' + esc(b.label) + '</p>' : '');
    },

    signup: function (b) {
      signupShown = true;
      return signupBox(b.title || 'Get it <em>first</em>', b.text);
    },

    vote: function (b) {
      return (b.intro ? '<div class="card vote-intro"><p>' + b.intro + '</p></div>' : '') +
        '<ul class="gallery">' + b.candidates.map(function (c, i) {
          var n = i + 1;
          return '<li data-n="' + n + '"><button type="button" class="shot" title="Zoom">' +
                 '<img loading="lazy" src="' + esc(url(c.thumb)) + '" alt="Cover candidate ' + n + ': ' + esc(c.name) + '"></button>' +
                 '<div class="strip"><span class="num">#' + n + ' ' + esc(c.name) + '</span>' +
                 '<button type="button" class="vote">Vote</button></div></li>';
        }).join('') + '</ul>' +
        '<div class="votebar" hidden><p>Your pick: <b class="pickname">—</b>. Now make it count:</p>' +
        '<div class="ways"><a class="v-tg" target="_blank" rel="noopener" href="#">Telegram</a>' +
        '<a class="v-x" target="_blank" rel="noopener" href="#">Post on X</a>' +
        '<a class="v-em" href="#">Email it</a></div></div>';
    },

    cta: function (b) {
      return (b.image ? '<a class="cardshot" href="' + esc(b.href) + '"' + ext(b.href) + '><img src="' + esc(url(b.image)) + '" alt="" loading="lazy"></a>' : '') +
             '<a class="ballot" href="' + esc(b.href) + '"' + ext(b.href) + '>' + esc(b.label) + '</a>';
    }
  };

  function signupBox(title, text) {
    var id = 'em' + (++uid);
    var tg = social('telegram');
    return '<div class="signup"><p class="big">' + title + '</p>' +
      '<p class="sub">' + esc(text || 'One email per release — new songs, stems and remixes the day they drop.') + '</p>' +
      '<form><label class="sr" for="' + id + '">Email address</label>' +
      '<input id="' + id + '" type="email" required autocomplete="email" placeholder="you@example.com">' +
      '<button type="submit">Sign me up</button></form>' +
      '<p class="fine">No spam. Just drops.' +
      (tg ? ' <a href="' + esc(tg.href) + '" target="_blank" rel="noopener">Or get them on Telegram</a>' : '') + '</p></div>';
  }


  /* ------------------------------------------------------------------------
     page
     ------------------------------------------------------------------------ */
  var lines = song.lines || [song.title];
  var long  = lines.length > 2 || lines.some(function (l) { return l.length > 9; });

  var others = SONGS.filter(function (s) { return s !== song; });

  var html = '';

  // top bar
  html += '<header class="top"><a class="brand" href="' + (BASE || './') + '">' +
          esc(SITE.artist).replace(/^(\S+)\s(.+)$/, '$1 <span>$2</span>') + '</a>' +
          '<nav class="switch" aria-label="Songs"><button type="button" aria-expanded="false" aria-controls="menu">' +
          '<img src="' + esc(url(song.cover)) + '" alt="">' +
          '<span class="now">' + esc(song.title) + '</span>' + GLYPH.chevron + '</button>' +
          '<ul class="menu" id="menu" hidden><li class="head">All songs · ' + SONGS.length + '</li>' +
          SONGS.map(function (s) {
            return '<li><a href="' + songHref(s) + '"' + (s === song ? ' aria-current="page"' : '') + '>' +
                   '<img src="' + esc(url(s.cover)) + '" alt="" loading="lazy">' +
                   '<span class="t">' + esc(s.title) + '</span>' +
                   '<span class="m">' + chip(s) + (s.runtime ? '<span>' + esc(s.runtime) + '</span>' : '') + '</span></a></li>';
          }).join('') + '</ul></nav></header>';

  // hero + blocks
  html += '<main class="wrap">' +
    (song.kicker ? '<p class="kicker">' + esc(song.kicker) + '</p>' : '') +
    '<h1' + (long ? ' class="long"' : '') + '>' + lines.map(esc).join('<br>') + '</h1>' +
    (song.sub ? '<p class="artist">' + esc(song.sub) + '</p>' : '') +
    (song.hook ? '<p class="hook">' + song.hook + '</p>' : '');

  (song.blocks || []).forEach(function (b, i) {
    var fn = BLOCKS[b.type];
    if (!fn) return;
    html += '<section class="block type-' + b.type + (b.title && b.type !== 'signup' ? ' has-title' : '') + '" data-i="' + i + '">' +
            (b.title && b.type !== 'signup' ? '<h2>' + esc(b.title) + '</h2>' : '') + fn(b) + '</section>';
  });
  html += '</main>';

  // end of page: signup -> follow -> more songs -> contact
  html += '<footer class="end"><div class="wrap">';
  if (!signupShown) {
    html += '<h2>Stay in the loop</h2>' + signupBox('Get the next drop <em>first</em>');
  }
  html += '<h2>Follow</h2>' + tiles(SITE.socials);
  if (others.length) {
    html += '<h2>More songs</h2><ul class="more">' + others.map(function (s) {
      return '<li><a href="' + songHref(s) + '"><img src="' + esc(url(s.cover)) + '" alt="" loading="lazy">' +
             '<span class="info"><span class="t">' + esc(s.title) + '</span>' +
             '<span class="m">' + chip(s) + (s.runtime ? '<span>' + esc(s.runtime) + '</span>' : '') + '</span></span></a></li>';
    }).join('') + '</ul>';
  }
  html += '<p class="foot">Available for DJ plays, radio, playlists, clips and press.<br>' +
          '<a href="mailto:' + esc(SITE.email) + '">' + esc(SITE.email) + '</a> · ' + esc(SITE.artist) +
          (song.footnote ? '<br><br>' + esc(song.footnote) : '') + '</p>';
  html += '</div></footer>';

  html += '<div class="lightbox" hidden><img alt=""><p></p></div>';

  // page goes in front of the <script> tags, particles canvas behind everything
  var firstScript = body.querySelector('script');
  var canvas = document.createElement('canvas');
  canvas.id = 'bg';
  canvas.setAttribute('aria-hidden', 'true');
  body.insertBefore(canvas, body.firstChild);

  var mount = document.createElement('div');
  mount.innerHTML = html;
  while (mount.firstChild) body.insertBefore(mount.firstChild, firstScript);


  /* ------------------------------------------------------------------------
     song switcher
     ------------------------------------------------------------------------ */
  (function () {
    var btn  = document.querySelector('.switch > button');
    var menu = document.getElementById('menu');
    function open(yes) {
      btn.setAttribute('aria-expanded', yes ? 'true' : 'false');
      menu.hidden = !yes;
      if (yes) (menu.querySelector('[aria-current]') || menu.querySelector('a')).focus();
    }
    btn.addEventListener('click', function () { open(menu.hidden); });
    document.addEventListener('click', function (e) {
      if (!menu.hidden && !e.target.closest('.switch')) open(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.hidden) { open(false); btn.focus(); }
    });
  })();


  /* ------------------------------------------------------------------------
     youtube facade -> real player on click
     ------------------------------------------------------------------------ */
  Array.prototype.forEach.call(document.querySelectorAll('[data-yt]'), function (b) {
    b.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(b.getAttribute('data-yt')) + '?autoplay=1';
      f.title = b.getAttribute('data-title');
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      f.allowFullscreen = true;
      b.parentNode.replaceChild(f, b);
    });
  });


  /* ------------------------------------------------------------------------
     countdowns
     ------------------------------------------------------------------------ */
  Array.prototype.forEach.call(document.querySelectorAll('.count[data-to]'), function (el) {
    var target = Date.parse(el.getAttribute('data-to'));
    function tick() {
      var ms = target - Date.now();
      if (!(ms > 0)) {
        el.innerHTML = '<div style="min-width:13rem"><span>' + esc(el.getAttribute('data-done')) + '</span><small>go listen</small></div>';
        return;
      }
      el.querySelector('[data-u=d]').textContent = Math.floor(ms / 864e5);
      el.querySelector('[data-u=h]').textContent = Math.floor(ms / 36e5) % 24;
      el.querySelector('[data-u=m]').textContent = Math.floor(ms / 6e4) % 60;
      setTimeout(tick, 30000);
    }
    tick();
  });


  /* ------------------------------------------------------------------------
     email signup — real list if SITE.signup.action is set, mail app otherwise
     ------------------------------------------------------------------------ */
  Array.prototype.forEach.call(document.querySelectorAll('.signup form'), function (form) {
    var input = form.querySelector('input');
    var cfg = SITE.signup || {};
    if (cfg.action) {
      form.action = cfg.action;
      form.method = 'post';
      form.target = '_blank';
      input.name = cfg.field || 'email';
      Object.keys(cfg.hidden || {}).forEach(function (k) {
        var h = document.createElement('input');
        h.type = 'hidden'; h.name = k; h.value = cfg.hidden[k];
        form.appendChild(h);
      });
    }
    form.addEventListener('submit', function (e) {
      if (!input.checkValidity()) { e.preventDefault(); input.reportValidity(); return; }
      var box = form.parentNode;
      var addr = input.value.trim();
      if (cfg.action) {
        setTimeout(function () {
          box.innerHTML = '<p class="done">Almost there — confirm from the email that just landed in your inbox.</p>';
        }, 50);
        return;
      }
      e.preventDefault();
      location.href = 'mailto:' + SITE.email +
        '?subject=' + encodeURIComponent('Add me to the ' + SITE.artist + ' list') +
        '&body=' + encodeURIComponent('Please add ' + addr + ' to the release list.\n\n(signed up on the ' + song.title + ' page)');
      box.innerHTML = '<p class="done">Your mail app should open with the request ready — hit send and you’re on the list.</p>' +
        '<p class="fine">Nothing opened? Email <a href="mailto:' + esc(SITE.email) + '">' + esc(SITE.email) + '</a> with “add me”.</p>';
    });
  });


  /* ------------------------------------------------------------------------
     artwork vote + lightbox
     ------------------------------------------------------------------------ */
  var lightbox = document.querySelector('.lightbox');
  var lightimg = lightbox.querySelector('img');
  var lightcap = lightbox.querySelector('p');
  var wanted = '';

  function zoom(thumb, full, caption) {
    wanted = full;
    lightimg.src = thumb;
    lightimg.alt = caption;
    lightcap.textContent = caption + ' — tap anywhere to close';
    lightbox.hidden = false;
    if (full && full !== thumb) {
      var pre = new Image();
      pre.onload = function () { if (!lightbox.hidden && wanted === full) lightimg.src = full; };
      pre.src = full;
    }
  }
  function unzoom() { lightbox.hidden = true; wanted = ''; lightimg.removeAttribute('src'); }
  lightbox.addEventListener('click', unzoom);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !lightbox.hidden) unzoom(); });

  (song.blocks || []).forEach(function (b, i) {
    if (b.type !== 'vote') return;
    var sec   = document.querySelector('.block[data-i="' + i + '"]');
    var bar   = sec.querySelector('.votebar');
    var KEY   = 'vote:' + song.slug;
    var items = sec.querySelectorAll('.gallery li');

    function render(n) {
      var c = b.candidates[n - 1];
      if (!c) return;
      Array.prototype.forEach.call(items, function (li) {
        var on = +li.getAttribute('data-n') === n;
        li.classList.toggle('picked', on);
        li.querySelector('.vote').textContent = on ? 'Picked ✓' : 'Vote';
      });
      var label = '#' + n + ' "' + c.name + '"';
      var what  = 'My vote for the ' + song.title.toUpperCase() + ' cover: ' + label;
      sec.querySelector('.pickname').textContent = '#' + n + ' ' + c.name;
      sec.querySelector('.v-tg').href = 'https://t.me/share/url?url=' + encodeURIComponent(pageUrl(song)) +
        '&text=' + encodeURIComponent(what + ' ' + xHandle());
      sec.querySelector('.v-x').href = 'https://twitter.com/intent/tweet?text=' +
        encodeURIComponent(what + ' 🔊 ' + pageUrl(song) + ' ' + xHandle());
      sec.querySelector('.v-em').href = 'mailto:' + SITE.email +
        '?subject=' + encodeURIComponent('Artwork vote: ' + song.title + ' ' + label) +
        '&body=' + encodeURIComponent(what + '.\n\nIdeas / remarks:\n');
      bar.hidden = false;
    }

    Array.prototype.forEach.call(items, function (li) {
      var n = +li.getAttribute('data-n');
      var c = b.candidates[n - 1];
      li.querySelector('.shot').addEventListener('click', function () {
        zoom(url(c.thumb), url(c.full), '#' + n + ' ' + c.name);
      });
      li.querySelector('.vote').addEventListener('click', function () {
        try { localStorage.setItem(KEY, n); } catch (e) {}
        render(n);
        bar.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
    });

    try { render(parseInt(localStorage.getItem(KEY), 10)); } catch (e) {}
  });


  /* ------------------------------------------------------------------------
     background particles in the song's colours
     ------------------------------------------------------------------------ */
  (function () {
    var COUNT = 64;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var ctx = canvas.getContext('2d');
    var dpr = window.devicePixelRatio || 1;
    var W, H, ps = [];
    var COLOURS = [T.a || '#2fe6ff', T.b || '#8b7bff', T.c || '#ff2fb3', '#ffd23f'].map(hexToRgb);

    function resize() {
      W = canvas.width  = window.innerWidth  * dpr;
      H = canvas.height = window.innerHeight * dpr;
    }
    window.addEventListener('resize', resize);
    resize();

    for (var i = 0; i < COUNT; i++) {
      ps.push({
        x: Math.random() * W, y: Math.random() * H,
        r: (Math.random() * 1.9 + 0.5) * dpr,
        s: Math.random() * 0.3 + 0.07,
        c: COLOURS[i % COLOURS.length],
        a: Math.random() * 0.45 + 0.14,
        ph: Math.random() * 6.28
      });
    }

    function frame(t) {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < ps.length; i++) {
        var p = ps[i];
        p.y -= p.s * dpr;
        if (p.y < -8) { p.y = H + 8; p.x = Math.random() * W; }
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, 6.28);
        ctx.fillStyle = 'rgba(' + p.c + ',' + p.a * (0.6 + 0.4 * Math.sin(t / 900 + p.ph)) + ')';
        ctx.fill();
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  })();

})();
