"""Contact sheets with LinkedIn's photo/logo overlap marked, from the 2x PNGs.

    python3 src/preview.py   ->  preview/profile.jpg, preview/company.jpg
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent

# Where LinkedIn draws over the banner, in banner pixels (desktop layout).
OVERLAP = {
    "profile": ("ellipse", (47, 207, 347, 507)),   # profile photo
    "company": ("rect", (24, 127, 152, 255)),      # page logo
}


def sheet(fmt, width=1584, pad=24):
    files = sorted((ROOT / "png" / fmt).glob("*.png"))
    tiles = []
    for p in files:
        im = Image.open(p).convert("RGB")
        scale = width / im.width
        im = im.resize((width, round(im.height * scale)), Image.LANCZOS)
        draw = ImageDraw.Draw(im, "RGBA")
        shape, box = OVERLAP[fmt]
        k = width / {"profile": 1584, "company": 1128}[fmt]
        box = [v * k for v in box]
        if shape == "ellipse":
            draw.ellipse(box, fill=(236, 232, 224, 70), outline=(236, 232, 224, 200), width=2)
        else:
            draw.rounded_rectangle(box, radius=8, fill=(236, 232, 224, 70), outline=(236, 232, 224, 200), width=2)
        tiles.append(im)
    h = sum(t.height for t in tiles) + pad * (len(tiles) + 1)
    out = Image.new("RGB", (width + 2 * pad, h), (18, 20, 30))
    y = pad
    for t in tiles:
        out.paste(t, (pad, y))
        y += t.height + pad
    dest = ROOT / "preview" / f"{fmt}.jpg"
    dest.parent.mkdir(exist_ok=True)
    out.save(dest, quality=88, optimize=True)
    print(dest.relative_to(ROOT))


if __name__ == "__main__":
    for fmt in OVERLAP:
        sheet(fmt)
