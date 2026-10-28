"""Собрать photo-materials.js: настоящие материалы одежды из фотографий вещей.

Берёт те же вырезки, что и макет (tools/photo_materials.js), и сохраняет их
в виде обычного объекта — его читает photo.js в игре.
"""
from pathlib import Path
import json, re

root = Path(__file__).resolve().parents[1]
src = (root / 'tools/photo_materials.js').read_text()
block = src.split('const defs=`', 1)[1].split('`;', 1)[0]
pairs = re.findall(r'<pattern id="([\w-]+)"[^>]*><image href="data:image/png;base64,([^"]+)"', block)
assert pairs, 'материалы не найдены'

data = {name: b64 for name, b64 in pairs}
out = ('/* Реальные материалы одежды: вязка, кожа, холст, шерсть, золото — вырезаны\n'
       '   с фотографий этих же вещей и приведены к серому, чтобы цвет оставался игровым. */\n'
       'window.PHOTO_MATERIALS=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
(root / 'photo-materials.js').write_text(out)
print('photo-materials.js:', ', '.join(data), '|', len(out.encode()), 'bytes')
