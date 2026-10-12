"""Build the Delta & Bay LinkedIn banners as self-contained SVGs.

    python3 src/build.py            # writes svg/profile/*.svg and svg/company/*.svg

Two LinkedIn formats, same seven designs:
  profile  1584 x 396  personal profile background (photo covers the bottom-left)
  company  1128 x 191  company page cover (logo box covers the bottom-left)
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from brand import IVORY, NAVY  # noqa: E402
from canvas import Canvas, f, horizontal, place, stacked  # noqa: E402
import pacific  # noqa: E402
import photos  # noqa: E402
import skyline as sk  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

FORMATS = {
    "profile": (1584, 396),
    "company": (1128, 191),
}

# Type scale (px per master-logo unit) per format: wordmark cap height ~30px / ~17px.
K = {"profile": 0.145, "company": 0.083}
K_STACK = {"profile": 0.145, "company": 0.075}

BLUE = "#2F6BFF"
BLUE_DEEP = "#1638B8"
BLUE_SOFT = "#5C9BFF"
ICE = "#D8E9FF"

FULL_STACK = [("monogram", 0.62, 150, 1), ("wordmark", 1, 120, 1),
              ("founders-club", 1, 170, 0.85), ("cities", 1, 0, 0.7)]


def base(c, top=NAVY, bottom="#07113F"):
    c.rect(c.lin(0, 0, 0, c.H, [(0, top), (1, bottom)]))


def halo(c, cx, cy, rx, ry, color=NAVY, op=0.6):
    """Soft dark pool behind type so it stays legible over busy art."""
    c.add(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" '
          f'fill="{c.rad(cx, cy, rx, [(0, color, op), (0.55, color, op * 0.6), (1, color, 0)], sy=ry / rx)}"/>')


def bloom(c, cx, cy, r, color=BLUE, op=0.5, sy=1.0, rot=0.0):
    c.add(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(r)}" ry="{f(r * sy)}" '
          f'transform="rotate({f(rot)} {f(cx)} {f(cy)})" '
          f'fill="{c.rad(cx, cy, r, [(0, color, op), (0.4, color, op * 0.45), (1, color, 0)], sy=sy)}"/>')


def cubic(p):
    return (f"M{f(p[0][0])} {f(p[0][1])}C{f(p[1][0])} {f(p[1][1])} "
            f"{f(p[2][0])} {f(p[2][1])} {f(p[3][0])} {f(p[3][1])}")


def ribbon(c, a, b, *, n=34, color=BLUE_SOFT, fade, op=0.55, width=0.75, twist=(0, 0)):
    """A silk ribbon: n fine strands interpolated between cubic edges a and b.

    Strands bunch toward edge `a` (the lit crest) and fade toward `b`.
    """
    paint = c.lin(*fade[:4], [(o, color, al) for o, al in fade[4]])
    strands = []
    for i in range(n):
        t = i / (n - 1)
        bend = math.sin(math.pi * t)
        pts = []
        for j, (pa, pb) in enumerate(zip(a, b)):
            x = pa[0] + (pb[0] - pa[0]) * t
            y = pa[1] + (pb[1] - pa[1]) * t
            if j in (1, 2):
                x += twist[0] * bend * (1 if j == 1 else -1)
                y += twist[1] * bend * (1 if j == 1 else -1)
            pts.append((x, y))
        strength = op * (0.18 + 0.82 * (1 - t) ** 2.2)
        strands.append(f'<path d="{cubic(pts)}" stroke-opacity="{f(strength)}"/>')
    c.add(f'<g fill="none" stroke="{paint}" stroke-width="{f(width * c.s)}">{"".join(strands)}</g>')


# ------------------------------------------------------------------ designs

def d02_light_sweep(c, fmt):
    """Curved sheet of light falling across the right; lockup on the left."""
    W, H, s = c.W, c.H, c.s
    base(c, NAVY, "#060C36")
    trough = (0.71 * W, 0.76 * H)
    edge = [(0.53 * W, -0.06 * H), (0.62 * W, 0.34 * H), (0.63 * W, trough[1]), trough]
    rise = [trough, (0.79 * W, 0.76 * H), (0.88 * W, 0.40 * H), (1.03 * W, 0.02 * H)]
    sheet = (f"{cubic(edge)}C{f(rise[1][0])} {f(rise[1][1])} {f(rise[2][0])} {f(rise[2][1])} "
             f"{f(rise[3][0])} {f(rise[3][1])}L{f(1.03 * W)} {f(-0.1 * H)}Z")
    # Lit sheet above the curve, brightest just over the trough.
    c.add(f'<path d="{sheet}" fill="{c.rad(trough[0], trough[1], 0.42 * W, [(0, "#1E56E8", 0.75), (0.35, "#123AA8", 0.5), (1, "#0A1A5C", 0.15)], sy=0.9)}"/>')
    c.add(f'<path d="{sheet}" fill="{c.lin(0.53 * W, 0, W, 0, [(0, NAVY, 0.85), (0.3, NAVY, 0), (1, NAVY, 0)])}"/>')
    # Strands inside the sheet give it a silk texture.
    ribbon(c, edge, [(0.68 * W, -0.1 * H), (0.74 * W, 0.20 * H), (0.76 * W, 0.48 * H), (0.82 * W, 0.54 * H)],
           n=26, color=BLUE_SOFT, op=0.35, width=0.6,
           fade=(0.53 * W, 0, 0.82 * W, 0, [(0, 0), (0.45, 0.6), (0.85, 1), (1, 0.7)]))
    ribbon(c, rise, [(0.82 * W, 0.54 * H), (0.87 * W, 0.46 * H), (0.94 * W, 0.22 * H), (1.03 * W, -0.08 * H)],
           n=20, color=BLUE_SOFT, op=0.3, width=0.6,
           fade=(0.71 * W, 0, 1.03 * W, 0, [(0, 1), (0.6, 0.6), (1, 0.15)]))
    path = (f"{cubic(edge)}C{f(rise[1][0])} {f(rise[1][1])} {f(rise[2][0])} {f(rise[2][1])} "
            f"{f(rise[3][0])} {f(rise[3][1])}")
    c.glow(path, width=1.5, strength=1.0,
           fade=(0.53 * W, 0, 1.03 * W, 0, [(0, 0), (0.25, 0.35), (0.45, 1), (0.7, 0.9), (1, 0.25)]))
    bloom(c, trough[0] + 0.02 * W, trough[1], 0.12 * W, "#7FB4FF", 0.35, sy=0.35)

    k = K[fmt]
    if fmt == "profile":
        horizontal(c, 0.19 * W, 0.42 * H, k * 1.12, mono=0.62, gap=260)
        place(c, "cities", 0.955 * W, 0.895 * H, height=12.9 * s, anchor="end", opacity=0.8)
    else:
        horizontal(c, 0.165 * W, 0.44 * H, k * 1.15, mono=0.62, gap=260)
        place(c, "cities", 0.965 * W, 0.875 * H, height=8.2, anchor="end", opacity=0.8)


def d03_pacific_route(c, fmt):
    """Night map of the Pacific: the route arcs from San Francisco to Shenzhen over the lockup."""
    W, H, s = c.W, c.H, c.s
    c.rect(c.lin(0, 0, 0, H, [(0, "#040826"), (0.5, NAVY), (1, "#060C38")]))
    bloom(c, 0.5 * W, 0.55 * H, 0.42 * W, "#0E2A86", 0.45, sy=0.7)
    if fmt == "profile":
        sz, sf_x = (0.245 * W, 0.565 * H), 0.80 * W
    else:
        sz, sf_x = (0.205 * W, 0.70 * H), 0.80 * W
    proj = pacific.Projection(sz, sf_x)
    pacific.draw(c, proj, land_fill=c.lin(0, 0, 0, H, [(0, "#17307A"), (1, "#0F2262")]))
    sf = proj(*pacific.SF)

    # Route arc, peaking above the lockup.
    peak = -0.30 * H if fmt == "profile" else -0.34 * H
    route = f"M{f(sz[0])} {f(sz[1])}Q{f((sz[0] + sf[0]) / 2)} {f(peak)} {f(sf[0])} {f(sf[1])}"
    c.glow(route, width=1.3, strength=0.95, tint="#4DA3FF", core="#E6F4FF",
           fade=(sz[0], 0, sf[0], 0, [(0, 1), (0.5, 0.7), (1, 1)]))
    for (x, y) in (sz, sf):
        bloom(c, x, y, 26 * s, "#5CB0FF", 0.75)
        c.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(5.5 * s)}" fill="none" stroke="{ICE}" '
              f'stroke-opacity="0.55" stroke-width="{f(max(0.6, 0.8 * s))}"/>')
        c.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(2.3 * s)}" fill="#FFFFFF"/>')
    lab_h = (11 if fmt == "profile" else 8.6) * (s if fmt == "profile" else 1)
    place(c, "shenzhen", sz[0] + 11 * s, sz[1] + 13 * s, height=lab_h, anchor="start", opacity=0.9)
    place(c, "san-francisco", sf[0] - 11 * s, sf[1] + 13 * s, height=lab_h, anchor="end", opacity=0.9)

    halo(c, 0.5 * W, 0.53 * H, 0.16 * W, 0.40 * H, NAVY, 0.6)
    rows = [("monogram", 0.62, 150, 1), ("wordmark", 1, 120, 1), ("founders-club", 1, 170, 0.85),
            ("bridging-frontiers", 0.9, 0, 0.62)]
    stacked(c, 0.5 * W, 0.53 * H, K_STACK[fmt], rows)


def d05_horizon(c, fmt):
    """A planet's lit rim rising from the bottom-left; lockup and tagline to the right."""
    W, H, s = c.W, c.H, c.s
    base(c, NAVY, "#050B33")
    bloom(c, 0.62 * W, 0.5 * H, 0.55 * W, "#0E2A8A", 0.35, sy=0.6)
    R = 2.6 * H
    cx, cy = (0.30 * W - R * 0.80, 1.05 * H + R * 0.55) if fmt == "profile" else (0.27 * W - R * 0.80, 1.05 * H + R * 0.55)
    # Atmosphere just outside the rim, then the dark body, then the lit edge.
    c.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(R * 1.14)}" '
          f'fill="{c.rad(cx, cy, R * 1.14, [(0, BLUE, 0), (0.86, BLUE, 0), (0.877, "#3D7BFF", 0.55), (0.91, BLUE, 0.16), (0.96, BLUE_DEEP, 0.05), (1, BLUE_DEEP, 0)])}"/>')
    c.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(R)}" '
          f'fill="{c.rad(cx, cy, R, [(0, "#03072A"), (0.88, "#050C3A"), (0.965, "#0B1F72"), (0.992, "#1D4FE0"), (1, "#6FA8FF")])}"/>')
    # Rim: the arc of the circle that crosses the canvas.
    a0, a1 = math.radians(-100), math.radians(-12)
    pts = [(cx + R * math.cos(a0 + (a1 - a0) * i / 60), cy + R * math.sin(a0 + (a1 - a0) * i / 60)) for i in range(61)]
    d = "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts)
    xs = [p[0] for p in pts if -0.1 * H < p[1] < 1.1 * H]
    c.glow(d, width=1.4, strength=1.0,
           fade=(0, 0, 0, H, [(0, 1), (0.45, 0.85), (0.8, 0.35), (1, 0.12)]))
    bloom(c, min(xs) + 0.04 * W, 0.02 * H, 0.16 * W, "#6FA8FF", 0.4, sy=0.55)

    zone = (0.36 * W, 0.97 * W) if fmt == "profile" else (0.33 * W, 0.975 * W)
    kk, cy0 = K[fmt] * 1.1, 0.47 * H
    pad = 46 * s * (1.0 if fmt == "profile" else 1.4)
    right = [("bridging-frontiers", 1, 170, 0.92), ("cities", 1, 0, 0.7)]

    def widths(kk):
        dry = Canvas(W, H)
        return horizontal(dry, 0, 0, kk, mono=0.62, gap=260)[0], stacked(dry, 0, 0, kk * 0.82, right, align="start")[0]

    w1, w2 = widths(kk)
    room = (zone[1] - zone[0]) * 0.94
    if w1 + w2 + 2 * pad > room:
        kk *= (room - 2 * pad) / (w1 + w2)
        w1, w2 = widths(kk)
    x0 = (zone[0] + zone[1]) / 2 - (w1 + w2 + 2 * pad) / 2
    _, h = horizontal(c, x0, cy0, kk, mono=0.62, gap=260)
    div_x = x0 + w1 + pad
    c.add(f'<rect x="{f(div_x)}" y="{f(cy0 - h * 0.48)}" width="{f(max(1, 1.1 * s))}" height="{f(h * 0.96)}" '
          f'fill="{IVORY}" opacity="0.35"/>')
    stacked(c, div_x + pad, cy0, kk * 0.82, right, align="start")


