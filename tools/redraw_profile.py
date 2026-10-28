"""Natural side-on Tishka: original artwork. Run, then build_art_bundle.py."""
from pathlib import Path
import json,math,random
root=Path(__file__).resolve().parents[1]
def hero(o={}):
 rng=random.Random(42);needles=[]
 for _ in range(185):
  x=rng.uniform(48,211);y=rng.uniform(108,212)
  if ((x-132)/91)**2+((y-171)/65)**2>1:continue
  dx=(x-110)*.11-5;dy=-rng.uniform(7,14)
  needles.append(f'<path d="M{x:.1f} {y:.1f} l{dx:.1f} {dy:.1f}" stroke="{rng.choice(["#b69c78","#d6c09a","#806b53"])}" stroke-width="{rng.uniform(1.1,2):.1f}" stroke-linecap="round"/>')
 fur='#d5979d' if o.get('paws') else 'url(#fur)'
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="262" viewBox="0 0 300 262">
 <defs><linearGradient id="spine" x2=".2" y2="1"><stop stop-color="#675342"/><stop offset="1" stop-color="#3e352e"/></linearGradient><linearGradient id="fur" x2=".6" y2="1"><stop stop-color="#e9d8b6"/><stop offset="1" stop-color="#b69a76"/></linearGradient></defs>
 <ellipse cx="153" cy="240" rx="111" ry="8" fill="#725d42" opacity=".14"/>
 <path d="M53 214 q-20 2 -15 9 l23 -5" fill="#a28b6c"/>
 <ellipse cx="94" cy="226" rx="19" ry="6" fill="#867258"/><ellipse cx="215" cy="225" rx="16" ry="6" fill="#867258"/>
 <path d="M43 199 Q35 153 69 122 Q94 98 134 104 Q183 105 206 140 Q225 166 219 211 Q172 234 77 227 Q48 224 43 199Z" fill="url(#spine)"/>
 <g opacity=".9">{''.join(needles)}</g>
 <path d="M147 192 Q178 174 207 187 Q231 203 223 223 Q183 235 129 226 Q115 207 147 192Z" fill="url(#fur)"/>
 <path d="M179 158 Q201 148 220 165 Q241 183 273 191 Q282 195 273 201 Q248 209 226 214 Q197 220 181 208 Q166 188 179 158Z" fill="url(#fur)"/>
 <ellipse cx="192" cy="166" rx="10" ry="13" fill="#9f8669"/><ellipse cx="194" cy="166" rx="6" ry="8" fill="#c4aa8c"/>
 <ellipse cx="221" cy="177" rx="4.4" ry="5" fill="#29251f"/><circle cx="222" cy="175.5" r="1.3" fill="#fff9e9"/>
 <ellipse cx="275" cy="194" rx="7" ry="4.5" fill="#332d27"/><ellipse cx="274" cy="192.6" rx="2" ry=".8" fill="#c5bba9"/>
 <path d="M246 201 q8 1 17 -2" stroke="#8c765d" stroke-width="1.1" fill="none"/>
 <path d="M205 192 l5 2 m4 -1 5 2 m-11 8 5 1 m14 -3 4 1 m-33 -18 4 1" stroke="#9d866a" stroke-width="1" stroke-linecap="round" opacity=".6"/>
 {('<g><path d="M111 140 q23 -7 46 4 l-1 51 q-23 9 -48 -2Z" fill="#81845a" stroke="#5a6040" stroke-width="2"/><rect x="114" y="167" width="35" height="22" rx="6" fill="#a4a374"/><path d="M122 139 q7 -13 16 2 M160 146 q11 19 2 55" fill="none" stroke="#665336" stroke-width="4"/><path d="M130 174 v7" stroke="#e0c590" stroke-width="3"/></g>') if o.get('back') else ''}
 <path d="M215 211 q3 10 19 16" stroke="#b79a77" stroke-width="11" fill="none" stroke-linecap="round"/>
 <ellipse data-slot="paws" cx="235" cy="228" rx="16" ry="7" fill="{fur}"/>
 <ellipse data-slot="paws" cx="219" cy="223" rx="12" ry="6" fill="{fur}"/>
 {('<path d="M221 222 l6 -2 M229 223 l3 -5" stroke="#f9e4d6" stroke-width="3"/>') if o.get('paws') else ''}
 {('<g><path d="M100 222 q0 -8 11 -8 h13 q7 2 8 10 l7 3 q5 7 -8 8 h-24 q-10 0 -7 -13Z" fill="#6c8ba4" stroke="#46647a" stroke-width="1.5"/><path d="M103 232 h31 M112 221 h10" stroke="#f6efd9" stroke-width="2.5" stroke-linecap="round"/></g>') if o.get('feet') else '<ellipse data-slot="feet" cx="117" cy="230" rx="22" ry="7" fill="url(#fur)"/>'}
 {('<path d="M181 199 q17 14 38 13 l1 10 q-24 1 -44 -13Z" fill="#bb7355"/><path d="M195 214 q-4 9 0 19 l13 -2 q-5 -10 1 -15Z" fill="#a45e48"/><path d="M195 226 l10 -2" stroke="#f0c69a" stroke-width="2"/>') if o.get('neck') else ''}
 {('<path d="M194 172 l17 2" stroke="#3e4549" stroke-width="2.5"/><rect x="212" y="169" width="21" height="15" rx="5" fill="#39434b"/><path d="M216 172 l9 1" stroke="#b6cfcb" stroke-width="2"/>') if o.get('eyes') else ''}
 {('<g transform="rotate(16 201 155)"><ellipse cx="201" cy="155" rx="26" ry="5.5" fill="#3b4247"/><path d="M184 154 l2 -28 q16 -6 32 0 l2 28Z" fill="#4a535a"/><path d="M186 145 h33" stroke="#bf8565" stroke-width="5"/></g>') if o.get('head')=='hat' else ''}
 {('<g transform="rotate(16 201 155)"><path d="M178 153 l-1 -23 13 10 11 -19 10 19 14 -10 -3 23Z" fill="#dab768" stroke="#ab8a43" stroke-width="1.5"/><path d="M180 153 h41" stroke="#be9b55" stroke-width="4"/></g>') if o.get('head')=='crown' else ''}
 </svg>'''
p=root/'tools/art-source.json';data=json.loads(p.read_text())
specs={'base':{},'hat':{'head':'hat'},'crown':{'head':'crown'},'glasses':{'eyes':True},'scarf':{'neck':True},'mittens':{'paws':True},'shoes':{'feet':True},'backpack':{'back':True}}
data['hero']={k:hero(v) for k,v in specs.items()};p.write_text(json.dumps(data,ensure_ascii=False))
