// Rasterise the SVG banners to upload-ready PNGs with headless Chromium.
//   node src/render.mjs [scale] [files...]   (default: every svg/*/*.svg at 2x)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); } catch { playwright = require('/opt/node22/lib/node_modules/playwright'); }

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [scaleArg, ...only] = process.argv.slice(2);
const scale = Number(scaleArg || 2);
const files = only.length ? only : fs.readdirSync(path.join(root, 'svg')).flatMap(fmt =>
  fs.readdirSync(path.join(root, 'svg', fmt)).filter(f => f.endsWith('.svg')).map(f => path.join('svg', fmt, f)));

const browser = await playwright.chromium.launch();
for (const rel of files) {
  const file = path.join(root, rel);
  const svg = fs.readFileSync(file, 'utf8');
  const [, w, h] = svg.match(/width="(\d+)" height="(\d+)"/).map(Number);
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
  // Load the file itself (strict XML), not inline HTML, so a malformed SVG fails here.
  await page.goto('file://' + file);
  if (await page.$('parsererror')) throw new Error(`${rel}: not well-formed SVG`);
  const out = path.join(root, rel.replace(/^svg/, 'png').replace(/\.svg$/, '.png'));
  fs.mkdirSync(path.dirname(out), { recursive: true });
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: w, height: h } });
  await page.close();
  console.log(path.relative(root, out));
}
await browser.close();
