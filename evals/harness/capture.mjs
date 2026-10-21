// Captures and measures a built web surface at four widths.
// Usage: node capture.mjs <start-url> <out-dir> [--max-pages=8] [--paths=/a,/b]
// Crawls same-origin links from the start URL (plus any --paths), and for each page and
// viewport writes one-screen slices and a metrics record to <out-dir>/metrics.json.
import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const [start, out, ...rest] = process.argv.slice(2);
const opt = Object.fromEntries(rest.map((a) => a.replace(/^--/, '').split('=')));
const maxPages = Number(opt['max-pages'] || 8);
const extra = (opt.paths || '').split(',').filter(Boolean);
const maxSlices = Number(opt['max-slices'] || 10);

const VIEWPORTS = [
  { name: '1440', width: 1440, height: 900 },
  { name: '2560', width: 2560, height: 1440 },
  { name: '390', width: 390, height: 844, deviceScaleFactor: 3, isMobile: true, hasTouch: true },
  { name: '320', width: 320, height: 700, isMobile: true, hasTouch: true },
];

await fs.mkdir(path.join(out, 'shots'), { recursive: true });
const browser = await chromium.launch();
const origin = new URL(start).origin;
const key = (u) => { const x = new URL(u); return x.pathname + x.search; };

// Discover pages at desktop width.
const queue = [start, ...extra.map((p) => new URL(p, start).href)];
const seen = new Set();
const pages = [];
const linkStatus = {};
{
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  while (queue.length && pages.length < maxPages) {
    const url = queue.shift();
    const k = key(url);
    if (seen.has(k)) continue;
    seen.add(k);
    let status = 0;
    try {
      const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      status = resp ? resp.status() : 200;
    } catch (e) { status = -1; }
    linkStatus[k] = status;
    if (status < 200 || status >= 400) continue;
    pages.push(url);
    const hrefs = await page.$$eval('a[href]', (as) => as.map((a) => a.href));
    for (const h of hrefs) {
      if (!h.startsWith(origin)) continue;
      const u = new URL(h); u.hash = '';
      if (!seen.has(key(u.href))) queue.push(u.href);
    }
  }
  // Check the status of every remaining discovered same-origin link without capturing it.
  for (const url of queue) {
    const k = key(url);
    if (k in linkStatus) continue;
    try { const r = await page.request.get(url); linkStatus[k] = r.status(); } catch { linkStatus[k] = -1; }
  }
  await ctx.close();
}