def d06_silk(c, fmt):
    """Ribbons of light crossing behind a centred lockup."""
    W, H = c.W, c.H
    base(c, NAVY, "#060D3A")
    bloom(c, 0.22 * W, 0.62 * H, 0.32 * W, "#1A45D0", 0.42, sy=0.6, rot=-12)
    bloom(c, 0.80 * W, 0.38 * H, 0.30 * W, "#1A4FE0", 0.38, sy=0.55, rot=8)
    # Left ribbon rises from bottom-left towards the centre.
    la = [(-0.05 * W, 0.92 * H), (0.12 * W, 0.70 * H), (0.26 * W, 0.18 * H), (0.47 * W, 0.30 * H)]
    lb = [(-0.05 * W, 0.62 * H), (0.14 * W, 0.40 * H), (0.30 * W, 0.08 * H), (0.47 * W, 0.20 * H)]
    fade_l = (-0.05 * W, 0, 0.47 * W, 0, [(0, 0.1), (0.35, 0.9), (0.7, 1), (1, 0)])
    ribbon(c, la, lb, n=40, color="#6FA8FF", op=0.5, fade=fade_l, twist=(0, -0.10 * H))
    c.glow(cubic(la), width=1.2, strength=0.9, fade=fade_l)
    # Right ribbon: a long wave from the top-centre out to the right edge.
    ra = [(0.53 * W, 0.12 * H), (0.70 * W, 0.02 * H), (0.80 * W, 0.80 * H), (1.05 * W, 0.42 * H)]
    rb = [(0.53 * W, 0.24 * H), (0.70 * W, 0.20 * H), (0.82 * W, 1.0 * H), (1.05 * W, 0.70 * H)]
    fade_r = (0.53 * W, 0, 1.05 * W, 0, [(0, 0), (0.3, 0.7), (0.65, 1), (1, 0.4)])
    ribbon(c, ra, rb, n=40, color="#6FA8FF", op=0.5, fade=fade_r, twist=(0, 0.08 * H))
    c.glow(cubic(ra), width=1.2, strength=0.9, fade=fade_r)
    # A faint counter-strand for depth.
    c.glow(cubic([(0.02 * W, 0.98 * H), (0.30 * W, 0.70 * H), (0.70 * W, 1.02 * H), (1.02 * W, 0.86 * H)]),
           width=0.9, strength=0.35, fade=(0, 0, W, 0, [(0, 0), (0.3, 0.8), (0.5, 0.2), (0.75, 0.8), (1, 0)]))
    halo(c, 0.5 * W, 0.5 * H, 0.2 * W, 0.46 * H, NAVY, 0.55)
    stacked(c, 0.5 * W, 0.5 * H, K_STACK[fmt], FULL_STACK if fmt == "profile" else COMPANY_STACK)


