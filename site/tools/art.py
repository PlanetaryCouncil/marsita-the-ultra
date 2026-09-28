#!/usr/bin/env python3
"""
Make the two images every song page needs, from one cover image.

    python3 site/tools/art.py <slug> "<path/to/cover.png>"

writes
    site/songs/<slug>/cover.jpg     600x600   - switcher, catalog grid
    site/songs/<slug>/preview.jpg   1200x630  - share card (X, WhatsApp, Discord...)

The share card puts the square cover in the middle of a blurred, darkened copy
of itself, so lettering on the cover never gets cropped.

Add --cover-only to leave an existing preview.jpg alone.

Needs Pillow:  pip install pillow
"""
import os
import sys

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))


def main(slug, src, cover_only=False):
    out = os.path.normpath(os.path.join(HERE, '..', 'songs', slug))
    os.makedirs(out, exist_ok=True)
    im = Image.open(src).convert('RGB')

    cover = ImageOps.fit(im, (600, 600), Image.LANCZOS)
    cover.save(os.path.join(out, 'cover.jpg'), 'JPEG', quality=84, optimize=True)

    if not cover_only:
        back = ImageOps.fit(im, (1200, 630), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
        back = ImageEnhance.Brightness(back).enhance(0.45)
        front = ImageOps.fit(im, (570, 570), Image.LANCZOS)
        back.paste(front, ((1200 - 570) // 2, 30))
        back.save(os.path.join(out, 'preview.jpg'), 'JPEG', quality=84, optimize=True)

    print('wrote', os.path.relpath(out))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--cover-only']
    if len(args) != 2:
        sys.exit(__doc__)
    main(args[0], args[1], cover_only='--cover-only' in sys.argv)
