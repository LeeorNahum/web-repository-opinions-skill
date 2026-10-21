"""Contact sheets: one image per page and viewport, all slices side by side.
Usage: python sheets.py <capture-dir>"""
import json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw
out = Path(sys.argv[1])
data = json.loads((out / 'metrics.json').read_text(encoding='utf-8'))
for r in data['results']:
    w = 300 if int(r['viewport']) < 500 else 640
    imgs = []
    for f in r['shots']:
        im = Image.open(out / 'shots' / f).convert('RGB')
        imgs.append(im.resize((w, round(im.height * w / im.width)), Image.Resampling.LANCZOS))
    if not imgs:
        continue
    cols = min(len(imgs), 6 if w == 300 else 3)
    h = max(i.height for i in imgs) + 24
    sheet = Image.new('RGB', (cols * (w + 8), math.ceil(len(imgs) / cols) * h), '#bbbbbb')
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(imgs):
        x, y = i % cols * (w + 8), i // cols * h
        d.text((x + 4, y + 5), r['shots'][i], fill='black')
        sheet.paste(im, (x, y + 22))
    dest = out / f"sheet-p{r['page']}-{r['viewport']}.png"
    sheet.save(dest, optimize=True)
    print(dest)
