"""Build the Delta and Bay identity as outlined, boolean-clean SVG.

    ./fetch-fonts.sh && python3 build.py

Writes ../svg (logo files), ../social (square avatars) and ../board.svg.
Every letter is converted to outlines, so the files need no fonts to display.
"""
import os

from fontTools.misc.transform import Transform

import typeset as T
from shapes import S, union, f, polar, leg, disc, ellipse, rect, triangle, crescent

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

INK = "#15130F"
PARCHMENT = "#EEE6D4"
IVORY = "#F6F1E7"
GRAPHITE = "#262521"

SERIF = ("cormorant", (("wght", 600),))
SERIF_ITALIC = ("cormorant-italic", (("wght", 500),))
SANS = ("hanken", (("wght", 500),))
DIDONE = ("bodoni", (("opsz", 96), ("wght", 420)))

PLACES = "SAN FRANCISCO  ·  SHENZHEN"


# ---------------------------------------------------------------- the mark
def mark(theta=21, length=560, leg_w=36, hinge=29, hole=0.3, arc_w=17, overshoot=16):
    """A pair of navigator's dividers. The open legs are the delta; the arc they
    sweep is the bay. Hinge at the origin."""
    start = hinge * 0.55
    parts = []
    for side in (-1, 1):
        x, y = polar(0, 0, start, side * theta)
        parts.append(leg(x, y, side * theta, length - start, leg_w))
    parts.append(disc(0, 0, hinge))
    parts.append(crescent(0, 0, length, arc_w, -theta - overshoot, theta + overshoot))
    return S.d(*parts) - S.d(disc(0, 0, hinge * hole))


# ---------------------------------------------------------------- type
def line(text, font, size, x=0, y=0, tracking=0.0, anchor="middle"):
    key, axes = font
    d, w = T.text(text, key, size, x, y, tracking=tracking, anchor=anchor, axes=axes)
    return S.d(d), w


def runs(parts, size, x=0, y=0, tracking=0.0, anchor="middle"):
    """One line set in several fonts: parts = [(text, font), ...]."""
    widths = []
    for i, (text, (key, axes)) in enumerate(parts):
        _, w = T.text(text, key, size, 0, 0, tracking=tracking, anchor="start", axes=axes)
        widths.append(w + (tracking * size if i < len(parts) - 1 else 0))
    cx = {"middle": x - sum(widths) / 2, "end": x - sum(widths)}.get(anchor, x)
    out = S()
    for (text, (key, axes)), w in zip(parts, widths):
        d, _ = T.text(text, key, size, cx, y, tracking=tracking, anchor="start", axes=axes)
        out = out | S.d(d)
        cx += w
    return out, sum(widths)


def name(size, x=0, y=0, tracking=0.2, anchor="middle"):
    """DELTA & BAY in spaced capitals with an italic ampersand."""
    return runs([("DELTA ", SERIF), ("&", SERIF_ITALIC), (" BAY", SERIF)], size, x, y, tracking, anchor)


def cap_height(font, size):
    key, axes = font
    return -T.bounds("H", key, size, axes)[1]


# ---------------------------------------------------------------- lockups
def lockup_vertical():
    m = mark().fit(0, 0, w=520, anchor="top")
    y = m.bounds[3] + 150
    nm, _ = name(96, 0, y)
    y += 70
    rule = S.d(rect(-60, y, 60, y + 2.5))
    y += 34 + cap_height(SANS, 22)
    sub, _ = line(PLACES, SANS, 22, 0, y, tracking=0.34)
    return union(m, nm, rule, sub)


def lockup_horizontal():
    size, sub_gap = 120, 64
    ch = cap_height(SERIF, size)
    m = mark().fit(0, 0, h=ch * 3.2, anchor="topleft")
    m = m.move(0, -m.h / 2)
    x = m.bounds[2] + 90
    bar = S.d(rect(x, -m.h * 0.42, x + 2.5, m.h * 0.42))
    x += 2.5 + 90
    base = (ch - sub_gap) / 2
    nm, _ = name(size, x, base, anchor="start")
    sub, _ = line(PLACES, SANS, 24, x + 4, base + sub_gap, tracking=0.38, anchor="start")
    return union(m, bar, nm, sub)


def wordmark():
    return name(120, tracking=0.22)[0]


# ---------------------------------------------------------------- monogram
def monogram(font=DIDONE, size=640):
    """A mirrored D and a B sharing a single stem."""
    key, axes = font
    D = S.d(T.text("D", key, size, 0, 0, anchor="start", axes=axes)[0])
    B = S.d(T.text("B", key, size, 0, 0, anchor="start", axes=axes)[0])

    def stem(shape):
        # a thin horizontal slice through the lower bowl; the leftmost piece is the stem
        y = -shape.h * 0.3
        pieces = (shape & S.d(rect(-size, y - 0.5, 2 * size, y + 0.5))).contours
        b = min(pieces, key=lambda c: c.bounds[0]).bounds
        return b[0], b[2]

    b0, _ = stem(B)
    _, d1 = stem(D)
    # mirror D about x=0, then slide it so its stem lands exactly on B's stem
    return D.mirror_x().move(b0 + d1, 0) | B


