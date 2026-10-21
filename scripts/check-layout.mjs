#!/usr/bin/env node
// Captures and measures a served web surface the way a person meets it, at four widths,
// and fails on the layout problems an agent cannot see from its own code.
//
// Usage: check-layout <url> [--paths=<route>,<route>] [--errors=<route>] [--storage-state=<file>] [--out=<dir>] [--app]
//   <url>     The served production build, for example http://localhost:3000
//   --paths   Extra routes to check besides the pages linked from <url>
//   --out     Folder for the one-screen captures (default: layout-check in the current folder)
//   --app     The surface is a signed-in app shell rather than a document
//   --errors  Routes that should answer an error status, checked as pages
//   --storage-state  A Playwright storage state file for a signed-in session
//
// Needs Playwright with Chromium, resolved from the current project first:
//   npm install --save-dev playwright && npx playwright install chromium
// Exit code 0 when every check passes, 1 when any fails, 2 on a usage or setup error.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const opt = Object.fromEntries(args.filter((a) => a.startsWith('--')).map((a) => { const [k, v] = a.slice(2).split('='); return [k, v ?? true]; }));
const start = args.find((a) => !a.startsWith('--'));
if (!start || opt.help) {
  console.log(`Usage: check-layout <url> [--paths=<route>,<route>] [--errors=<route>] [--storage-state=<file>] [--out=<dir>] [--app]

Checks the start page, the pages it links to, and every --paths route, at 1440x900,
2560x1440, 390x844 (touch), and 320x700, and fails on:
  sideways scroll; standalone targets under 24x24; desktop actions a phone cannot reach;
  form fields under 16px on a phone; text under 9px;
  a document page over 1.3x its desktop length in screens at 390 or 320 (long reading
  pages exempt); a short row of two or three peers that stacks on a phone; a table that
  drops columns on a phone; text cut off, scrolling inside its box, or covered by a control;
  a one-word label broken across lines; a heading wrapping over one line more than on
  desktop; pages sharing a tab title or a title that does not lead with the page heading;
  a missing favicon or apple-touch-icon; console errors and failed requests; placeholder
  text such as lorem ipsum or TODO:; with --app, a shell that scrolls the whole page.
It also lists for review, without failing, phone text outside 13 to 15px, which the
supporting-copy range covers but a reading page's body text does not.
--errors names routes that should answer an error status, such as a not-found page, so they
are checked as pages. --storage-state is a Playwright storage state file for a signed-in session.
Captures go to --out as page<N>-<width>-<slice>.png, and the output maps each N to its route.`);
  process.exit(opt.help ? 0 : 2);
}

async function loadPlaywright() {
  for (const base of [path.join(process.cwd(), 'noop.js'), import.meta.url]) {
    try {
      const req = createRequire(base);
      const pw = await import(pathToFileURL(req.resolve('playwright')).href);
      return pw.chromium ? pw : pw.default;
    } catch {}
  }
  console.error('Playwright is not installed. Run: npm install --save-dev playwright && npx playwright install chromium');
  process.exit(2);
}
const { chromium } = await loadPlaywright();

