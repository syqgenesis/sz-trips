// Rasterise every SVG in ../svg and ../social (plus ../board.svg) to PNG with headless Chromium.
// Logos get a transparent background at 2400px on the long side; avatars are 1080px squares.
//   node export-png.mjs
import { chromium } from 'playwright';
import { readFileSync, readdirSync, mkdirSync } from 'node:fs';
import path from 'node:path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const jobs = [
  ...readdirSync(path.join(root, 'svg')).map((f) => ['svg', f, 'png', 2400]),
  ...readdirSync(path.join(root, 'social')).filter((f) => f.endsWith('.svg')).map((f) => ['social', f, 'social', 1080]),
  ['.', 'board.svg', '.', 2400],
];

const browser = await chromium.launch({ args: ['--disable-gpu', '--disable-dev-shm-usage'] });
const page = await browser.newPage();
for (const [dir, file, outDir, long] of jobs) {
  const src = readFileSync(path.join(root, dir, file), 'utf8');
  const [, , vw, vh] = src.match(/viewBox="([^"]+)"/)[1].split(' ').map(Number);
  const k = long / Math.max(vw, vh);
  const [w, h] = [Math.round(vw * k), Math.round(vh * k)];
  await page.setViewportSize({ width: w, height: h });
  await page.setContent(`<body style="margin:0;background:transparent">${src.replace('<svg ', `<svg width="${w}" height="${h}" style="display:block" `)}</body>`);
  mkdirSync(path.join(root, outDir), { recursive: true });
  const out = path.join(root, outDir, file.replace(/\.svg$/, '.png'));
  await page.screenshot({ path: out, omitBackground: true });
  console.log('wrote', path.relative(root, out));
}
await browser.close();