def d07_monogram_glow(c, fmt):
    """The monogram as a giant lit watermark; type set left, route on the right."""
    W, H, s = c.W, c.H, c.s
    c.rect(c.lin(0, 0, W, 0, [(0, "#1550F0"), (0.16, "#0D35B8"), (0.42, "#081A6A"), (0.7, NAVY), (1, NAVY)]))
    c.rect(c.lin(0, 0, 0, H, [(0, NAVY, 0.0), (1, NAVY, 0.35)]))
    bloom(c, 0.05 * W, 0.80 * H, 0.30 * W, "#3D8BFF", 0.55, sy=0.9)
    mono_h = 1.5 * H if fmt == "profile" else 1.62 * H
    mono_x = 0.135 * W if fmt == "profile" else 0.125 * W
    paint = c.lin(0, 0, mono_x + mono_h * 0.5, H, [(0, "#B4D7FF", 0.62), (0.55, "#6AA2FF", 0.42), (1, "#3A6FF0", 0.2)])
    place(c, "monogram", mono_x, 0.60 * H, height=mono_h, fill=paint)
    k = K[fmt]
    rows = [("wordmark", 1, 140, 1), ("founders-club", 1, 230, 0.85), ("bridging-frontiers", 0.92, 0, 0.6)]
    if fmt == "profile":
        stacked(c, 0.33 * W, 0.47 * H, k * 1.12, rows, align="start")
        place(c, "cities", 0.955 * W, 0.50 * H, height=12.3 * s * 1.05, anchor="end", opacity=0.8)
    else:
        stacked(c, 0.31 * W, 0.47 * H, k * 1.15, rows, align="start")
        place(c, "cities", 0.965 * W, 0.50 * H, height=8.2, anchor="end", opacity=0.8)