const measure = () => {
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 1 && r.height > 1 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity !== 0; };
  const R = (e) => { const r = e.getBoundingClientRect(); return { x: Math.round(r.x), y: Math.round(r.y + scrollY), w: Math.round(r.width * 10) / 10, h: Math.round(r.height * 10) / 10 }; };
  const label = (e) => (e.getAttribute('aria-label') || e.textContent || e.getAttribute('title') || e.getAttribute('placeholder') || e.tagName).trim().replace(/\s+/g, ' ').slice(0, 60);
  const lines = (e) => { const ys = new Set(); const w = document.createTreeWalker(e, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) { for (let i = 0; i < n.length; i++) { if (!n.textContent[i].trim()) continue; const r = new Range(); r.setStart(n, i); r.setEnd(n, i + 1); for (const b of r.getClientRects()) if (b.width && b.height) ys.add(Math.round(b.y)); } } return ys.size; };
  const de = document.documentElement;
  const W = innerWidth;
  // Interactive targets.
  const targets = [...document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=tab],[role=link],[role=menuitem],[role=checkbox],[role=switch]')].filter(vis).map((e) => {
    const inline = e.tagName === 'A' && !!e.closest('p,li:not(nav li)') && getComputedStyle(e).display === 'inline';
    return { label: label(e), tag: e.tagName.toLowerCase(), inline, ...R(e) };
  });
  const undersized = targets.filter((t) => t.w < 24 || t.h < 24);
  // Elements escaping the viewport horizontally, outside any horizontal scroller.
  const escaped = [];
  for (const e of document.querySelectorAll('body *')) {
    if (!vis(e)) continue;
    const r = e.getBoundingClientRect();
    if (r.right <= W + 1 && r.left >= -1) continue;
    let p = e.parentElement, contained = false;
    while (p && p !== document.body) { const s = getComputedStyle(p); if (/auto|scroll|hidden|clip/.test(s.overflowX)) { contained = true; break; } p = p.parentElement; }
    if (!contained && getComputedStyle(e).position !== 'fixed') escaped.push({ el: e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.split(/\s+/)[0] : ''), left: Math.round(r.left), right: Math.round(r.right) });
    if (escaped.length > 20) break;
  }
  // Text sizes.
  const textEls = [...document.querySelectorAll('p,li,dd,td,span,a,label,small,figcaption,blockquote')].filter((e) => vis(e) && [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 2));
  const sizes = textEls.map((e) => parseFloat(getComputedStyle(e).fontSize));
  const paras = [...document.querySelectorAll('p')].filter(vis);
  const pSizes = paras.map((e) => parseFloat(getComputedStyle(e).fontSize)).sort((a, b) => a - b);
  const median = (a) => (a.length ? a[Math.floor(a.length / 2)] : null);
  const inputs = [...document.querySelectorAll('input:not([type=checkbox]):not([type=radio]):not([type=hidden]),textarea,select')].filter(vis).map((e) => ({ label: label(e), font: parseFloat(getComputedStyle(e).fontSize) }));
  // Reading measure: widest paragraph in approximate characters.
  const measureCh = paras.map((e) => { const fs = parseFloat(getComputedStyle(e).fontSize); return { text: e.textContent.trim().slice(0, 40), ch: Math.round(e.getBoundingClientRect().width / (fs * 0.5)) }; }).sort((a, b) => b.ch - a.ch).slice(0, 3);
  // Headings and their line counts.
  const headings = [...document.querySelectorAll('h1,h2,h3')].filter(vis).map((e) => ({ tag: e.tagName.toLowerCase(), text: e.textContent.trim().replace(/\s+/g, ' ').slice(0, 60), font: parseFloat(getComputedStyle(e).fontSize), lines: lines(e) }));
  // Small groups (2 to 4 visible children) and whether their children share a row.
  const groups = [...document.querySelectorAll('body *')].filter((e) => vis(e) && /grid|flex/.test(getComputedStyle(e).display)).map((e) => {
    const kids = [...e.children].filter(vis);
    if (kids.length < 2 || kids.length > 4) return null;
    const tops = kids.map((k) => Math.round(k.getBoundingClientRect().top));
    const sameRow = tops.every((t) => Math.abs(t - tops[0]) < 8);
    const txt = e.textContent.trim().replace(/\s+/g, ' ').slice(0, 50);
    return { sig: e.tagName.toLowerCase() + (typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.') : '') + '|' + txt, n: kids.length, sameRow, h: Math.round(e.getBoundingClientRect().height) };
  }).filter(Boolean);
  // First screen: the region holding the h1.
  const h1 = document.querySelector('h1');
  let hero = null;
  if (h1) { let s = h1; while (s.parentElement && s.parentElement !== document.body && s.parentElement.tagName !== 'MAIN' && s.getBoundingClientRect().width < W - 2) s = s.parentElement; hero = { bottom: Math.round(s.getBoundingClientRect().bottom + scrollY), tag: s.tagName.toLowerCase() }; }
  // Placeholder or unfinished content.
  const bodyText = document.body.innerText;
  const placeholder = [...new Set((bodyText.match(/lorem ipsum|\bTODO\b|\bTBD\b|placeholder|coming soon|your (text|content) here|\[insert|xxx+|undefined|NaN|\[object Object\]/gi) || []).map((s) => s.toLowerCase()))];
  const brokenImages = [...document.images].filter((i) => i.complete && i.naturalWidth === 0 && vis(i)).map((i) => i.getAttribute('src'));
  const ids = new Set([...document.querySelectorAll('[id]')].map((e) => e.id));
  const deadAnchors = [...document.querySelectorAll('a[href^="#"]')].map((a) => a.getAttribute('href')).filter((h) => h === '#' || (h.length > 1 && !ids.has(decodeURIComponent(h.slice(1)))));
  const meta = (sel) => document.querySelector(sel)?.getAttribute('content') || document.querySelector(sel)?.getAttribute('href') || null;
  return {
    url: location.href, title: document.title, lang: de.lang || null,
    width: W, height: innerHeight, docHeight: de.scrollHeight, screens: Math.round((de.scrollHeight / innerHeight) * 100) / 100,
    overflowX: de.scrollWidth - de.clientWidth, docScrolls: de.scrollHeight > innerHeight + 1,
    rootGutter: getComputedStyle(de).scrollbarGutter,
    escaped, targetsCount: targets.length, undersized, undersizedNonInline: undersized.filter((t) => !t.inline).length,
    textMin: sizes.length ? Math.min(...sizes) : null, textUnder12: sizes.filter((s) => s < 12).length,
    pMedian: median(pSizes), inputs, measureCh, headings, groups, hero, placeholder, brokenImages, deadAnchors,
    head: { description: meta('meta[name=description]'), canonical: meta('link[rel=canonical]'), icon: meta('link[rel~=icon]'), ogTitle: meta('meta[property="og:title"]'), ogDescription: meta('meta[property="og:description"]'), ogImage: meta('meta[property="og:image"]'), twitterCard: meta('meta[name="twitter:card"]'), viewport: meta('meta[name=viewport]'), themeColor: meta('meta[name=theme-color]') },
  };
};

const results = [];
for (const [pi, url] of pages.entries()) {
  for (const v of VIEWPORTS) {
    const ctx = await browser.newContext({ viewport: { width: v.width, height: v.height }, deviceScaleFactor: v.deviceScaleFactor || 1, isMobile: !!v.isMobile, hasTouch: !!v.hasTouch, reducedMotion: 'reduce' });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push('pageerror: ' + e.message.slice(0, 200)));
    page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text().slice(0, 200)); });
    try { await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 }); } catch (e) { errors.push('goto: ' + e.message.slice(0, 120)); }
    await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {});
    await page.waitForTimeout(400);
    const m = await page.evaluate(measure);
    m.errors = errors; m.viewport = v.name; m.page = pi;
    // One-screen slices, from the document or the app's single scrolling region.
    m.shots = [];
    const scroller = await page.evaluate(() => {
      const de = document.documentElement;
      if (de.scrollHeight > innerHeight + 1) return null;
      const cands = [...document.querySelectorAll('body *')].filter((e) => { const s = getComputedStyle(e); return /auto|scroll/.test(s.overflowY) && e.scrollHeight > e.clientHeight + 1 && e.clientHeight > innerHeight * 0.4; });
      cands.sort((a, b) => b.clientWidth * b.clientHeight - a.clientWidth * a.clientHeight);
      if (!cands[0]) return null;
      cands[0].setAttribute('data-capture-scroller', '1');
      return { total: cands[0].scrollHeight, view: cands[0].clientHeight };
    });
    m.regionScreens = scroller ? Math.round((scroller.total / scroller.view) * 100) / 100 : null;
    const total = scroller ? scroller.total : m.docHeight;
    const step = scroller ? scroller.view : v.height;
    for (let y = 0, i = 1; y < total && i <= maxSlices; y += step, i++) {
      await page.evaluate(([y, s]) => { if (s) document.querySelector('[data-capture-scroller]').scrollTop = y; else scrollTo({ top: y, behavior: 'instant' }); }, [y, !!scroller]);
      await page.waitForTimeout(150);
      const f = `p${pi}-${v.name}-${String(i).padStart(2, '0')}.png`;
      await page.screenshot({ path: path.join(out, 'shots', f) });
      m.shots.push(f);
    }
    results.push(m);
    await ctx.close();
  }
}
await browser.close();
const truncated = { pagesNotCaptured: queue.filter((u) => !pages.includes(u)).map(key), slicesCapped: results.filter((r) => r.shots.length >= maxSlices).map((r) => `${key(pages[r.page])} @${r.viewport}`) };
await fs.writeFile(path.join(out, 'metrics.json'), JSON.stringify({ start, pages, linkStatus, truncated, results }, null, 2));
if (truncated.pagesNotCaptured.length || truncated.slicesCapped.length) console.log('TRUNCATED: raise --max-pages or --max-slices, or capture these with --paths', JSON.stringify(truncated));

// Summary line per page.
for (const [pi, url] of pages.entries()) {
  const r = Object.fromEntries(results.filter((x) => x.page === pi).map((x) => [x.viewport, x]));
  const ratio = (a) => (r[a] && r['1440'] ? Math.round(((r[a].regionScreens || r[a].screens) / (r['1440'].regionScreens || r['1440'].screens)) * 100) / 100 : null);
  console.log(JSON.stringify({ page: key(url), screens: VIEWPORTS.map((v) => r[v.name]?.screens), ratio390: ratio('390'), ratio320: ratio('320'), overflow: VIEWPORTS.map((v) => r[v.name]?.overflowX), undersized: VIEWPORTS.map((v) => r[v.name]?.undersizedNonInline), p320: r['320']?.pMedian, errors: r['1440']?.errors.length, placeholder: r['1440']?.placeholder }));
}
const bad = Object.entries(linkStatus).filter(([, s]) => s < 200 || s >= 400);
if (bad.length) console.log('BROKEN LINKS', JSON.stringify(bad));
