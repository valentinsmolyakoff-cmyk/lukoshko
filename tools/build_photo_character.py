"""Photo-based Tishka: fit garments to the measured landmarks of the real photograph.

Landmarks in the 600x524 source (the game draws in a 300x262 viewBox that fills the
same box, so every coordinate below is half of the measured pixel position):
  forehead top (455,300) · ear (415,315) · eye (487,347) · snout tip (550,385)
  belly line y=425 · front feet (405,455) and (425,465) · hind feet (95,450),(175,465)
"""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]


def svg(inner):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="262" viewBox="0 0 300 262">'
            '<defs>'
            '<linearGradient id="cloth" x2=".8" y2="1"><stop stop-color="#a0a175"/><stop offset=".5" stop-color="#727650"/><stop offset="1" stop-color="#434b31"/></linearGradient>'
            '<linearGradient id="felt" x2=".4" y2="1"><stop stop-color="#6a655d"/><stop offset=".5" stop-color="#383c3c"/><stop offset="1" stop-color="#262b2d"/></linearGradient>'
            '<linearGradient id="leather" x2=".5" y2="1"><stop stop-color="#a77f59"/><stop offset="1" stop-color="#4c3528"/></linearGradient>'
            '<linearGradient id="wool" x2="1" y2="1"><stop stop-color="#c18b68"/><stop offset="1" stop-color="#794431"/></linearGradient>'
            '<radialGradient id="lens" cx=".35" cy=".3" r=".8"><stop stop-color="#8ea08f" stop-opacity=".85"/><stop offset="1" stop-color="#25312c" stop-opacity=".92"/></radialGradient>'
            '<linearGradient id="gold" x2=".3" y2="1"><stop stop-color="#f0d489"/><stop offset=".45" stop-color="#c6a451"/><stop offset="1" stop-color="#8c712f"/></linearGradient>'
            '</defs>' + inner + '</svg>')


parts = {
    'base': '',
    # Wool beanie sitting on the real forehead; brim follows the skull curve.
    'hat': ('<g transform="rotate(9 228 150)">'
            '<path d="M206 149 q2 -21 22 -22 q20 1 22 22Z" fill="url(#felt)" stroke="#2f312c" stroke-width=".9"/>'
            '<path d="M204 149 q24 -6 48 0 l1 7 q-25 6 -50 0Z" fill="#7d6448" stroke="#3a3229" stroke-width=".7"/>'
            '<path d="M212 133 q10 -14 17 -14 q8 0 14 14" fill="none" stroke="#9a958a" stroke-width=".8" opacity=".55"/>'
            '<circle cx="231" cy="128" r="4.6" fill="#cbb08a" stroke="#7a6350" stroke-width=".6"/>'
            '</g>'),
    'crown': ('<g transform="rotate(9 228 150)">'
              '<path d="M208 149 l-3 -22 12 10 11 -19 11 19 12 -10 -3 22Z" fill="url(#gold)" stroke="#7d6229" stroke-width=".9"/>'
              '<path d="M208 149 q20 5 41 0" fill="none" stroke="#f4e0a6" stroke-width="2.4"/>'
              '<circle cx="229" cy="136" r="2.6" fill="#963b2e"/>'
              '<circle cx="216" cy="140" r="1.7" fill="#7d9a52"/><circle cx="242" cy="140" r="1.7" fill="#7d9a52"/>'
              '</g>'),
    'glasses': ('<g>'
                '<path d="M214 164 q-4 -6 6 -7" fill="none" stroke="#333839" stroke-width="1.5"/>'
                '<circle cx="243" cy="174" r="7.4" fill="url(#lens)" stroke="#2e3233" stroke-width="1.6"/>'
                '<circle cx="252" cy="176" r="6.2" fill="url(#lens)" stroke="#2e3233" stroke-width="1.3" opacity=".75"/>'
                '<path d="M236 171 l3 2" stroke="#3a3f40" stroke-width="1.5"/>'
                '<path d="M239 170 q4 -3 7 -1" fill="none" stroke="#cfd8cf" stroke-width="1.1" opacity=".7"/>'
                '</g>'),
    # Scarf wraps the real neck, tail hangs down the chest.
    'scarf': ('<g>'
              '<path d="M228 172 q16 8 26 20 q-7 6 -14 0 q-9 -9 -16 -13Z" fill="url(#wool)" stroke="#5f3b2c" stroke-width=".8"/>'
              '<path d="M231 177 q13 9 22 19" fill="none" stroke="#e6c4ab" stroke-width=".8" opacity=".55"/>'
              '<path d="M239 190 q-5 9 -2 17 q4 1 6 -1 q-3 -8 2 -13Z" fill="url(#wool)" stroke="#5f3b2c" stroke-width=".7"/>'
              '</g>'),
    # Mittens sit on the real front paws.
    'mittens': ('<g fill="url(#wool)" stroke="#6e4d3b" stroke-width=".7">'
                '<ellipse cx="203" cy="227" rx="10" ry="5.4" transform="rotate(-6 203 227)"/>'
                '<ellipse cx="213" cy="233" rx="8" ry="4.6" transform="rotate(8 213 233)"/>'
                '</g><path d="M196 227 l4 -2 M206 233 l4 -2" stroke="#dcbca2" stroke-width="1.6"/>'),
    # Four real feet: two front, two hind.
    'shoes': ('<g fill="url(#leather)" stroke="#3d2c21" stroke-width=".7">'
              '<path d="M196 226 q6 -5 12 0 l1 5 5 2 q1 4 -4 4 h-13 q-5 -1 -2 -6Z"/>'
              '<path d="M207 231 q5 -4 10 0 l1 5 4 2 q1 3 -4 4 h-11 q-4 -1 -1 -5Z"/>'
              '<path d="M39 223 q6 -5 11 0 l1 5 5 2 q1 4 -4 4 h-12 q-5 -1 -2 -6Z"/>'
              '<path d="M81 228 q5 -4 10 0 l1 5 4 2 q1 3 -4 3 h-11 q-4 -1 -1 -5Z"/>'
              '</g><path d="M196 236 h13 M207 241 h11 M39 233 h12 M81 237 h11" stroke="#d8c2a1" stroke-width="1.3"/>'),
    # Canvas backpack on the real back, straps over the shoulders.
    'backpack': ('<g>'
                 '<path d="M139 96 q26 -6 46 8 l-2 48 q-22 9 -47 -2Z" fill="url(#cloth)" stroke="#4a5336" stroke-width="1.1"/>'
                 '<path d="M141 116 q22 7 43 1" fill="none" stroke="#3f4730" stroke-width="1"/>'
                 '<rect x="146" y="122" width="27" height="20" rx="4" fill="#989a70" stroke="#5a6343"/>'
                 '<path d="M152 96 q10 -13 20 2" fill="none" stroke="#7a6446" stroke-width="3"/>'
                 '<path d="M138 104 q10 24 4 46" fill="none" stroke="#7a6446" stroke-width="3.2"/>'
                 '<path d="M159 129 v7" stroke="#d3b78a" stroke-width="2.4"/>'
                 '</g>'),
}

p = root / 'tools/art-source.json'
data = json.loads(p.read_text())
data['hero'] = {k: svg(v) for k, v in parts.items()}
p.write_text(json.dumps(data, ensure_ascii=False))
print('garment layers:', ', '.join(parts))
