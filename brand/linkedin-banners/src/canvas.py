"""Minimal SVG canvas: gradients, layered glows and the brand lockups.

Effects are built from gradients and stacked translucent strokes only (no
filters, masks or embedded images) so the files survive Figma, Illustrator,
Inkscape and Canva imports unchanged.
"""

from xml.sax.saxutils import escape

from brand import EL, IVORY

CITIES = ("san-francisco", "dash", "shenzhen")


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Canvas:
    def __init__(self, w, h, base_h=396):
        self.W, self.H = w, h
        self.s = h / base_h  # scene scale: 1.0 on the 1584x396 profile banner
        self.defs, self.body = [], []
        self._n = 0

    def uid(self, prefix):
        self._n += 1
        return f"{prefix}{self._n}"

    def add(self, *items):
        self.body.extend(items)

    def _stops(self, stops):
        out = []
        for st in stops:
            off, col = st[0], st[1]
            op = st[2] if len(st) > 2 else 1
            out.append(f'<stop offset="{f(off)}" stop-color="{col}"'
                       + (f' stop-opacity="{f(op)}"' if op != 1 else "") + "/>")
        return "".join(out)

    def lin(self, x1, y1, x2, y2, stops):
        gid = self.uid("lg")
        self.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
                         f'x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}">'
                         f"{self._stops(stops)}</linearGradient>")
        return f"url(#{gid})"

    def rad(self, cx, cy, r, stops, sx=1.0, sy=1.0, rot=0.0):
        """Radial gradient in user space; sx/sy/rot make it elliptical."""
        gid = self.uid("rg")
        tf = ""
        if sx != 1 or sy != 1 or rot:
            tf = (f' gradientTransform="translate({f(cx)} {f(cy)}) rotate({f(rot)}) '
                  f'scale({f(sx)} {f(sy)}) translate({f(-cx)} {f(-cy)})"')
        self.defs.append(f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" '
                         f'cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"{tf}>'
                         f"{self._stops(stops)}</radialGradient>")
        return f"url(#{gid})"

    def rad_box(self, stops):
        """Radial gradient sized to each shape's own box, for reuse across many shapes."""
        gid = self.uid("rb")
        self.defs.append(f'<radialGradient id="{gid}">{self._stops(stops)}</radialGradient>')
        return f"url(#{gid})"

    def rect(self, fill, x=0, y=0, w=None, h=None, extra=""):
        w = self.W if w is None else w
        h = self.H if h is None else h
        self.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="{fill}"{extra}/>')

    def glow(self, d, *, core="#EAF4FF", tint="#3D8BFF", deep="#1F4FD8", width=1.6,
             strength=1.0, fade=None, layers=None):
        """A line of light: a crisp core inside stacked, widening translucent strokes.

        fade=(x0, y0, x1, y1, [(offset, opacity), ...]) varies the light's
        strength along that axis.
        """
        layers = layers or [(90, 0.018, deep), (48, 0.03, deep), (24, 0.055, tint),
                            (11, 0.10, tint), (5, 0.22, tint), (2.4, 0.5, core), (1, 1.0, core)]
        paints = {}
        for _, _, col in layers:
            if col in paints:
                continue
            if fade:
                x0, y0, x1, y1, stops = fade
                paints[col] = self.lin(x0, y0, x1, y1, [(o, col, a) for o, a in stops])
            else:
                paints[col] = col
        out = []
        for mult, op, col in layers:
            out.append(f'<path d="{d}" fill="none" stroke="{paints[col]}" '
                       f'stroke-width="{f(width * mult * self.s)}" stroke-opacity="{f(min(1, op * strength))}" '
                       f'stroke-linecap="round"/>')
        self.add(f'<g>{"".join(out)}</g>')

    def svg(self, title, desc=""):
        clip = self.uid("canvas")
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" '
                f'viewBox="0 0 {self.W} {self.H}">\n<title>{escape(title)}</title>\n'
                + (f"<desc>{escape(desc)}</desc>\n" if desc else "")
                + f'<defs><clipPath id="{clip}"><rect width="{self.W}" height="{self.H}"/></clipPath>\n'
                + "\n".join(self.defs) + "</defs>\n"
                + f'<g clip-path="url(#{clip})">\n' + "\n".join(self.body) + "\n</g>\n</svg>\n")


