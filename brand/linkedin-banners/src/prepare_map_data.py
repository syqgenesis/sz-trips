"""One-off: cut Natural Earth (public domain) down to the Pacific window we draw.

    python3 src/prepare_map_data.py <dir with ne_50m_land.geojson and
                                     ne_10m_populated_places_simple.geojson>

Writes data/pacific.json: land rings and city points with longitudes shifted to
0..360 so the Pacific is continuous. Only needed if the map window changes.
Source: https://github.com/nvkelso/natural-earth-vector (geojson/).
"""

import json
import sys
from pathlib import Path

from shapely.geometry import box, mapping, shape
from shapely.affinity import translate
from shapely.ops import unary_union

LON = (55.0, 300.0)   # India to the US east coast, through the Pacific
LAT = (-12.0, 72.0)
OUT = Path(__file__).resolve().parent.parent / "data" / "pacific.json"


def main(src):
    src = Path(src)
    window = box(LON[0], LAT[0], LON[1], LAT[1])
    land = json.loads((src / "ne_50m_land.geojson").read_text())
    pieces = []
    for feat in land["features"]:
        g = shape(feat["geometry"]).buffer(0)
        for shifted in (g, translate(g, xoff=360)):
            cut = shifted.intersection(window)
            if not cut.is_empty:
                pieces.append(cut)
    merged = unary_union(pieces).simplify(0.04, preserve_topology=True)
    rings = []
    for poly in getattr(merged, "geoms", [merged]):
        if poly.area < 0.02:
            continue
        geo = mapping(poly)["coordinates"]
        rings.append([[[round(x, 3), round(y, 3)] for x, y in ring] for ring in geo])

    places = json.loads((src / "ne_10m_populated_places_simple.geojson").read_text())
    cities = []
    for feat in places["features"]:
        p = feat["properties"]
        lon, lat = feat["geometry"]["coordinates"]
        lon = lon + 360 if lon < LON[0] else lon
        pop = p.get("pop_max") or 0
        if LON[0] <= lon <= LON[1] and LAT[0] <= lat <= LAT[1] and pop >= 20000:
            cities.append([round(lon, 3), round(lat, 3), int(pop)])
    cities.sort(key=lambda c: -c[2])

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"source": "Natural Earth 1:50m land, 1:10m populated places (public domain)",
                               "lon": LON, "lat": LAT, "land": rings, "cities": cities},
                              separators=(",", ":")))
    print(f"{OUT.name}: {len(rings)} land polygons, {len(cities)} cities, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1])