const out = path.resolve(opt.out || 'layout-check');
await fs.mkdir(out, { recursive: true });
const WIDTHS = [
  { name: '1440', width: 1440, height: 900 },
  { name: '2560', width: 2560, height: 1440 },
  { name: '390', width: 390, height: 844, deviceScaleFactor: 3, isMobile: true, hasTouch: true },
  { name: '320', width: 320, height: 700, isMobile: true, hasTouch: true },
];
const LENGTH_BUDGET = 1.3;
// Installed in every page: visible means a real box, not hidden or transparent, and not clipped away by any ancestor.
const VIS_INIT = () => {
  window.__lcVis = (e) => {
    const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    if (!(r.width > 1 && r.height > 1 && s.visibility !== 'hidden' && +s.opacity !== 0)) return false;
    let left = r.left, right = r.right, top = r.top, bottom = r.bottom;
    for (let p = e.parentElement; p && p !== document.documentElement; p = p.parentElement) {
      const ps = getComputedStyle(p);
      if (+ps.opacity === 0 || ps.visibility === 'hidden') return false;
      const pr = p.getBoundingClientRect();
      if (/hidden|clip/.test(ps.overflowX) && p !== document.body) { left = Math.max(left, pr.left); right = Math.min(right, pr.right); }
      if (/hidden|clip/.test(ps.overflowY) && p !== document.body) { top = Math.max(top, pr.top); bottom = Math.min(bottom, pr.bottom); }
      if (right - left < 1 || bottom - top < 1) return false;
    }
    return true;
  };
};
const origin = new URL(start).origin;
let browser;
try {
  browser = await chromium.launch();
} catch {
  console.error('Chromium is not installed for Playwright. Run: npx playwright install chromium');
  process.exit(2);
}

// Pages: the start page, every same-origin page it links to, and any --paths.
const pages = [];
const notChecked = [];
const capped = [];
const sampled = [];
const downloads = [];
const MAX_PAGES = Number(opt['max-pages'] || 12);
const MAX_SLICES = Number(opt['max-slices'] || 12);
// Git Bash rewrites a leading slash into its install folder, so undo that before resolving.
const route = (p) => p.replace(/^[A-Za-z]:\/.*?\/Git(?=\/)/i, '').replace(/^(?!\/)/, '/');
const norm = (u) => { const x = new URL(u); x.hash = ''; if (x.pathname.length > 1) x.pathname = x.pathname.replace(/\/+$/, ''); return x.href; };
const list = (v) => String(v || '').split(',').filter(Boolean).map((p) => norm(new URL(route(p), start).href));
const expectedErrors = new Set(list(opt.errors));
const storageState = opt['storage-state'] || undefined;
// Loads a page, then waits a bounded time for the network to settle, so live connections cannot hang it.
const load = async (page, url) => {
  const resp = await page.goto(url, { waitUntil: 'load', timeout: 30000 }).catch(() => null);
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
  return resp;
};
{
  const ctx = await browser.newContext({ storageState });
  await ctx.addInitScript(VIS_INIT);
  const page = await ctx.newPage();
  // Every route passed with --paths or --errors is checked; links from the start page fill the rest up to the page limit.
  const given = [norm(start), ...list(opt.paths), ...expectedErrors];
  const found = [];
  const seen = new Set();
  const visit = async (href, crawl) => {
    const u = new URL(href);
    if (seen.has(u.href)) return;
    seen.add(u.href);
    let downloaded = false;
    const onDownload = () => { downloaded = true; };
    page.on('download', onDownload);
    const resp = await page.goto(u.href, { waitUntil: 'load', timeout: 30000 }).catch((e) => { if (/download is starting/i.test(e.message)) downloaded = true; return null; });
    if (resp) await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
    await page.waitForTimeout(200);
    page.off('download', onDownload);
    if (downloaded || /attachment/i.test((resp && resp.headers()['content-disposition']) || '')) { downloads.push(u.pathname); return; }
    if (!resp) { pages.push({ url: u.href, status: 0 }); return; }
    const landed = new URL(norm(page.url()));
    if (landed.pathname !== u.pathname) {
      // A redirect to sign-in means the page was never seen. Any other redirect, such as a
      // dispatcher route forwarding into the product, is followed and the landed page is checked.
      if (/(^|\/)(log-?in|sign-?in|auth|session)(\/|$)/i.test(landed.pathname)) { pages.push({ url: u.href, status: resp.status(), redirected: landed.pathname }); return; }
      if (seen.has(landed.href)) return;
      seen.add(landed.href);
      pages.push({ url: landed.href, status: resp.status(), from: u.pathname });
    } else pages.push({ url: u.href, status: resp.status() });
    if (crawl) for (const h of await page.$$eval('a[href]:not([download])', (as) => as.map((a) => a.href))) {
      const x = new URL(h);
      // Same-origin documents only: a link to a file such as an installer is a download, not a page.
      if (x.origin === origin && !/\.(?!html?$)[a-z0-9]{1,5}$/i.test(x.pathname)) found.push(norm(h));
    }
  };
  for (const [i, g] of given.entries()) await visit(g, i === 0);
  // Linked pages that differ only by an identifier share one route shape, so one of each shape is checked.
  const shape = (href) => { const x = new URL(href); return x.pathname.split('/').map((s) => /^\d+$/.test(s) || (/\d/.test(s) && /[A-Za-z]/.test(s) && s.length >= 6) || /^[0-9a-f-]{16,}$/i.test(s) ? ':id' : s).join('/') + (x.search ? '?' : ''); };
  const shapes = new Set([...seen].map(shape));
  for (const f of found) {
    if (shapes.has(shape(f))) continue;
    if (pages.length >= MAX_PAGES + given.length) break;
    shapes.add(shape(f));
    await visit(f, false);
  }
  notChecked.push(...new Set(found.filter((q) => !shapes.has(shape(q))).map((q) => new URL(q).pathname)));
  sampled.push(...new Set(found.filter((q) => !seen.has(q) && shapes.has(shape(q))).map((q) => new URL(q).pathname)));
  await ctx.close();
}


