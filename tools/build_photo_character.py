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
    # Шапка лежит на макушке: основание повторяет склон головы (он поднимается вправо),
    # поэтому наклон 21°, а сама шапка сидит между иголками и ухом, не закрывая глаз.
    'hat': ('<g transform="rotate(21 224 132)">'
            '<path d="M204 136 q1 -20 21 -21 q20 1 21 21Z" fill="url(#felt)" stroke="#2f312c" stroke-width=".9"/>'
            '<path d="M202 136 q23 -6 46 0 l1 6 q-24 6 -48 0Z" fill="#7d6448" stroke="#3a3229" stroke-width=".7"/>'
            '<path d="M211 121 q8 -12 14 -12 q7 0 13 12" fill="none" stroke="#9a958a" stroke-width=".8" opacity=".5"/>'
            '<circle cx="224" cy="114" r="4" fill="#cbb08a" stroke="#7a6350" stroke-width=".6"/>'
            '</g>'),
    'crown': ('<g transform="rotate(19 224 130)">'
              '<path d="M204 134 l-3 -19 11 9 11 -16 11 16 11 -9 -3 19Z" fill="url(#gold)" stroke="#7d6229" stroke-width=".9"/>'
              '<path d="M204 134 q20 5 40 0" fill="none" stroke="#f4e0a6" stroke-width="2.1"/>'
              '<circle cx="221" cy="125" r="2.3" fill="#963b2e"/>'
              '<circle cx="211" cy="128" r="1.5" fill="#7d9a52"/><circle cx="233" cy="128" r="1.5" fill="#7d9a52"/>'
              '</g>'),
    # Очки: одно стекло на глазу (он под ухом, чуть выше линии морды) и дужка к уху.
    'glasses': ('<g>'
                '<circle cx="242" cy="178" r="7.2" fill="url(#lens)" stroke="#2e3233" stroke-width="1.7"/>'
                '<path d="M236 173 q4 -3 8 -1" fill="none" stroke="#eef3ee" stroke-width="1.2" opacity=".8"/>'
                '<path d="M234 175 q-9 -2 -16 -6" fill="none" stroke="#333839" stroke-width="1.6"/>'
                '</g>'),
    # Шарф: полоса обнимает шею там, где голова переходит в грудь, ниже подбородка,
    # и два конца свисают вниз с бахромой — как настоящий шерстяной шарф.
    'scarf': ('<g>'
              '<path d="M194 194 C 206 190, 222 192, 234 200 L 230 216 C 218 208, 204 206, 192 208 Z" fill="url(#wool)" stroke="#5f3b2c" stroke-width=".9"/>'
              '<path d="M196 200 C 208 197, 220 199, 231 205" fill="none" stroke="#e6c4ab" stroke-width="1" opacity=".5"/>'
              '<path d="M196 196 l0 11 M204 194 l0 11 M212 194 l0 11 M220 197 l0 11" stroke="#6b3f2d" stroke-width=".8" opacity=".45"/>'
              '<path d="M199 210 q-3 15 1 26 q6 2 10 -1 q-4 -13 0 -23Z" fill="url(#wool)" stroke="#5f3b2c" stroke-width=".8"/>'
              '<path d="M213 212 q-2 12 2 21 q6 1 9 -2 q-4 -10 -1 -18Z" fill="url(#wool)" stroke="#5f3b2c" stroke-width=".8"/>'
              '<path d="M201 236 l2 5 M206 236 l2 5 M211 235 l2 5 M216 233 l2 5 M221 233 l2 5" stroke="#8a563c" stroke-width="1.2"/>'
              '</g>'),
    # Перчатки — на передних лапках под грудью.
    'mittens': ('<g fill="url(#wool)" stroke="#6e4d3b" stroke-width=".8">'
                '<path d="M198 222 q9 -5 17 1 q1 7 -8 8 q-9 0 -9 -9Z"/>'
                '<path d="M212 229 q9 -5 16 1 q1 7 -7 8 q-9 0 -9 -9Z"/>'
                '</g><path d="M198 227 h17 M212 234 h16" stroke="#dcbca2" stroke-width="1.4"/>'),
    # Ботинки — на задних ножках, чтобы не спорить с перчатками.
    'shoes': ('<g fill="url(#leather)" stroke="#3d2c21" stroke-width=".8">'
              '<path d="M40 220 q7 -6 13 0 l2 6 5 2 q1 4 -4 4 h-15 q-5 -1 -2 -6Z"/>'
              '<path d="M82 226 q7 -6 13 0 l2 6 5 2 q1 4 -4 4 h-15 q-5 -1 -2 -6Z"/>'
              '</g><path d="M40 232 h20 M82 238 h20" stroke="#d8c2a1" stroke-width="1.3"/>'),
    # Холщовый рюкзак на спине: клапан, шов, лямка через плечо.
    'backpack': ('<g transform="rotate(-8 122 132)">'
                 '<path d="M96 112 q26 -9 52 4 l-2 52 q-24 11 -52 -1Z" fill="url(#cloth)" stroke="#4a5336" stroke-width="1.1"/>'
                 '<path d="M96 130 q26 8 52 1 l0 12 q-26 7 -52 -1Z" fill="#8b8d63" stroke="#4a5336" stroke-width=".8"/>'
                 '<path d="M100 150 q22 7 44 0" fill="none" stroke="#3f4730" stroke-width=".9"/>'
                 '<rect x="108" y="156" width="24" height="16" rx="4" fill="#989a70" stroke="#5a6343"/>'
                 '<path d="M112 112 q10 -12 20 0" fill="none" stroke="#7a6446" stroke-width="3"/>'
                 '<path d="M146 118 q14 16 22 40" fill="none" stroke="#7a6446" stroke-width="3"/>'
                 '<path d="M114 163 v7" stroke="#d3b78a" stroke-width="2.2"/>'
                 '</g>'),
}

p = root / 'tools/art-source.json'
data = json.loads(p.read_text())
data['hero'] = {k: svg(v) for k, v in parts.items()}
p.write_text(json.dumps(data, ensure_ascii=False))
print('garment layers:', ', '.join(parts))
