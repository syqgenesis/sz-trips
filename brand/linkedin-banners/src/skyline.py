"""Vector skylines: San Francisco with the Bay Bridge, and Shenzhen.

Landmarks are drawn from simple geometry (Transamerica Pyramid, Salesforce Tower,
181 Fremont, Bay Bridge western span; Ping An Finance Centre, China Resources
"Spring Bamboo", Kingkey 100). Everything else is a seeded procedural fill.
All sizes are in scene units scaled by c.s so both banner formats match.
"""

import math

from canvas import f


class Compound:
    """Collects shapes into one compound path, so a layer is a single editable object."""

    def __init__(self):
        self.parts = []

    def poly(self, pts):
        self.parts.append("M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z")

    def rect(self, x, y, w, h):
        self.parts.append(f"M{f(x)} {f(y)}h{f(w)}v{f(h)}h{f(-w)}Z")

    def line(self, x0, y0, x1, y1):
        self.parts.append(f"M{f(x0)} {f(y0)}L{f(x1)} {f(y1)}")

    @property
    def d(self):
        return "".join(self.parts)


class Building:
    """Outline polygons plus the rectangles where windows may sit.

    `edges` = (y where the left wall starts, y where the right wall starts), used
    for rim lighting; None for tapered landmarks that have no straight wall.
    """

    def __init__(self, polys, bodies, x0, x1, top, edges=None):
        self.polys, self.bodies, self.x0, self.x1, self.top = polys, bodies, x0, x1, top
        self.edges = edges


# ------------------------------------------------------------- generic fill

def generic(x, w, h, b, s, rng):
    kind = rng.choices(["flat", "step", "slant", "spire", "crown"], [40, 22, 14, 14, 10])[0]
    t = b - h
    if kind == "step":
        polys = [[(x, b), (x, t + 0.14 * h), (x + 0.18 * w, t + 0.14 * h), (x + 0.18 * w, t),
                  (x + 0.82 * w, t), (x + 0.82 * w, t + 0.14 * h), (x + w, t + 0.14 * h), (x + w, b)]]
        bodies = [(x, x + w, t + 0.14 * h + 3 * s, b)]
        edges = (t + 0.14 * h, t + 0.14 * h)
    elif kind == "slant":
        lo = rng.uniform(0.06, 0.14) * h
        if rng.random() < 0.5:
            pts, edges = [(x, b), (x, t + lo), (x + w, t), (x + w, b)], (t + lo, t)
        else:
            pts, edges = [(x, b), (x, t), (x + w, t + lo), (x + w, b)], (t, t + lo)
        polys, bodies = [pts], [(x, x + w, t + lo + 3 * s, b)]
    else:
        polys, bodies = [[(x, b), (x, t), (x + w, t), (x + w, b)]], [(x, x + w, t + 3 * s, b)]
        edges = (t, t)
        if kind == "spire":
            sh = rng.uniform(8, 18) * s
            polys.append([(x + w / 2 - 0.5 * s, t), (x + w / 2, t - sh), (x + w / 2 + 0.5 * s, t)])
        elif kind == "crown":
            polys.append([(x + 0.3 * w, t), (x + 0.3 * w, t - 4 * s), (x + 0.7 * w, t - 4 * s), (x + 0.7 * w, t)])
    return Building(polys, bodies, x, x + w, t, edges)


def fill_row(x0, x1, b, s, rng, hmin, hmax, wmin, wmax, envelope=None, gap=(0.0, 1.5)):
    """Tile [x0, x1] with generic towers; `envelope(x)` scales heights (0..1)."""
    out, x = [], x0
    while x < x1:
        w = rng.uniform(wmin, wmax) * s
        e = envelope(x) if envelope else 1.0
        h = (hmin + (hmax - hmin) * rng.random() ** 1.3) * s * e
        if h > 6 * s:
            out.append(generic(x, w, h, b, s, rng))
        x += w + rng.uniform(*gap) * s
    return out