def ridge(c, x0, x1, b, s, rng, hmin, hmax, fill, step=6):
    """Smooth mountain silhouette from summed sines."""
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    pts, x = [(x0, b)], x0
    while x <= x1:
        u = (x - x0) / (x1 - x0)
        n = 0.5 + 0.28 * math.sin(u * 7 + ph[0]) + 0.14 * math.sin(u * 17 + ph[1]) + 0.06 * math.sin(u * 41 + ph[2])
        taper = min(1, u * 4, (1 - u) * 6 + 0.4)
        pts.append((x, b - (hmin + (hmax - hmin) * n) * s * taper))
        x += step * s
    pts.append((x1, b))
    c.add(f'<path d="M{"L".join(f"{f(px)} {f(py)}" for px, py in pts)}Z" fill="{fill}"/>')


def shimmer(c, b, s, rng, x0, x1, colours, n, op=(0.06, 0.3), depth=None):
    depth = depth or (c.H - b)
    for col in colours:
        comp = sk.Compound()
        for _ in range(n):
            y = b + (rng.random() ** 1.6) * depth
            x = rng.uniform(x0, x1)
            comp.rect(x, y, rng.uniform(4, 26) * s, max(0.5, 0.6 * s))
        c.add(f'<path d="{comp.d}" fill="{col}" opacity="{f(rng.uniform(*op))}"/>')


