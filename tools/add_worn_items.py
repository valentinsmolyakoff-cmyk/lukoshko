"""Вырезать вещи в «надетом» виде (снятые в нужном ракурсе) и связать их с глифами.

Инвентарь показывает студийное фото предмета, а на ёжика надевается та же вещь,
снятая так, как она сидит: сбоку, с драпировкой и открытым низом. Поэтому для
каждого глифа может быть две картинки: обычная (manifest.json) и «надетая»
(worn.json). Запуск: python3 tools/add_worn_items.py
"""
from pathlib import Path
from collections import deque
import json
import numpy as np
from PIL import Image, ImageFilter
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from defringe import defringe

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/photo'

# глиф -> имя вырезки в «надетом» виде
# 👑 корону оставляем в студийном виде: у неё тонкие светлые зубцы, вырезка рвётся
WORN = {
    '🎩': 'hat-knit-worn', '🕶️': 'glasses-worn', '🧣': 'scarf-knit-worn',
    '🧤': 'mittens-knit-worn', '👟': 'boots-leather-worn', '🎒': 'backpack-canvas-worn',
}
TOL = {'glasses-worn': 30, 'boots-leather-worn': 40, 'hat-knit-worn': 45,
       'scarf-knit-worn': 50, 'mittens-knit-worn': 40, 'backpack-canvas-worn': 45}


def largest(arr, share=0.04):
    h, w = arr.shape
    seen = np.zeros_like(arr); parts = []
    for y in range(h):
        for x in range(w):
            if arr[y, x] and not seen[y, x]:
                q = deque([(y, x)]); seen[y, x] = 1; px = []
                while q:
                    cy, cx = q.popleft(); px.append((cy, cx))
                    for ny, nx in ((cy-1, cx), (cy+1, cx), (cy, cx-1), (cy, cx+1)):
                        if 0 <= ny < h and 0 <= nx < w and arr[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = 1; q.append((ny, nx))
                parts.append(px)
    # обрывки фона у края кадра — это не предмет: выкидываем всё, что касается границы
    big = max(len(p) for p in parts); keep = np.zeros_like(arr)
    for p in parts:
        ys = np.array([q[0] for q in p]); xs = np.array([q[1] for q in p])
        touches = ys.min() == 0 or xs.min() == 0 or ys.max() == h - 1 or xs.max() == w - 1
        if len(p) >= big * share and not touches:
            keep[ys, xs] = True
    if not keep.any():
        for p in parts:
            if len(p) >= big * share:
                ys, xs = zip(*p); keep[np.array(ys), np.array(xs)] = True
    return keep


def cut(name, tol, max_side=220):
    src = ASSETS / (name + '-source.png')
    im = Image.open(src).convert('RGB'); a = np.array(im).astype(np.int16)
    border = np.concatenate([a[0:3].reshape(-1, 3), a[-3:].reshape(-1, 3),
                             a[:, 0:3].reshape(-1, 3), a[:, -3:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    # просветы внутри предмета (петля шарфа, лямка) тоже убираем: не только заливка от края
    near = np.abs(a - bg).max(axis=2) <= tol
    alpha = Image.fromarray(np.where(near, 0, 255).astype('uint8'))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.6))
    keep = largest(np.array(alpha) > 128)
    alpha = Image.fromarray((keep * 255).astype('uint8'))
    bbox = alpha.getbbox()
    assert bbox, (name, 'пустая вырезка')
    im = im.convert('RGBA'); im.putalpha(alpha); im = im.crop(bbox)
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    out = Image.new('RGBA', (256, 256))
    out.alpha_composite(im, ((256 - im.width) // 2, (256 - im.height) // 2))
    out = defringe(out)
    out.save(ASSETS / (name + '.png'))
    return out


if __name__ == '__main__':
    worn_path = ASSETS / 'worn.json'
    worn = json.loads(worn_path.read_text(encoding='utf-8')) if worn_path.exists() else {}
    for glyph, name in WORN.items():
        cut(name, TOL.get(name, 34))
        worn[glyph] = name
        print('надетый вид:', glyph, '->', name)
    worn_path.write_text(json.dumps(worn, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('worn.json:', len(worn))
