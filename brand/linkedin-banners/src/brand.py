"""Brand elements lifted verbatim from the master logo file.

Every banner places these paths with a transform; nothing here redraws or
re-types the logo. Replace logo/delta-and-bay-logo.svg and rebuild to update.
"""

import re
from pathlib import Path

MASTER = Path(__file__).resolve().parent.parent / "logo" / "delta-and-bay-logo.svg"

NAVY = "#050A30"
IVORY = "#ECE8E0"


def _bbox(d, steps=16):
    """Exact-enough bounds for absolute M/L/H/V/C/Q/Z path data (curves sampled)."""
    toks = re.findall(r"[MLHVCQZ]|-?\d*\.?\d+(?:e-?\d+)?", d)
    xs, ys = [], []
    i, cmd, cur, start = 0, None, (0.0, 0.0), (0.0, 0.0)

    def nums(n):
        nonlocal i
        out = [float(t) for t in toks[i:i + n]]
        i += n
        return out

    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd == "Z":
                cur = start
                continue
        if cmd == "M":
            cur = start = tuple(nums(2))
            cmd = "L"
            pts = [cur]
        elif cmd == "L":
            cur = tuple(nums(2))
            pts = [cur]
        elif cmd == "H":
            cur = (nums(1)[0], cur[1])
            pts = [cur]
        elif cmd == "V":
            cur = (cur[0], nums(1)[0])
            pts = [cur]
        elif cmd == "C":
            a = nums(6)
            p0, p1, p2, p3 = cur, a[0:2], a[2:4], a[4:6]
            pts = []
            for k in range(1, steps + 1):
                t = k / steps
                u = 1 - t
                pts.append(tuple(u**3 * q0 + 3 * u * u * t * q1 + 3 * u * t * t * q2 + t**3 * q3
                                 for q0, q1, q2, q3 in zip(p0, p1, p2, p3)))
            cur = tuple(p3)
        elif cmd == "Q":
            a = nums(4)
            p0, p1, p2 = cur, a[0:2], a[2:4]
            pts = []
            for k in range(1, steps + 1):
                t = k / steps
                u = 1 - t
                pts.append(tuple(u * u * q0 + 2 * u * t * q1 + t * t * q2 for q0, q1, q2 in zip(p0, p1, p2)))
            cur = tuple(p2)
        else:
            raise ValueError(f"unsupported path command {cmd}")
        for x, y in pts:
            xs.append(x)
            ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


class Element:
    def __init__(self, ident, d):
        self.id, self.d = ident, d
        x0, y0, x1, y1 = _bbox(d)
        self.x, self.y, self.w, self.h = x0, y0, x1 - x0, y1 - y0

    def place(self, x, y, *, h=None, w=None, anchor="middle", fill=IVORY, attrs=""):
        """Draw the element scaled to height `h` (or width `w`).

        (x, y) is the top edge at the anchor point: anchor = start | middle | end.
        Returns (svg, placed_width, placed_height).
        """
        s = h / self.h if h is not None else w / self.w
        pw, ph = self.w * s, self.h * s
        left = {"start": x, "middle": x - pw / 2, "end": x - pw}[anchor]
        tx, ty = left - self.x * s, y - self.y * s
        svg = (f'<path d="{self.d}" fill="{fill}" '
               f'transform="translate({tx:.3f} {ty:.3f}) scale({s:.6f})"{attrs}/>')
        return svg, pw, ph


def load():
    src = MASTER.read_text()
    return {m.group(1): Element(m.group(1), m.group(2))
            for m in re.finditer(r'<path id="([^"]+)" d="([^"]+)"', src)}


EL = load()
