// Static server with single-page-app fallback. Usage: node serve.mjs <dir> <port>
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const [dir, port] = process.argv.slice(2);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.ico': 'image/x-icon', '.json': 'application/json', '.woff2': 'font/woff2', '.txt': 'text/plain', '.xml': 'application/xml', '.webmanifest': 'application/manifest+json' };
http.createServer((req, res) => {
  const u = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  let f = path.join(dir, u);
  const tries = [f, f + '.html', path.join(f, 'index.html')];
  let hit = tries.find((t) => fs.existsSync(t) && fs.statSync(t).isFile());
  let status = 200;
  if (!hit) {
    // Fallback only for extensionless routes, like a single-page app host would.
    if (!path.extname(u) && fs.existsSync(path.join(dir, 'index.html')) && !fs.existsSync(path.join(dir, '404.html'))) hit = path.join(dir, 'index.html');
    else { status = 404; hit = fs.existsSync(path.join(dir, '404.html')) ? path.join(dir, '404.html') : null; }
  }
  if (!hit) { res.writeHead(404); return res.end('not found'); }
  res.writeHead(status, { 'content-type': types[path.extname(hit)] || 'application/octet-stream' });
  fs.createReadStream(hit).pipe(res);
}).listen(Number(port), '127.0.0.1');