const measure = () => {
  const vis = window.__lcVis;
  // A checkbox or radio is hit through its label too, so its target is the larger of the two boxes.
  const hitBox = (e) => {
    let r = e.getBoundingClientRect();
    const label = /checkbox|radio/.test(e.type || '') && (e.closest('label') || (e.id && document.querySelector(`label[for="${CSS.escape(e.id)}"]`)));
    if (label) { const l = label.getBoundingClientRect(); if (l.width * l.height > r.width * r.height) r = l; }
    return r;
  };
  const name = (e) => (e.getAttribute('aria-label') || e.textContent || e.getAttribute('title') || '').trim().replace(/\s+/g, ' ').slice(0, 50);
  const W = innerWidth, de = document.documentElement;
  const actions = [...document.querySelectorAll('a[href],button,[role=button],summary,input:not([type=hidden]),select,textarea')];
  const visible = actions.filter(vis);
  const inSentence = (e) => e.tagName === 'A' && getComputedStyle(e).display === 'inline' && !!e.closest('p,li p,td,dd,blockquote');
  const small = visible.filter((e) => !inSentence(e)).map((e) => ({ name: name(e) || e.tagName.toLowerCase(), w: Math.round(hitBox(e).width), h: Math.round(hitBox(e).height) })).filter((t) => t.w < 24 || t.h < 24);
  const escaped = [...document.querySelectorAll('body *')].filter((e) => { if (!vis(e)) return false; const r = e.getBoundingClientRect(); if (r.right <= W + 1 && r.left >= -1) return false; for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) { if (/auto|scroll|hidden|clip/.test(getComputedStyle(p).overflowX)) return false; } return getComputedStyle(e).position !== 'fixed'; }).slice(0, 5).map((e) => e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className ? '.' + e.className.trim().split(/\s+/)[0] : ''));
  const copy = [...document.querySelectorAll('p,li,dd,figcaption,blockquote')].filter((e) => vis(e) && !e.closest('nav,header,footer,button') && e.textContent.trim().length > 30).map((e) => parseFloat(getComputedStyle(e).fontSize));
  const inputs = [...document.querySelectorAll('input:not([type=checkbox]):not([type=radio]):not([type=hidden]),textarea,select')].filter(vis).map((e) => parseFloat(getComputedStyle(e).fontSize)).filter((s) => s < 16).length;
  const lines = (e) => { const ys = new Set(); const w = document.createTreeWalker(e, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) for (let i = 0; i < n.length; i++) { if (!n.textContent[i].trim()) continue; const r = new Range(); r.setStart(n, i); r.setEnd(n, i + 1); for (const b of r.getClientRects()) if (b.width) ys.add(Math.round(b.y)); } return ys.size; };
  const headings = [...document.querySelectorAll('h1,h2')].filter(vis).map((e) => ({ text: e.textContent.trim().replace(/\s+/g, ' ').slice(0, 40), lines: lines(e) }));
  const toggle = visible.some((e) => e.hasAttribute('aria-expanded') || e.hasAttribute('aria-controls') || e.tagName === 'SUMMARY' || e.getAttribute('aria-haspopup'));
  // Text a person cannot read in full: clipped by its own box, or covered by a control.
  const textEls = [...document.querySelectorAll('p,li,h1,h2,h3,h4,code,pre,kbd,label,td,dd,span')].filter((e) => vis(e) && [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 3));
  const clipped = textEls.filter((e) => { const s = getComputedStyle(e); return /hidden|clip|auto|scroll/.test(s.overflowX) && s.textOverflow !== 'ellipsis' && e.textContent.trim().length < 160 && e.scrollWidth > e.clientWidth + 1; }).map((e) => e.textContent.trim().slice(0, 30));
  const covered = [];
  for (const c of visible.filter((e) => /absolute|fixed|sticky/.test(getComputedStyle(e).position) || e.tagName === 'BUTTON')) {
    const r = c.getBoundingClientRect().toJSON();
    for (const t of textEls) {
      if (t.contains(c) || c.contains(t)) continue;
      const range = document.createRange(); range.selectNodeContents(t);
      for (const b0 of range.getClientRects()) {
        const o = (b) => Math.min(b.right, r.right) - Math.max(b.left, r.left) >= 3 && Math.min(b.bottom, r.bottom) - Math.max(b.top, r.top) >= 3;
        if (!b0.width || !o(b0)) continue;
        c.scrollIntoView({ block: 'center', behavior: 'instant' });
        const b = [...range.getClientRects()].find((x) => x.width && o(x)) || b0;
        Object.assign(r, c.getBoundingClientRect().toJSON());
        const x1 = Math.max(b.left, r.left), x2 = Math.min(b.right, r.right), y1 = Math.max(b.top, r.top), y2 = Math.min(b.bottom, r.bottom);
        if (x2 - x1 < 3 || y2 - y1 < 3) continue;
        const hit = document.elementFromPoint(Math.min((x1 + x2) / 2, innerWidth - 1), (y1 + y2) / 2);
        if (hit && (hit === c || c.contains(hit))) { covered.push(`${name(c)} over "${t.textContent.trim().slice(0, 30)}"`); break; }
      }
      if (covered.length > 4) break;
    }
  }
  scrollTo({ top: 0, behavior: 'instant' });
  // Short rows of two or three short peers, keyed by their place in the document, excluding rows that pair copy with a picture.
  const pathOf = (e) => { const parts = []; for (let n = e; n && n !== document.body; n = n.parentElement) parts.unshift(n.tagName + ':' + [...n.parentElement.children].indexOf(n)); return parts.join('>'); };
  const rows = {};
  for (const e of document.querySelectorAll('body *')) {
    if (!vis(e) || !/flex|grid/.test(getComputedStyle(e).display)) continue;
    const kids = [...e.children].filter(vis);
    if (kids.length < 2 || kids.length > 3 || kids.some((k) => k.textContent.trim().length > 140)) continue;
    const box = e.getBoundingClientRect();
    if (kids.some((k) => [k, ...k.querySelectorAll('*')].some((m) => /^(IMG|SVG|CANVAS|VIDEO|PICTURE)$/i.test(m.tagName) && m.getBoundingClientRect().width > box.width * 0.3))) continue;
    const tops = kids.map((k) => Math.round(k.getBoundingClientRect().top));
    rows[pathOf(e)] = { oneRow: tops.every((t) => Math.abs(t - tops[0]) < 12), n: kids.length, text: e.textContent.trim().replace(/\s+/g, ' ').slice(0, 30) };
  }
  const tiny = [...new Set(textEls.filter((e) => parseFloat(getComputedStyle(e).fontSize) < 9).map((e) => `"${e.textContent.trim().slice(0, 20)}" ${parseFloat(getComputedStyle(e).fontSize).toFixed(1)}px`))].slice(0, 5);
  const broken = visible.filter((e) => { const t = e.textContent.trim(); if (!t || /\s/.test(t) || t.length > 24) return false; const tops = new Set(); const w = document.createTreeWalker(e, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) { const r = document.createRange(); r.selectNodeContents(n); for (const b of r.getClientRects()) if (b.width > 1) tops.add(Math.round(b.top)); } return tops.size > 1; }).map((e) => e.textContent.trim()).slice(0, 5);
  const paras = [...document.querySelectorAll('p')].filter(vis).map((e) => e.textContent.trim().length);
  // A reading page, such as legal text or an article, is mostly long paragraphs; its copy follows the reading measure.
  const bodyLen = document.body.innerText.length || 1;
  const reading = [...document.querySelectorAll('p')].filter(vis).map((e) => e.textContent.trim().length).filter((n) => n > 150).reduce((a, b) => a + b, 0) / bodyLen > 0.5;
  const longForm = reading || paras.reduce((a, b) => a + b, 0) > 2500 && paras.filter((n) => n > 200).length >= 4;
  // Placeholder phrases anywhere, and a value rendered as a bare undefined, NaN, or null.
  const placeholder = [...new Set([
    ...(document.body.innerText.match(/lorem ipsum|\bTODO:|\[object Object\]/gi) || []).map((s) => s.toLowerCase()),
    ...[...document.querySelectorAll('body *')].filter((e) => !e.children.length && vis(e) && /^(undefined|NaN|null)$/.test(e.textContent.trim())).map((e) => e.textContent.trim()),
  ])];
  // The one region an app shell scrolls, when the document itself does not.
  let region = null;
  if (de.scrollHeight <= innerHeight + 1) {
    const c = [...document.querySelectorAll('body *')].filter((e) => /auto|scroll/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 1 && e.clientHeight > innerHeight * 0.4).sort((a, b) => b.clientHeight * b.clientWidth - a.clientHeight * a.clientWidth)[0];
    if (c) { c.setAttribute('data-layout-check-region', ''); region = { total: c.scrollHeight, view: c.clientHeight }; }
  }
  return {
    screens: region ? region.total / region.view : de.scrollHeight / innerHeight, docScrolls: de.scrollHeight > innerHeight + 1,
    overflow: de.scrollWidth - de.clientWidth, escaped, small, copyMin: copy.length ? Math.min(...copy) : null, copyMax: copy.length ? Math.max(...copy) : null,
    smallInputs: inputs, longForm, rows, tiny, broken, clipped: [...new Set(clipped)].slice(0, 5), covered: [...new Set(covered)].slice(0, 5), headings, actionNames: [...new Set(visible.map(name).filter(Boolean))], toggle, placeholder,
    tables: [...document.querySelectorAll('table')].filter(vis).map((t) => [...(t.tHead?.rows[0] || t.rows[0])?.cells || []].filter(vis).length),
    h1: (document.querySelector('h1')?.textContent || '').trim().replace(/\s+/g, ' '),
    icons: { icon: document.querySelector('link[rel~="icon"]')?.href || null, apple: document.querySelector('link[rel="apple-touch-icon"]')?.href || null },
    title: document.title, total: region ? region.total : de.scrollHeight, step: region ? region.view : innerHeight, region: !!region,
  };
};