def twin_skylines(c, fmt, mood):
    """San Francisco (left, with the Bay Bridge) facing Shenzhen (right) across the water."""
    W, H, s = c.W, c.H, c.s
    rng = random.Random(f"{mood}-{fmt}")
    b = 0.80 * H
    night = mood == "night"
    # Sky.
    if night:
        c.rect(c.lin(0, 0, 0, b, [(0, NAVY), (0.45, "#0A1850"), (0.78, "#16317C"), (1, "#2B4FA4")]))
    else:
        c.rect(c.lin(0, 0, 0, b, [(0, NAVY), (0.35, "#12245F"), (0.7, "#2C3F86"), (1, "#5A64A8")]))
        bloom(c, 0.27 * W, b, 0.46 * W, "#FFB06E", 0.95, sy=0.5)
        bloom(c, 0.30 * W, b, 0.20 * W, "#FFD39A", 0.75, sy=0.42)
        bloom(c, 0.82 * W, b, 0.32 * W, "#3F6FE0", 0.45, sy=0.45)
        # Thin evening cloud bands catching the light.
        for y, x0, x1, op in [(0.50, 0.05, 0.42, 0.22), (0.56, 0.16, 0.50, 0.16)]:
            cx, w = (x0 + x1) / 2 * W, (x1 - x0) * W
            c.add(f'<ellipse cx="{f(cx)}" cy="{f(y * H)}" rx="{f(w / 2)}" ry="{f(2.2 * s)}" '
                  f'fill="{c.lin(cx - w / 2, 0, cx + w / 2, 0, [(0, "#FFC890", 0), (0.4, "#FFC890", op), (1, "#FFC890", 0)])}"/>')
    if night:
        stars = sk.Compound()
        for _ in range(int(70 * W / 1584)):
            x, y = rng.uniform(0, W), rng.uniform(0, 0.42 * H) ** 1.0
            r = rng.uniform(0.4, 1.0) * max(s, 0.7)
            stars.rect(x, y, r, r)
        c.add(f'<path d="{stars.d}" fill="{ICE}" opacity="0.45"/>')
        bloom(c, 0.5 * W, b, 0.34 * W, "#4A78E8", 0.40, sy=0.45)
    # Distant hills behind each city.
    hill = "#16296A" if night else "#3B3F7C"
    ridge(c, 0.56 * W, 1.02 * W, b, s, rng, 18, 64, hill)
    ridge(c, -0.02 * W, 0.24 * W, b, s, rng, 8, 30, hill)

    sf_env = lambda x: 0.35 + 0.65 * max(0.0, 1 - abs(x / W - 0.13) / 0.14)  # noqa: E731
    sz_env = lambda x: 0.3 + 0.7 * min(1.0, max(0.0, (x / W - 0.63) / 0.10))  # noqa: E731
    back_col = "#1E3478" if night else "#343A74"
    mid_col = "#0A1645" if night else "#1A1D52"
    front_col = "#060D30" if night else "#0C0E33"
    warm = ["#FFD9A3", "#FFE9C8", "#F6B86C"]
    cool = ["#CFE5FF", "#9CC5FF", "#FFE3B8", "#E8F2FF"]
    win_op = 0.95 if night else 0.75

    # Back layer.
    back = sk.fill_row(-0.01 * W, 0.26 * W, b, s, rng, 14, 70, 9, 22, sf_env) + \
        sk.fill_row(0.635 * W, 1.01 * W, b, s, rng, 30, 120, 10, 22, sz_env)
    sk.draw_layer(c, back, fill=back_col, b=b, s=s, rng=rng, lights=cool, lit=0.08, win_op=0.45 * win_op)

    # Mid layer with landmarks.
    sf_marks = [sk.transamerica(0.075 * W, b, s), sk.salesforce(0.165 * W, b, s), sk.fremont181(0.195 * W, b, s)]
    sz_marks = [sk.kingkey(0.705 * W, b, s), sk.pingan(0.80 * W, b, s), sk.bamboo(0.875 * W, b, s)]
    marks = sf_marks + sz_marks

    def clear(bd):
        return all(bd.x1 < m.x0 - 1.5 * s or bd.x0 > m.x1 + 1.5 * s for m in marks)

    mid = [bd for bd in sk.fill_row(-0.01 * W, 0.235 * W, b, s, rng, 26, 112, 10, 24, sf_env) if clear(bd)] + \
          [bd for bd in sk.fill_row(0.645 * W, 1.01 * W, b, s, rng, 40, 165, 11, 26, sz_env) if clear(bd)]
    reflect = c.lin(0, b, 0, b - 0.2 * H, [(0, mid_col, 0.85), (1, mid_col, 0)])
    sk.draw_layer(c, mid + marks, fill=mid_col, b=b, s=s, rng=rng, lights=None, reflect=reflect)
    sf_lit = sk.draw_layer(c, [bd for bd in mid + marks if bd.x1 < 0.5 * W], fill="none", b=b, s=s, rng=rng,
                           lights=warm, lit=0.30, win_op=win_op, rim="#5F86E6" if night else "#F2A877", rim_side="right")
    sz_lit = sk.draw_layer(c, [bd for bd in mid + marks if bd.x0 > 0.5 * W], fill="none", b=b, s=s, rng=rng,
                           lights=cool, lit=0.32, win_op=win_op, rim="#4F7EEA", rim_side="left")
    # Ping An's spire beacon and Salesforce's lit crown.
    pa = sz_marks[1]
    c.add(f'<circle cx="{f(0.80 * W)}" cy="{f(pa.top + 1 * s)}" r="{f(1.3 * s)}" fill="#FF5A4E"/>')
    sf = sf_marks[1]
    c.add(f'<path d="M{f(0.165 * W - 10 * s)} {f(sf.top + 17 * s)}Q{f(0.165 * W)} {f(sf.top - 4 * s)} {f(0.165 * W + 10 * s)} {f(sf.top + 17 * s)}Z" '
          f'fill="{"#BFD8FF" if night else "#FFD7A6"}" opacity="0.55"/>')

    # Bay Bridge reaching out from San Francisco, fading into the haze.
    sk.bay_bridge(c, 0.205 * W, 0.372 * W, [0.25 * W, 0.318 * W], b, s,
                  steel="#3A54A8" if night else "#1C1E55", fade_to=(0.29 * W, 0.372 * W))

    # Front layer: waterfront low-rise.
    front = sk.fill_row(-0.01 * W, 0.215 * W, b, s, rng, 8, 40, 8, 20) + \
        sk.fill_row(0.635 * W, 1.01 * W, b, s, rng, 14, 70, 9, 22, sz_env)
    reflect_f = c.lin(0, b, 0, b - 0.16 * H, [(0, front_col, 0.9), (1, front_col, 0)])
    sk.draw_layer(c, front, fill=front_col, b=b, s=s, rng=rng, reflect=reflect_f)
    sk.draw_layer(c, front, fill="none", b=b, s=s, rng=rng, lights=warm + cool, lit=0.22, win_op=win_op)

    # Water.
    water = c.lin(0, b, 0, H, [(0, "#14286A" if night else "#3A3772", 0.85), (1, NAVY, 0.98)])
    c.rect(water, 0, b, W, H - b)
    if not night:
        bloom(c, 0.28 * W, b + 0.05 * H, 0.30 * W, "#FFB06E", 0.45, sy=0.2)
    sk.water_streaks(c, sf_lit + sz_lit, b, s, rng, depth=0.17 * H, op=0.45)
    shimmer(c, b, s, rng, 0.0, W, [ICE, "#7FA8F0"] if night else ["#FFD3A0", ICE], int(90 * W / 1584))
    c.add(f'<rect x="0" y="{f(b)}" width="{W}" height="{f(max(0.6, 0.7 * s))}" fill="{ICE}" opacity="0.18"/>')

    halo(c, 0.5 * W, 0.45 * H, 0.17 * W, 0.42 * H, NAVY, 0.5 if night else 0.42)
    stacked(c, 0.5 * W, 0.45 * H, K_STACK[fmt], FULL_STACK if fmt == "profile" else COMPANY_STACK)


