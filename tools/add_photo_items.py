"""Нарезать новые фотографии предметов и добавить их в манифест игры.

Берёт <имя>-source.png из assets/photo, отделяет предмет от фона (медиана по краю +
заливка внешней области, как в макете — не «белее 236», иначе ореолы), обрезает по
границам, вписывает в квадрат 256 и сохраняет <имя>.png. Затем дописывает глифы в
assets/photo/manifest.json, чтобы tools/build_art_bundle.py встроил их в игру.

Использование: python3 tools/add_photo_items.py clover bee ant ...
"""
from pathlib import Path
from collections import deque
import json, sys
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

root = Path(__file__).resolve().parents[1]
assets = root / 'assets/photo'

def keep_largest(alpha, min_share=0.04):
    a = np.array(alpha) > 128; h, w = a.shape; seen = np.zeros_like(a); parts = []
    for y in range(h):
        for x in range(w):
            if a[y, x] and not seen[y, x]:
                q = deque([(y, x)]); seen[y, x] = 1; px = []
                while q:
                    cy, cx = q.popleft(); px.append((cy, cx))
                    for ny, nx in ((cy-1, cx), (cy+1, cx), (cy, cx-1), (cy, cx+1)):
                        if 0 <= ny < h and 0 <= nx < w and a[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = 1; q.append((ny, nx))
                parts.append(px)
    if not parts:
        return alpha
    biggest = max(len(p) for p in parts); keep = np.zeros_like(a)
    for p in parts:
        if len(p) >= biggest * min_share:
            ys, xs = zip(*p); keep[np.array(ys), np.array(xs)] = True
    return Image.fromarray((keep * 255).astype('uint8'))

def cut(name, tolerance=34, max_side=220):
    src = assets / (name + '-source.png')
    assert src.exists(), 'нет файла ' + str(src)
    im = Image.open(src).convert('RGB'); a = np.array(im).astype(np.int16)
    border = np.concatenate([a[0:3].reshape(-1, 3), a[-3:].reshape(-1, 3),
                             a[:, 0:3].reshape(-1, 3), a[:, -3:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    near = ((np.abs(a - bg).max(axis=2)) <= tolerance).astype('uint8') * 255
    mask = Image.fromarray(np.pad(near, 1, constant_values=255)).copy()
    ImageDraw.floodfill(mask, (0, 0), 128, thresh=0)
    alpha = Image.fromarray(np.where(np.array(mask)[1:-1, 1:-1] == 128, 0, 255).astype('uint8'))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.6))
    alpha = keep_largest(alpha)
    bbox = alpha.getbbox(); assert bbox, (name, 'пустая вырезка')
    im = im.convert('RGBA'); im.putalpha(alpha); im = im.crop(bbox)
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    out = Image.new('RGBA', (256, 256))
    out.alpha_composite(im, ((256 - im.width) // 2, (256 - im.height) // 2))
    out.save(assets / (name + '.png'))
    return out

# glyph -> имя вырезки
GLYPHS = {
    '🍀': 'clover', '🔇': 'sign-mute', '🐝': 'bee', '🍒': 'cherry',
    '🅰️': 'letter-block', '🍞': 'bread', '🌳': 'tree', '🚲': 'bicycle', '🐜': 'ant',
}

if __name__ == '__main__':
    names = sys.argv[1:] or sorted(set(GLYPHS.values()))
    manifest_path = assets / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for name in names:
        cut(name)
        print('нарезано:', name)
    for glyph, name in GLYPHS.items():
        if name in names:
            manifest[glyph] = name
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('манифест:', len(manifest), 'предметов')