const failures = new Map();
const reviews = new Map();
// Heuristic findings a person decides, listed apart from failures.
const review = (page, width, msg) => { const k = `${msg} (at ${width})`; if (!reviews.has(k)) reviews.set(k, new Set()); reviews.get(k).add(new URL(page).pathname); };
// Problems group by kind and width, so one cause across many pages reads as one line.
const fail = (page, width, msg) => {
  const [kind, detail] = msg.split(/: (.*)/s);
  const k = `${kind} (at ${width})`;
  if (!failures.has(k)) failures.set(k, { pages: new Set(), details: new Set() });
  failures.get(k).pages.add(new URL(page).pathname);
  for (const d of (detail || '').split('; ').filter(Boolean)) failures.get(k).details.add(d);
};
for (const [pi, p] of pages.entries()) {
  const expected = expectedErrors.has(norm(p.url));
  if (p.status === 0 || (p.status >= 400 && !expected)) { fail(p.url, '-', `answered ${p.status || 'no response'}`); continue; }
  if (expected && p.status < 400) fail(p.url, '-', `answered ${p.status} where an error status was expected`);
  if (p.redirected) { fail(p.url, '-', `redirected to sign-in at ${p.redirected}, so it was not checked; pass --storage-state for a signed-in session`); continue; }
  const byWidth = {};
  for (const v of WIDTHS) {
    const ctx = await browser.newContext({ storageState, viewport: { width: v.width, height: v.height }, deviceScaleFactor: v.deviceScaleFactor || 1, isMobile: !!v.isMobile, hasTouch: !!v.hasTouch });
    await ctx.addInitScript(VIS_INIT);
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(e.message.slice(0, 120)));
    page.on('console', (m) => { if (m.type() === 'error' && !expected) errors.push(m.text().slice(0, 120)); });
    page.on('response', (r) => { const u = new URL(r.url()); if (u.origin === origin && r.status() >= 400 && !(expected && norm(u.href) === norm(p.url))) errors.push(`${r.status()} ${u.pathname}`); });
    await load(page, p.url);
    await page.evaluate(() => document.fonts && document.fonts.ready);
    await page.waitForTimeout(300);
    const m = await page.evaluate(measure);
    byWidth[v.name] = m;
    for (let y = 0, i = 1; y < m.total && i <= MAX_SLICES; y += m.step, i++) {
      await page.evaluate(([y, r]) => { if (r) document.querySelector('[data-layout-check-region]').scrollTop = y; else scrollTo({ top: y, behavior: 'instant' }); }, [y, m.region]);
      await page.waitForTimeout(100);
      await page.screenshot({ path: path.join(out, `page${pi + 1}-${v.name}-${String(i).padStart(2, '0')}.png`) });
    }
    if (m.total > MAX_SLICES * m.step) capped.push(`page${pi + 1} at ${v.name}`);
    if (v.isMobile) {
      // Actions missing on a phone count as reachable only when opening a menu or disclosure shows them.
      m.lost = byWidth['1440'].actionNames.filter((n) => !m.actionNames.includes(n));
      const toggles = page.locator('[aria-expanded], [aria-haspopup], summary, [aria-controls]');
      for (let t = 0; m.lost.length && t < Math.min(await toggles.count(), 6); t++) {
        const el = toggles.nth(t);
        if (!(await el.isVisible().catch(() => false))) continue;
        await el.click({ timeout: 2000 }).catch(() => {});
        await page.waitForTimeout(300);
        const shown = await page.evaluate(() => [...document.querySelectorAll('a[href],button,[role=button],summary,input:not([type=hidden]),select,textarea')].filter(window.__lcVis).map((e) => (e.getAttribute('aria-label') || e.textContent || e.getAttribute('title') || '').trim().replace(/\s+/g, ' ').slice(0, 50)));
        m.lost = m.lost.filter((n) => !shown.includes(n));
        await page.keyboard.press('Escape').catch(() => {});
        await load(page, p.url);
      }
      // A stacked short row counts only when its items would fit side by side at this width.
      const stacked = Object.entries(byWidth['1440'].rows).filter(([k, r]) => r.oneRow && m.rows[k] && !m.rows[k].oneRow).map(([k]) => k);
      m.fitting = await page.evaluate((keys) => keys.filter((k) => {
        const el = [...document.querySelectorAll('body *')].find((e) => { const parts = []; for (let n = e; n && n !== document.body; n = n.parentElement) parts.unshift(n.tagName + ':' + [...n.parentElement.children].indexOf(n)); return parts.join('>') === k; });
        if (!el) return false;
        const saved = el.getAttribute('style');
        el.style.display = 'flex'; el.style.flexDirection = 'row'; el.style.flexWrap = 'nowrap'; el.style.gap = '12px';
        const kids = [...el.children];
        const savedKids = kids.map((c) => c.getAttribute('style'));
        kids.forEach((c) => { c.style.minWidth = '0'; c.style.flex = '1 1 0'; });
        const tops = kids.map((c) => Math.round(c.getBoundingClientRect().top));
        const box = el.getBoundingClientRect();
        const fits = tops.every((t) => Math.abs(t - tops[0]) < 12) && kids.every((c) => c.getBoundingClientRect().right <= box.right + 1) && kids.every((c) => c.scrollWidth <= c.clientWidth + 1 && ![...c.querySelectorAll('*')].some((d) => d.scrollWidth > d.clientWidth + 1 && /hidden|clip/.test(getComputedStyle(d).overflowX)));
        kids.forEach((c, i) => (savedKids[i] === null ? c.removeAttribute('style') : c.setAttribute('style', savedKids[i])));
        saved === null ? el.removeAttribute('style') : el.setAttribute('style', saved);
        return fits;
      }), stacked);
    }
    if (m.overflow > 0) fail(p.url, v.name, `scrolls sideways by ${m.overflow}px (${m.escaped.join(', ')})`);
    if (m.small.length) fail(p.url, v.name, `targets under 24x24: ${m.small.slice(0, 6).map((t) => `${t.name} ${t.w}x${t.h}`).join('; ')}`);
    if (errors.length) fail(p.url, v.name, `errors: ${[...new Set(errors)].slice(0, 3).join(' | ')}`);
    if (m.tiny.length) fail(p.url, v.name, `text under 9px: ${m.tiny.join('; ')}`);
    if (m.broken.length) fail(p.url, v.name, `a one-word label breaks across lines: ${m.broken.join('; ')}`);
    if (m.clipped.length) fail(p.url, v.name, `text cut off or scrolling sideways inside its box: ${m.clipped.join('; ')}`);
    if (m.covered.length) fail(p.url, v.name, `a control covers text: ${m.covered.join('; ')}`);
    if (m.placeholder.length) fail(p.url, v.name, `unfinished text: ${m.placeholder.join(', ')}`);
    if (v.isMobile && m.smallInputs) fail(p.url, v.name, `${m.smallInputs} form fields under 16px text, which zooms on focus`);
    await ctx.close();
  }
  const d = byWidth['1440'];
  p.title = d.title;
  for (const w of ['390', '320']) {
    const m = byWidth[w];
    const ratio = m.screens / d.screens;
    if (!opt.app && !d.longForm && ratio > LENGTH_BUDGET) fail(p.url, w, `page is ${ratio.toFixed(2)}x the desktop length in screens (budget ${LENGTH_BUDGET})`);
    if (!d.longForm && m.copyMin !== null && (m.copyMin < 13 || m.copyMax > 15.5)) review(p.url, w, `phone text from ${m.copyMin} to ${m.copyMax}px; supporting copy belongs at 13 to 15px`);
    for (const k of m.fitting) fail(p.url, w, `a row of ${d.rows[k].n} stacks on a phone although it fits side by side: "${d.rows[k].text}"`);
    m.tables.forEach((n, i) => { if (d.tables[i] && n < d.tables[i]) fail(p.url, w, `a table shows ${n} of its ${d.tables[i]} columns`); });
    if (m.lost.length) fail(p.url, w, `actions shown on desktop that no phone menu reveals: ${m.lost.slice(0, 5).join(', ')}`);
    for (const h of m.headings) { const wide = d.headings.find((x) => x.text === h.text); if (wide && h.lines > wide.lines + 1) fail(p.url, w, `heading "${h.text}" wraps to ${h.lines} lines against ${wide.lines} on desktop`); }
  }
  // The tab title leads with the page's own heading, except on the home page, whose title is the product.
  if (new URL(p.url).pathname !== '/' && d.h1 && d.title && !d.title.toLowerCase().startsWith(d.h1.toLowerCase().replace(/[.!?:]+$/, '').slice(0, 40))) fail(p.url, '1440', `tab title does not lead with the page heading: "${d.title}" against "${d.h1}"`);
  for (const [kind, href] of Object.entries(d.icons)) {
    if (!href) { fail(p.url, '1440', `no ${kind === 'apple' ? 'apple-touch-icon' : 'favicon'} link`); continue; }
    const r = await fetch(href).catch(() => null);
    if (!r || !r.ok) fail(p.url, '1440', `${kind === 'apple' ? 'apple-touch-icon' : 'favicon'} does not load: ${href}`);
  }
  if (opt.app && byWidth['1440'].docScrolls) fail(p.url, '1440', 'the app shell scrolls the whole page instead of one content region');
}
const titles = new Map();
for (const p of pages.filter((x) => x.title !== undefined)) { const t = p.title.trim(); if (!titles.has(t)) titles.set(t, new Map()); titles.get(t).set(new URL(p.url).pathname, p.url); }
for (const [t, byPath] of titles) if (byPath.size > 1) for (const u of byPath.values()) fail(u, '1440', `${byPath.size} pages share the tab title "${t || '(empty)'}"`);
await browser.close();
pages.forEach((p, i) => console.log(`page${i + 1} = ${new URL(p.url).pathname}${new URL(p.url).search}${p.from ? ` (reached from ${p.from})` : ""}`));
if (sampled.length) console.log(`Checked one page per route shape; these share a shape with a checked page: ${sampled.slice(0, 8).join(', ')}${sampled.length > 8 ? ` and ${sampled.length - 8} more` : ''}.`);
if (downloads.length) console.log(`Downloads, not pages: ${[...new Set(downloads)].join(', ')}.`);
if (capped.length) console.log(`Captured only the first ${MAX_SLICES} screens of ${capped.join(', ')}; raise --max-slices to see the rest.`);
if (notChecked.length) fail(start, '-', `linked pages not checked, over the ${MAX_PAGES}-page limit; pass them with --paths or raise --max-pages: ${notChecked.join('; ')}`);
console.log(`Checked ${pages.length} pages at ${WIDTHS.map((w) => w.name).join(', ')}. Captures in ${out}. Look at them before calling the layout done.`);
if (reviews.size) {
  console.log('To check by eye:');
  for (const [k, ps] of reviews) console.log(`- ${k} on ${[...ps].slice(0, 3).join(', ')}${ps.size > 3 ? ` and ${ps.size - 3} more` : ''}`);
}
if (failures.size) {
  console.log(`${failures.size} problems:`);
  for (const [k, { pages: ps, details: ds }] of failures) {
    const pl = [...ps], dl = [...ds];
    const on = pl.length > 3 ? `${pl.slice(0, 3).join(', ')} and ${pl.length - 3} more` : pl.join(', ');
    console.log(`- ${k} on ${on}${dl.length ? `: ${dl.slice(0, 6).join('; ')}${dl.length > 6 ? ` and ${dl.length - 6} more` : ''}` : ''}`);
  }
  process.exit(1);
}
console.log('No measured problems.');