def photo_skylines(c, fmt, mood, left, right):
    """Real photos: San Francisco cross-fading into Shenzhen, lockup over a darkened centre."""
    W, H = c.W, c.H
    credits = photos.panorama(c, left, right, mood=mood)
    # Brand grade: deepen the top and the water, and open a calm navy field for the type.
    c.rect(c.lin(0, 0, 0, H, [(0, NAVY, 0.62), (0.42, NAVY, 0.12), (0.72, NAVY, 0.05), (1, NAVY, 0.55)]))
    c.rect(c.lin(0, 0, W, 0, [(0.16, NAVY, 0), (0.36, NAVY, 0.72), (0.5, NAVY, 0.82),
                              (0.64, NAVY, 0.72), (0.84, NAVY, 0)]))
    halo(c, 0.5 * W, 0.47 * H, 0.17 * W, 0.44 * H, NAVY, 0.45)
    stacked(c, 0.5 * W, 0.47 * H, K_STACK[fmt], FULL_STACK if fmt == "profile" else COMPANY_STACK)
    return "Photos: " + "; ".join(credits)


def d01_skylines_night(c, fmt):
    have = photos.catalogue()
    if {"sf-night", "sz-night"} <= have.keys():
        return photo_skylines(c, fmt, "night", "sf-night", "sz-night")
    twin_skylines(c, fmt, "night")


