"""Turn text into outlined SVG path data so logo files need no fonts installed."""
import io
import math
import os
from functools import lru_cache

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
FONTS = {
    "cormorant": "CormorantGaramond[wght].ttf",
    "cormorant-italic": "CormorantGaramond-Italic[wght].ttf",
    "bodoni": "BodoniModa[opsz,wght].ttf",
    "hanken": "HankenGrotesk[wght].ttf",
}


@lru_cache(maxsize=None)
def load(key, axes=()):
    font = TTFont(os.path.join(FONT_DIR, FONTS[key]))
    if "fvar" in font:
        loc = {a.axisTag: a.defaultValue for a in font["fvar"].axes}
        loc.update(dict(axes))
        font = instancer.instantiateVariableFont(font, loc)
    buf = io.BytesIO()
    font.save(buf)
    data = buf.getvalue()
    hb_font = hb.Font(hb.Face(data))
    return font, hb_font


def shape(text, key, axes=(), features=None):
    font, hb_font = load(key, tuple(sorted(axes)))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hb_font, buf, features or {"kern": True, "liga": True})
    order = font.getGlyphOrder()
    return font, [(order[i.codepoint], p.x_advance, p.x_offset, p.y_offset)
                  for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def text(s, key, size, x=0, y=0, tracking=0.0, anchor="middle", axes=(), features=None,
         optical=True):
    """Return (path_d, width). y is the baseline. tracking is in em.

    With anchor='middle' and optical=True the trailing tracking is ignored so
    letterspaced words still centre on x.
    """
    font, glyphs = shape(s, key, axes, features)
    upm = font["head"].unitsPerEm
    k = size / upm
    track = tracking * upm
    total = sum(adv for _, adv, _, _ in glyphs) + track * (len(glyphs) - 1)
    width = total * k
    if anchor == "middle":
        x0 = x - width / 2
    elif anchor == "end":
        x0 = x - width
    else:
        x0 = x
    gs = font.getGlyphSet()
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    cx = 0
    for name, adv, xo, yo in glyphs:
        t = TransformPen(pen, (k, 0, 0, -k, x0 + (cx + xo) * k, y - yo * k))
        gs[name].draw(t)
        cx += adv + track
    return pen.getCommands(), width


def bounds(s, key, size, axes=(), tracking=0.0):
    """Ink bounds (xmin, ymin, xmax, ymax) in SVG coords for text set at origin baseline."""
    font, glyphs = shape(s, key, axes)
    upm = font["head"].unitsPerEm
    k = size / upm
    gs = font.getGlyphSet()
    bp = BoundsPen(gs)
    cx = 0
    for name, adv, xo, yo in glyphs:
        gs[name].draw(TransformPen(bp, (k, 0, 0, -k, (cx + xo) * k, -yo * k)))
        cx += adv + tracking * upm
    return bp.bounds


def text_circle(s, key, size, cx, cy, r, center_deg=0.0, tracking=0.0, axes=(), bottom=False):
    """Set text around a circle. Top text sits outside radius r reading clockwise;
    bottom text hangs inside radius r reading left to right. Returns path d."""
    font, glyphs = shape(s, key, axes)
    upm = font["head"].unitsPerEm
    k = size / upm
    track = tracking * upm
    total = (sum(a for _, a, _, _ in glyphs) + track * (len(glyphs) - 1)) * k
    gs = font.getGlyphSet()
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    pos = -total / 2
    for name, adv, xo, yo in glyphs:
        gw = adv * k
        mid = pos + gw / 2
        ang = mid / r
        deg = center_deg + (-math.degrees(ang) if bottom else math.degrees(ang))
        t = Transform().translate(cx, cy).rotate(math.radians(deg))
        t = t.translate(-gw / 2 + xo * k, (r if bottom else -r) - yo * k).scale(k, -k)
        gs[name].draw(TransformPen(pen, tuple(t)))
        pos += gw + track * k
    return pen.getCommands(), total
