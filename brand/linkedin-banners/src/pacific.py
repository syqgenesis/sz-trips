"""Night map of the Pacific with the San Francisco to Shenzhen route."""

import json
import math
from pathlib import Path

from shapely.geometry import Polygon, box

from canvas import f
from skyline import Compound

DATA = Path(__file__).resolve().parent.parent / "data" / "pacific.json"
SZ = (114.06, 22.54)
SF = (237.58, 37.77)  # -122.42 shifted into 0..360


def merc(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


class Projection:
    """Mercator, scaled so the two cities land on the given pixel positions (x only;
    y follows from the projection so the map is never stretched)."""

    def __init__(self, sz_px, sf_x):
        self.R = (sf_x - sz_px[0]) / math.radians(SF[0] - SZ[0])
        self.x0, self.y0 = sz_px

    def __call__(self, lon, lat):
        return (self.x0 + self.R * math.radians(lon - SZ[0]),
                self.y0 - self.R * (merc(lat) - merc(SZ[1])))


def draw(c, proj, *, land_fill, coast="#4C7BE0", lights="#FFC877"):
    W, H, s = c.W, c.H, c.s
    data = json.loads(DATA.read_text())
    frame = box(-20, -20, W + 20, H + 20)

    # Graticule every 15 degrees, very faint.
    grid = Compound()
    for lon in range(60, 301, 15):
        x, _ = proj(lon, 0)
        if 0 <= x <= W:
            grid.line(x, 0, x, H)
    for lat in range(-15, 76, 15):
        _, y = proj(SZ[0], lat)
        if 0 <= y <= H:
            grid.line(0, y, W, y)
    c.add(f'<path d="{grid.d}" fill="none" stroke="#9CC5FF" stroke-opacity="0.06" stroke-width="{f(max(0.5, 0.6 * s))}"/>')

    # Land, clipped to the frame and simplified in pixel space.
    land = Compound()
    for rings in data["land"]:
        poly = Polygon([proj(*p) for p in rings[0]], [[proj(*p) for p in r] for r in rings[1:]])
        poly = poly.buffer(0).intersection(frame).simplify(0.35)
        for g in getattr(poly, "geoms", [poly]):
            if g.is_empty or g.geom_type != "Polygon" or g.area < 1.5:
                continue
            for ring in [g.exterior, *g.interiors]:
                land.poly(list(ring.coords)[:-1])
    c.add(f'<path d="{land.d}" fill="none" stroke="{coast}" stroke-opacity="0.10" stroke-width="{f(4 * s)}" stroke-linejoin="round"/>')
    c.add(f'<path d="{land.d}" fill="{land_fill}" fill-rule="evenodd" stroke="{coast}" '
          f'stroke-opacity="0.5" stroke-width="{f(max(0.5, 0.6 * s))}" stroke-linejoin="round"/>')

    # City lights, brightest last.
    glow = c.rad_box([(0, lights, 0.55), (0.35, lights, 0.18), (1, lights, 0)])
    tiers = {}
    big = []
    for lon, lat, pop in data["cities"]:
        x, y = proj(lon, lat)
        if not (-5 < x < W + 5 and -5 < y < H + 5):
            continue
        if pop >= 1_000_000:
            big.append((x, y, pop))
        size = (0.7 if pop < 150_000 else 1.0 if pop < 500_000 else 1.4 if pop < 2_000_000 else 1.9) * max(s, 0.55)
        op = 0.45 if pop < 150_000 else 0.65 if pop < 500_000 else 0.85 if pop < 2_000_000 else 1.0
        tiers.setdefault(op, Compound()).rect(x - size / 2, y - size / 2, size, size)
    glows = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f((4 + 3.2 * math.log10(pop / 1e6 + 1) * 3) * s)}"/>'
                    for x, y, pop in big)
    c.add(f'<g fill="{glow}">{glows}</g>')
    for op, comp in sorted(tiers.items()):
        c.add(f'<path d="{comp.d}" fill="{lights}" opacity="{f(op)}"/>')