# ---------------------------------------------------------------- landmarks

def transamerica(cx, b, s, h=150):
    h *= s
    t = b - h
    body = [(cx - 11 * s, b), (cx - 1.4 * s, t), (cx + 1.4 * s, t), (cx + 11 * s, b)]
    wy0, wy1 = b - 0.84 * h, b - 0.70 * h
    wings = [(cx - 5.6 * s, wy1), (cx - 5.6 * s, wy0), (cx + 5.6 * s, wy0), (cx + 5.6 * s, wy1)]
    spire = [(cx - 0.9 * s, t), (cx, t - 24 * s), (cx + 0.9 * s, t)]
    bodies = [(cx - (11 - 9.6 * k) * s + 1.5 * s, cx + (11 - 9.6 * k) * s - 1.5 * s,
               b - (k + 0.1) * h, b - k * h) for k in [i / 10 for i in range(7)]]
    return Building([body, wings, spire], bodies, cx - 11 * s, cx + 11 * s, t - 24 * s)


def salesforce(cx, b, s, h=205):
    h *= s
    crown = 18 * s
    t = b - h
    pts = [(cx - 13 * s, b), (cx - 11 * s, t + crown)]
    for i in range(1, 12):
        a = math.pi * (1 - i / 12)
        pts.append((cx + 11 * s * math.cos(a), t + crown - crown * math.sin(a) ** 0.6))
    pts += [(cx + 11 * s, t + crown), (cx + 13 * s, b)]
    return Building([pts], [(cx - 11 * s, cx + 11 * s, t + crown + 4 * s, b)], cx - 13 * s, cx + 13 * s, t)


def fremont181(cx, b, s, h=168):
    h *= s
    t = b - h
    body = [(cx - 7 * s, b), (cx - 7 * s, t + 18 * s), (cx + 7 * s, t), (cx + 7 * s, b)]
    spire = [(cx + 5.6 * s, t + 2 * s), (cx + 6.3 * s, t - 30 * s), (cx + 7 * s, t)]
    return Building([body, spire], [(cx - 7 * s, cx + 7 * s, t + 20 * s, b)], cx - 7 * s, cx + 7 * s, t - 30 * s)


def pingan(cx, b, s, h=250):
    h *= s
    t = b - h
    pts = [(cx - 18 * s, b), (cx - 15 * s, b - 0.8 * h), (cx - 12.5 * s, b - 0.88 * h), (cx - 8 * s, b - 0.95 * h),
           (cx - 2.4 * s, t), (cx - 0.7 * s, t), (cx, t - 34 * s), (cx + 0.7 * s, t), (cx + 2.4 * s, t),
           (cx + 8 * s, b - 0.95 * h), (cx + 12.5 * s, b - 0.88 * h), (cx + 15 * s, b - 0.8 * h), (cx + 18 * s, b)]
    bodies = [(cx - 15 * s, cx + 15 * s, b - 0.8 * h + 3 * s, b)]
    return Building([pts], bodies, cx - 18 * s, cx + 18 * s, t - 34 * s)


def bamboo(cx, b, s, h=188):
    h *= s
    t = b - h
    pts = [(cx - 13 * s, b), (cx - 11 * s, b - 0.78 * h)]
    for i in range(1, 12):
        k = i / 12
        pts.append((cx - 11 * s * math.sqrt(1 - k), b - 0.78 * h - 0.22 * h * k))
    pts.append((cx, t - 6 * s))
    for i in range(11, 0, -1):
        k = i / 12
        pts.append((cx + 11 * s * math.sqrt(1 - k), b - 0.78 * h - 0.22 * h * k))
    pts += [(cx + 11 * s, b - 0.78 * h), (cx + 13 * s, b)]
    return Building([pts], [(cx - 11 * s, cx + 11 * s, b - 0.78 * h + 3 * s, b)], cx - 13 * s, cx + 13 * s, t - 6 * s)