# ---------------------------------------------------------------- seal
def seal():
    rx, ry, stroke = 300, 400, 9
    ring = S.d(ellipse(0, 0, rx, ry)) - S.d(ellipse(0, 0, rx - stroke, ry - stroke))
    top, _ = line("DELTA", SERIF, 88, 0, -120, tracking=0.16)
    amp, _ = line("&", SERIF_ITALIC, 250, 0, 96)
    bottom, _ = line("BAY", SERIF, 88, 0, 250, tracking=0.16)
    return union(ring, top, amp, bottom)


# ---------------------------------------------------------------- roundel
def roundel():
    outer = S.d(disc(0, 0, 470)) - S.d(disc(0, 0, 460))
    inner = S.d(disc(0, 0, 352)) - S.d(disc(0, 0, 349))
    key, axes = SERIF
    top, _ = T.text_circle("DELTA & BAY", key, 74, 0, 0, 383, tracking=0.24, axes=axes)
    key, axes = SANS
    bottom, _ = T.text_circle("SAN FRANCISCO · SHENZHEN", key, 28, 0, 0, 420,
                              tracking=0.34, axes=axes, bottom=True)
    deltas = [S.d(triangle(*polar(0, 0, 408, deg), 22)) for deg in (-90, 90)]
    m = mark().fit(0, -8, w=430)
    return union(outer, inner, S.d(top), S.d(bottom), *deltas, m)


# ---------------------------------------------------------------- output
def svg(shape, fill=INK, bg=None, pad=0.12, square=False):
    b = shape.bounds
    w, h = b[2] - b[0], b[3] - b[1]
    p = pad * max(w, h)
    vb = [b[0] - p, b[1] - p, w + 2 * p, h + 2 * p]
    if square:
        side = max(vb[2], vb[3])
        vb = [b[0] + w / 2 - side / 2, b[1] + h / 2 - side / 2, side, side]
    back = (f'<rect x="{f(vb[0])}" y="{f(vb[1])}" width="{f(vb[2])}" height="{f(vb[3])}" fill="{bg}"/>'
            if bg else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(f(v) for v in vb)}">'
            f'{back}<path fill="{fill}" d="{shape.path_d()}"/></svg>\n')


def contain(shape, x, y, w, h, frac):
    """Scale shape to fit inside frac of the box and centre it there."""
    k = min(w * frac / shape.w, h * frac / shape.h)
    b = shape.bounds
    s = shape.t(Transform().scale(k).translate(-b[0], -b[1]))
    return s.move(x + (w - s.w) / 2, y + (h - s.h) / 2)


def board(pieces):
    """Overview sheet in the spirit of a monogram mood board."""
    cell, gap, r = 760, 24, 22
    col = lambda i: gap + i * (cell + gap)
    tiles = [  # (piece, x, y, w, h, background, ink, fraction)
        ("lockup-vertical", col(0), col(0), 2 * cell + gap, 2 * cell + gap, PARCHMENT, INK, 0.56),
        ("monogram", col(2), col(0), cell, cell, GRAPHITE, PARCHMENT, 0.5),
        ("seal", col(2), col(1), cell, cell, IVORY, INK, 0.62),
        ("roundel", col(0), col(2), cell, cell, INK, PARCHMENT, 0.7),
        ("mark", col(1), col(2), cell, cell, PARCHMENT, INK, 0.56),
        ("monogram", col(2), col(2), cell, cell, PARCHMENT, INK, 0.32),
        ("lockup-horizontal", col(0), col(3), 3 * cell + 2 * gap, cell // 2, GRAPHITE, PARCHMENT, 0.62),
    ]
    W = 3 * cell + 4 * gap
    H = col(3) + cell // 2 + gap
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" fill="#1D1D1C"/>']
    for key, x, y, w, h, bg, ink, frac in tiles:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{bg}"/>')
        out.append(f'<path fill="{ink}" d="{contain(pieces[key], x, y, w, h, frac).path_d()}"/>')
    out.append("</svg>\n")
    return "".join(out)


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)
    print("wrote", rel)


if __name__ == "__main__":
    pieces = {
        "mark": mark(),
        "monogram": monogram(),
        "wordmark": wordmark(),
        "lockup-vertical": lockup_vertical(),
        "lockup-horizontal": lockup_horizontal(),
        "seal": seal(),
        "roundel": roundel(),
    }
    for key, shape in pieces.items():
        write(f"svg/delta-and-bay-{key}.svg", svg(shape, INK))
        write(f"svg/delta-and-bay-{key}-reverse.svg", svg(shape, PARCHMENT))
    write("social/avatar-mark.svg", svg(pieces["mark"], INK, PARCHMENT, pad=0.3, square=True))
    write("social/avatar-monogram.svg", svg(pieces["monogram"], PARCHMENT, GRAPHITE, pad=0.3, square=True))
    write("social/avatar-roundel.svg", svg(pieces["roundel"], PARCHMENT, INK, pad=0.08, square=True))
    write("board.svg", board(pieces))
