"""Убрать светлую кайму по краю вырезки: подтянуть цвет изнутри и подсушить альфу.

Белая кайма появляется, когда фото снимали на светлом фоне и вырезали по цвету.
На тёмном фоне (спина ёжика) она читается как «наклейка». Здесь RGB под краем
заменяется на цвет изнутри предмета, а альфа чуть поджимается.
"""
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageFilter

def defringe(im, erode=1):
    a = np.array(im)[:, :, 3].astype(np.float32) / 255.0
    rgb = np.array(im.convert('RGB')).astype(np.float32)
    solid = a > 0.85
    filled = rgb.copy()
    have = solid.copy()
    for _ in range(6):                      # разносим цвет вглубь прозрачной каймы
        acc = np.zeros_like(rgb); cnt = np.zeros(a.shape, np.float32)
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
            sh = np.roll(np.roll(filled, dy, 0), dx, 1)
            shave = np.roll(np.roll(have, dy, 0), dx, 1)
            acc += sh * shave[..., None]; cnt += shave
        grow = (~have) & (cnt > 0)
        filled[grow] = (acc[grow] / cnt[grow][..., None])
        have = have | grow
    alpha = Image.fromarray((a * 255).astype('uint8'))
    if erode:
        alpha = alpha.filter(ImageFilter.MinFilter(erode * 2 + 1))
    alpha = np.array(alpha).astype(np.float32) / 255.0
    out = np.dstack([filled, alpha * 255]).astype('uint8')
    return Image.fromarray(out, 'RGBA')

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    names = sys.argv[1:]
    for n in names:
        p = root / 'assets/photo' / (n + '.png')
        im = Image.open(p).convert('RGBA')
        defringe(im).save(p)
        print('почищено:', n)