def kingkey(cx, b, s, h=205):
    h *= s
    t = b - h
    pts = [(cx - 15 * s, b), (cx - 15 * s, t + 16 * s)]
    for i in range(1, 10):
        k = i / 10
        pts.append((cx - 15 * s + 30 * s * k, t + 16 * s - 16 * s * math.sin(math.pi * k)))
    pts += [(cx + 15 * s, t + 16 * s), (cx + 15 * s, b)]
    return Building([pts], [(cx - 15 * s, cx + 15 * s, t + 18 * s, b)], cx - 15 * s, cx + 15 * s, t)


# ------------------------------------------------------------------ drawing

def draw_layer(c, buildings, *, fill, b, s, rng, lights=None, lit=0.3, win_op=1.0,
               rim=None, rim_side="right", reflect=None):
    """Silhouettes as one compound path, windows bucketed by colour/opacity."""
    sil = Compound()
    for bd in buildings:
        for p in bd.polys:
            sil.poly(p)
    c.add(f'<path d="{sil.d}" fill="{fill}"/>')
    if reflect:
        c.add(f'<path d="{sil.d}" fill="{reflect}" transform="matrix(1 0 0 -1 0 {f(2 * b)})"/>')
    if rim:
        edge = Compound()
        for bd in buildings:
            if bd.edges and rng.random() < 0.55:
                x, y = (bd.x1, bd.edges[1]) if rim_side == "right" else (bd.x0, bd.edges[0])
                edge.line(x, y + 1 * s, x, b)
        c.add(f'<path d="{edge.d}" fill="none" stroke="{rim}" stroke-width="{f(0.8 * s)}"/>')
    if not lights:
        return []
    ww, wh, px, py = 1.8 * s, 1.5 * s, 4.2 * s, 4.6 * s
    ww, wh = max(ww, 0.9), max(wh, 0.8)
    buckets, streaks = {}, []
    for bd in buildings:
        dense = rng.uniform(0.4, 1.3) * lit
        for (x0, x1, y0, y1) in bd.bodies:
            cols = int((x1 - x0 - 1.4 * s) // px)
            rows = int((y1 - y0 - 2 * s) // py)
            if cols < 1 or rows < 1:
                continue
            ox = x0 + (x1 - x0 - (cols - 1) * px - ww) / 2
            colour = rng.choice(lights)
            for r in range(rows):
                band = rng.random() < 0.15  # whole floors lit or dark read as real
                for q in range(cols):
                    p = dense * (2.2 if band else 1.0)
                    if rng.random() < p:
                        op = rng.choice([0.3, 0.5, 0.75, 1.0])
                        if rng.random() < 0.18:
                            colour_w = rng.choice(lights)
                        else:
                            colour_w = colour
                        x, y = ox + q * px, y0 + 2 * s + r * py
                        buckets.setdefault((colour_w, op), Compound()).rect(x, y, ww, wh)
                        if y > b - 0.35 * (b - bd.top) and rng.random() < 0.25:
                            streaks.append((x, colour_w, op))
    for (col, op), comp in sorted(buckets.items()):
        c.add(f'<path d="{comp.d}" fill="{col}" opacity="{f(op * win_op)}"/>')
    return streaks


def water_streaks(c, streaks, b, s, rng, depth, op=0.4):
    """Window lights smeared down into the water."""
    by_col = {}
    for x, col, o in streaks:
        length = rng.uniform(0.25, 1.0) * depth
        by_col.setdefault(col, Compound()).rect(x, b + rng.uniform(0.5, 3) * s, max(1.8 * s, 0.9), length)
    for col, comp in by_col.items():
        paint = c.lin(0, b, 0, b + depth, [(0, col, op), (0.5, col, op * 0.35), (1, col, 0)])
        c.add(f'<path d="{comp.d}" fill="{paint}"/>')


def bay_bridge(c, x0, x1, towers, b, s, *, deck=28, tower_h=118, steel="#1A2C66",
               cable="#B9CCF2", led="#E6F0FF", fade_to=None):
    """Bay Bridge western span: X-braced towers, catenary cables, lit suspenders.

    fade_to=(xa, xb) fades the whole structure out between those x positions.
    """
    yd = b - deck * s
    top = b - tower_h * s

    def paint(col, op=1.0):
        if not fade_to:
            return col, op
        xa, xb = fade_to
        return c.lin(xa, 0, xb, 0, [(0, col, op), (1, col, 0)]), 1.0

    steel_p, _ = paint(steel)
    cable_p, _ = paint(cable, 0.85)
    led_p, _ = paint(led, 1.0)
    struct = Compound()
    # Deck and piers.
    struct.rect(x0, yd, x1 - x0, 2.6 * s)
    for tx in towers:
        struct.rect(tx - 7 * s, yd, 14 * s, b - yd)
    # Towers: two legs with X bracing.
    brace = Compound()
    for tx in towers:
        for side in (-1, 1):
            lx = tx + side * 4.6 * s
            struct.poly([(lx - 1.3 * s, b), (lx - 1.0 * s, top), (lx + 1.0 * s, top), (lx + 1.3 * s, b)])
        struct.rect(tx - 5.6 * s, top - 1.5 * s, 11.2 * s, 2.6 * s)
        panels = 4
        for i in range(panels):
            ya = top + (yd - top) * i / panels + 2 * s
            yb = top + (yd - top) * (i + 1) / panels
            brace.line(tx - 4.6 * s, ya, tx + 4.6 * s, yb)
            brace.line(tx + 4.6 * s, ya, tx - 4.6 * s, yb)
            brace.line(tx - 4.6 * s, yb, tx + 4.6 * s, yb)
    c.add(f'<path d="{struct.d}" fill="{steel_p}"/>')
    c.add(f'<path d="{brace.d}" fill="none" stroke="{steel_p}" stroke-width="{f(0.9 * s)}"/>')
    # Main cables between anchor points and tower tops, with suspenders.
    anchors = [(x0, yd - 2 * s)] + [(tx, top) for tx in towers] + [(x1, yd - 2 * s)]
    cab, sus = Compound(), Compound()
    for (ax, ay), (bx, by) in zip(anchors, anchors[1:]):
        mx = (ax + bx) / 2
        # Main spans dip to just above the deck; side spans sag gently to the anchorage.
        my = 2 * (yd - 3 * s) - top if ay == by else yd - 6 * s
        cab.parts.append(f"M{f(ax)} {f(ay)}Q{f(mx)} {f(my)} {f(bx)} {f(by)}")
        n = int(abs(bx - ax) / (3.4 * s))
        for i in range(1, n):
            t = i / n
            x = (1 - t) ** 2 * ax + 2 * (1 - t) * t * mx + t * t * bx
            y = (1 - t) ** 2 * ay + 2 * (1 - t) * t * my + t * t * by
            if y < yd - 1.5 * s:
                sus.line(x, y, x, yd)
    c.add(f'<path d="{sus.d}" fill="none" stroke="{led_p}" stroke-width="{f(max(0.55 * s, 0.45))}" opacity="0.55"/>')
    c.add(f'<path d="{cab.d}" fill="none" stroke="{cable_p}" stroke-width="{f(1.2 * s)}"/>')
    # Deck lights.
    dots = Compound()
    x = x0
    while x < x1:
        dots.rect(x, yd + 0.6 * s, 1.4 * s, 1.2 * s)
        x += 5.5 * s
    c.add(f'<path d="{dots.d}" fill="{paint("#FFE2AE")[0]}" opacity="0.9"/>')
    # Tower beacons.
    for tx in towers:
        c.add(f'<circle cx="{f(tx)}" cy="{f(top - 2 * s)}" r="{f(1.2 * s)}" fill="#FF5A4E" opacity="0.85"/>')
    return sus.d
