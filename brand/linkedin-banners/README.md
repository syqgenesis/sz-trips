# Delta & Bay LinkedIn banners

Seven banner designs, each in two LinkedIn formats, built from the mockups we picked (01, 02, 03, 05, 06, 07, 08). The numbers match the mockup sheet.

| Format | Size | Where | What covers it |
|---|---|---|---|
| `profile` | 1584 × 396 (4:1) | Personal profile background | Profile photo, bottom-left |
| `company` | 1128 × 191 | Company page cover | Page logo, bottom-left |

All seven keep the bottom-left clear. `preview/profile.jpg` and `preview/company.jpg` show every banner with the photo/logo area marked.

| # | Design |
|---|---|
| 01 | Twin skylines at night: San Francisco and the Bay Bridge on the left, Shenzhen (Ping An, China Resources, Kingkey 100) on the right |
| 02 | A curved sheet of light sweeping across the right, with the lockup on the left |
| 03 | Night map of the Pacific with a route arc from San Francisco to Shenzhen |
| 05 | A planet's lit rim rising from the bottom-left, then the lockup and tagline. Mirrored from the mockup so the light stays clear of the profile photo |
| 06 | Silk ribbons of light behind a centred lockup |
| 07 | The monogram as a giant lit watermark |
| 08 | Twin skylines at dusk: warm sunset over San Francisco, blue hour over Shenzhen |

## Files

- `svg/<format>/*.svg`: the vector masters. They're self-contained, with no fonts, embedded images, filters or masks, so they open the same in Figma, Illustrator, Inkscape, Affinity and Canva. Glows are built from gradients and stacked strokes.
- `png/<format>/*.png`: ready to upload. They're rendered at 2× (3168 × 792 and 2256 × 382), which LinkedIn accepts and downsizes cleanly.
- `logo/delta-and-bay-logo.svg`: the master logo. Every banner uses its paths unchanged (the monogram, DELTA & BAY, FOUNDERS CLUB, BRIDGING FRONTIERS, and the SAN FRANCISCO — SHENZHEN line). Nothing is redrawn or retyped.

Palette: navy `#050A30` and ivory `#ECE8E0` from the logo, plus electric blues for the light.

## Rebuild

```sh
pip install shapely pillow             # shapely for the map, pillow for previews
python3 src/build.py                   # svg/
node src/render.mjs                    # png/ (needs Playwright + Chromium)
python3 src/preview.py                 # preview/
```

To update the logo, replace `logo/delta-and-bay-logo.svg` (keep the path `id`s) and rebuild. `src/build.py` holds one function per design. Layout values are fractions of the banner width/height, so both formats come from the same code. The map uses `data/pacific.json`, a trimmed cut of Natural Earth (public domain) made by `src/prepare_map_data.py`.