def d08_skylines_dusk(c, fmt):
    have = photos.catalogue()
    if {"sf-dusk", "sz-dusk"} <= have.keys():
        return photo_skylines(c, fmt, "dusk", "sf-dusk", "sz-dusk")
    twin_skylines(c, fmt, "dusk")


COMPANY_STACK = [("monogram", 0.62, 140, 1), ("wordmark", 1, 120, 1),
                 ("founders-club", 1, 160, 0.85), ("cities", 1.15, 0, 0.7)]

DESIGNS = {
    "01-skylines-night": d01_skylines_night,
    "02-light-sweep": d02_light_sweep,
    "03-pacific-route": d03_pacific_route,
    "05-horizon": d05_horizon,
    "06-silk-light": d06_silk,
    "07-monogram-glow": d07_monogram_glow,
    "08-skylines-dusk": d08_skylines_dusk,
}


def main(only=None):
    for fmt, (w, h) in FORMATS.items():
        out = ROOT / "svg" / fmt
        out.mkdir(parents=True, exist_ok=True)
        for name, fn in DESIGNS.items():
            if only and not any(o in name for o in only):
                continue
            random.seed(name)
            c = Canvas(w, h)
            desc = fn(c, fmt) or ""
            title = f"Delta & Bay Founders Club, LinkedIn {fmt} banner {name[:2]}"
            (out / f"{name}.svg").write_text(c.svg(title, desc))
            print(f"svg/{fmt}/{name}.svg")


if __name__ == "__main__":
    main(sys.argv[1:])