# ---------------------------------------------------------------- lockups
# Built in the master file's own units, then scaled as one group, so the
# relationships between the monogram and type stay exactly as drawn.

def _piece(key, m, x, y, anchor="middle", fill=IVORY, opacity=1.0):
    """Place element(s) `key` at scale m, top edge at y, anchored at x."""
    ids = CITIES if key == "cities" else (key,)
    els = [EL[i] for i in ids]
    x0 = min(e.x for e in els)
    x1 = max(e.x + e.w for e in els)
    y0 = min(e.y for e in els)
    y1 = max(e.y + e.h for e in els)
    w, h = (x1 - x0) * m, (y1 - y0) * m
    left = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
    op = f' opacity="{f(opacity)}"' if opacity != 1 else ""
    paths = "".join(f'<path d="{e.d}"/>' for e in els)
    svg = (f'<g fill="{fill}"{op} transform="translate({f(left - x0 * m)} {f(y - y0 * m)}) '
           f'scale({m:.5f})">{paths}</g>')
    return svg, w, h


def size(key, m=1.0):
    ids = CITIES if key == "cities" else (key,)
    els = [EL[i] for i in ids]
    return ((max(e.x + e.w for e in els) - min(e.x for e in els)) * m,
            (max(e.y + e.h for e in els) - min(e.y for e in els)) * m)


def stacked(c, x, cy, k, rows, fill=IVORY, align="middle"):
    """Vertical lockup scaled by k (px per master unit), vertically centred on cy.

    rows = [(key, scale, gap_after, opacity)] in master units; align = middle | start.
    Returns (width, height) in px.
    """
    total = sum(size(key, m)[1] + g for key, m, g, _ in rows) - rows[-1][2]
    y, parts = 0.0, []
    for key, m, gap, op in rows:
        svg, _, h = _piece(key, m, 0, y, anchor=align, fill=fill, opacity=op)
        parts.append(svg)
        y += h + gap
    width = max(size(r[0], r[1])[0] for r in rows) * k
    c.add(f'<g transform="translate({f(x)} {f(cy - total * k / 2)}) scale({k:.6f})">{"".join(parts)}</g>')
    return width, total * k


def horizontal(c, x, cy, k, *, mono=0.5, gap=230, lines=None, anchor="start", fill=IVORY):
    """Monogram on the left, type block on the right, all vertically centred.

    k = px per master unit; `mono` scales the monogram relative to the type.
    `lines` = [(key, scale, gap_after, opacity)]. Returns (width, height) in px.
    """
    lines = lines or [("wordmark", 1.0, 120, 1.0), ("founders-club", 1.0, 0, 0.82)]
    mono_w, mono_h = size("monogram", mono)
    block_h = sum(size(k, m)[1] + g for k, m, g, _ in lines) - lines[-1][2]
    block_w = max(size(k, m)[0] for k, m, _, _ in lines)
    total_w = mono_w + gap + block_w
    left = {"start": 0, "middle": -total_w / 2, "end": -total_w}[anchor]
    parts = [_piece("monogram", mono, left, -mono_h / 2, anchor="start", fill=fill)[0]]
    y = -block_h / 2
    for key, m, g, op in lines:
        svg, _, h = _piece(key, m, left + mono_w + gap, y, anchor="start", fill=fill, opacity=op)
        parts.append(svg)
        y += h + g
    c.add(f'<g transform="translate({f(x)} {f(cy)}) scale({k:.6f})">{"".join(parts)}</g>')
    return total_w * k, max(mono_h, block_h) * k


def place(c, key, x, y, height=None, width=None, anchor="middle", fill=IVORY, opacity=1.0):
    """Single element (or the cities line) at an absolute px size; y is the vertical centre."""
    w0, h0 = size(key)
    m = height / h0 if height else width / w0
    svg, w, h = _piece(key, m, x, y - h0 * m / 2, anchor=anchor, fill=fill, opacity=opacity)
    c.add(svg)
    return w, h
