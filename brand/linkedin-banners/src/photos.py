"""Real city photos for the skyline banners: crop, colour-grade, embed.

Drop photos into photos/ and describe them in photos/photos.json:

    {
      "sf-night": {"file": "sf-night.jpg", "focus": [0.55, 0.6], "zoom": 1.0,
                   "source": "https://unsplash.com/photos/...", "credit": "Name", "licence": "Unsplash License"},
      ...
    }

`focus` is the point of the photo (0..1 across, 0..1 down) kept centred in the
panel; `zoom` > 1 crops tighter. Each panel is cropped to its exact size at 2x,
graded toward the brand navy, and embedded as JPEG, so the SVG stays one file.
"""

import base64
import io
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DIR = Path(os.environ.get("BANNER_PHOTOS", ROOT / "photos"))
NAVY = np.array([5, 10, 48], dtype=np.float32) / 255


def catalogue():
    meta = DIR / "photos.json"
    if not meta.exists():
        return {}
    return {k: v for k, v in json.loads(meta.read_text()).items() if (DIR / v["file"]).exists()}


def _crop(im, w, h, focus, zoom):
    """Largest crop of aspect w:h (divided by zoom) centred on focus, clamped inside the photo."""
    target = w / h
    cw, ch = im.width, im.height
    if cw / ch > target:
        cw = ch * target
    else:
        ch = cw / target
    cw, ch = cw / zoom, ch / zoom
    x = min(max(focus[0] * im.width - cw / 2, 0), im.width - cw)
    y = min(max(focus[1] * im.height - ch / 2, 0), im.height - ch)
    return im.crop((round(x), round(y), round(x + cw), round(y + ch))).resize((round(w), round(h)), Image.LANCZOS)


def _grade(im, mood):
    """Pull shadows toward brand navy and cool the midtones; keep warm city lights."""
    a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255
    luma = a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    if mood == "night":
        tint, shadow, contrast = np.array([0.90, 0.96, 1.10]), 0.55, 1.08
    else:  # dusk keeps the sunset warmth
        tint, shadow, contrast = np.array([0.98, 0.97, 1.04]), 0.40, 1.05
    a = np.clip((a - 0.5) * contrast + 0.5, 0, 1)
    a = a * tint
    k = (shadow * (1 - luma) ** 2.2)[..., None]
    a = a * (1 - k) + NAVY * k
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def _load(key, w, h, mood):
    info = catalogue()[key]
    im = Image.open(DIR / info["file"])
    im = _crop(im, w, h, info.get("focus", (0.5, 0.5)), info.get("zoom", 1.0))
    return _grade(im, info.get("mood", mood)), info


def panorama(c, left, right, *, mood="night", seam=(0.40, 0.60), scale=2, quality=86):
    """One full-bleed image: `left` photo cross-fading into `right` across `seam`.

    The blend is baked into a single embedded JPEG (no SVG masks), and each photo
    is cropped to the part of the banner it covers. Returns the credit lines.
    """
    W, H = round(c.W * scale), round(c.H * scale)
    a, b = round(seam[0] * W), round(seam[1] * W)
    li, linfo = _load(left, b, H, mood)
    ri, rinfo = _load(right, W - a, H, mood)
    canvas = Image.new("RGB", (W, H))
    canvas.paste(li, (0, 0))
    ramp = np.clip((np.arange(W - a) / max(1, b - a)), 0, 1)
    ramp = (ramp * ramp * (3 - 2 * ramp) * 255).astype(np.uint8)  # smoothstep
    alpha = Image.fromarray(np.tile(ramp, (H, 1)), "L")
    canvas.paste(ri, (a, 0), alpha)
    buf = io.BytesIO()
    canvas.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    data = base64.b64encode(buf.getvalue()).decode()
    c.add(f'<image x="0" y="0" width="{c.W}" height="{c.H}" preserveAspectRatio="none" '
          f'xlink:href="data:image/jpeg;base64,{data}"/>')
    return [f'{i.get("credit", "")}, {i.get("licence", "")}, {i.get("source", "")}' for i in (linfo, rinfo)]
