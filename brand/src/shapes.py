"""Geometry primitives and boolean-clean shapes (skia-pathops)."""
import math

import pathops
from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pt(x, y):
    return f"{f(x)},{f(y)}"


# ---------------------------------------------------------------- primitives (SVG path data)
def polar(cx, cy, r, deg):
    """Point at radius r; deg is measured from straight down, positive to the right."""
    a = math.radians(deg)
    return cx + r * math.sin(a), cy + r * math.cos(a)


def leg(x, y, deg, length, width):
    """Long isosceles triangle from a base of `width` at (x, y) to a point `length` away."""
    a = math.radians(deg)
    ux, uy = math.sin(a), math.cos(a)
    nx, ny = uy, -ux
    tip = (x + ux * length, y + uy * length)
    p0 = (x + nx * width / 2, y + ny * width / 2)
    p1 = (x - nx * width / 2, y - ny * width / 2)
    return f"M{pt(*p0)} L{pt(*tip)} L{pt(*p1)} Z"


def disc(cx, cy, r):
    return f"M{f(cx - r)},{f(cy)} a{f(r)},{f(r)} 0 1,0 {f(2 * r)},0 a{f(r)},{f(r)} 0 1,0 {f(-2 * r)},0 Z"


def ellipse(cx, cy, rx, ry):
    return f"M{f(cx - rx)},{f(cy)} a{f(rx)},{f(ry)} 0 1,0 {f(2 * rx)},0 a{f(rx)},{f(ry)} 0 1,0 {f(-2 * rx)},0 Z"


def rect(x0, y0, x1, y1):
    return f"M{f(x0)},{f(y0)} L{f(x1)},{f(y0)} L{f(x1)},{f(y1)} L{f(x0)},{f(y1)} Z"


def triangle(cx, cy, h):
    """Equilateral-ish triangle pointing up, centred on (cx, cy)."""
    return (f"M{f(cx)},{f(cy - h * 0.6)} L{f(cx + h * 0.58)},{f(cy + h * 0.4)} "
            f"L{f(cx - h * 0.58)},{f(cy + h * 0.4)} Z")


def crescent(cx, cy, r, wmax, d0, d1, n=240, power=2.0):
    """Band on radius r, widest in the middle and tapering to points at both ends."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        d = d0 + (d1 - d0) * t
        w = wmax * (1 - abs(2 * t - 1) ** power)
        outer.append(polar(cx, cy, r + w / 2, d))
        inner.append(polar(cx, cy, r - w / 2, d))
    return "M" + " L".join(pt(*p) for p in outer + inner[::-1]) + " Z"


# ---------------------------------------------------------------- shapes
class S:
    """A filled shape. | is union, - is difference, & is intersection."""

    def __init__(self, p=None):
        self.p = p if p is not None else pathops.Path()

    @staticmethod
    def d(*ds):
        out = pathops.Path()
        for d in ds:
            p = pathops.Path()
            parse_path(d, p.getPen())
            out = pathops.op(out, p, pathops.PathOp.UNION)
        return S(out)

    def __or__(self, o):
        return S(pathops.op(self.p, o.p, pathops.PathOp.UNION))

    def __sub__(self, o):
        return S(pathops.op(self.p, o.p, pathops.PathOp.DIFFERENCE))

    def __and__(self, o):
        return S(pathops.op(self.p, o.p, pathops.PathOp.INTERSECTION))

    def t(self, transform):
        out = pathops.Path()
        self.p.draw(TransformPen(out.getPen(), tuple(transform)))
        return S(out)

    def move(self, dx, dy):
        return self.t(Transform().translate(dx, dy))

    def mirror_x(self):
        return self.t(Transform().scale(-1, 1))

    @property
    def bounds(self):
        return self.p.bounds

    @property
    def contours(self):
        return [S(c) for c in self.p.contours]

    @property
    def w(self):
        return self.bounds[2] - self.bounds[0]

    @property
    def h(self):
        return self.bounds[3] - self.bounds[1]

    def fit(self, x, y, w=None, h=None, anchor="center"):
        """Scale to width w (or height h); anchor 'center', 'top' (top-centre) or 'topleft'."""
        b = self.bounds
        k = w / self.w if w is not None else h / self.h
        s = self.t(Transform().scale(k).translate(-b[0], -b[1]))
        if anchor == "center":
            return s.move(x - s.w / 2, y - s.h / 2)
        if anchor == "top":
            return s.move(x - s.w / 2, y)
        return s.move(x, y)

    def path_d(self):
        pen = SVGPathPen(None, ntos=f)
        self.p.draw(pen)
        return pen.getCommands()


def union(*shapes):
    out = S()
    for s in shapes:
        out = out | s
    return out
