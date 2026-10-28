"""Original side-on Tishka artwork. Rebuild source and then run build_art_bundle.py."""
from pathlib import Path
import json,math
root=Path(__file__).resolve().parents[1]
def hero(o={}):
 pts=[]
 for i in range(33):
  a=math.pi-i*math.pi/32;r=1 if i%2==0 else .94
  pts.append(f'{139+101*math.cos(a)*r:.1f},{199-104*math.sin(a)*r:.1f}')
 sp='M'+' L'.join(pts)+' L225 221 L57 224 Z'
 hat=o.get('head')=='hat';crown=o.get('head')=='crown'
 paws='#ec97a8' if o.get('paws') else 'url(#fur)'
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="262" viewBox="0 0 300 262">
 <defs><linearGradient id="spine" x2=".2" y2="1"><stop stop-color="#ae7b54"/><stop offset="1" stop-color="#77503d"/></linearGradient><linearGradient id="fur" x2=".4" y2="1"><stop stop-color="#fff1d3"/><stop offset="1" stop-color="#e6ba85"/></linearGradient></defs>
 <ellipse cx="154" cy="241" rx="111" ry="9" fill="#80522c" opacity=".13"/>
 <path d="M57 211 q-20 5 -19 13 q8 4 26 -6" fill="#c39768"/>
 <ellipse cx="91" cy="224" rx="20" ry="10" fill="#b88455"/>
 <ellipse cx="191" cy="224" rx="17" ry="10" fill="#b88455"/>
 <path d="{sp}" fill="url(#spine)" stroke="#90633f" stroke-width="1.2" stroke-linejoin="round"/>
 <path d="M65 184 l-4 -13 m17 -31 4 -10 m23 -14 7 -7 m25 13 10 -7 m-37 52 6 -11 m51 7 9 -7 m-24 39 9 -7" stroke="#e6bd89" stroke-width="3.5" opacity=".55" stroke-linecap="round"/>
 <path d="M114 180 Q146 153 181 172 Q208 183 226 206 Q220 230 184 231 L109 230 Q87 215 114 180Z" fill="url(#fur)"/>
 <path d="M187 135 Q219 126 236 151 Q247 167 271 173 Q281 179 271 187 Q248 205 220 204 Q199 204 183 187 Q163 161 187 135Z" fill="url(#fur)"/>
 <ellipse cx="183" cy="147" rx="18" ry="20" fill="#d9a16d"/><ellipse cx="185" cy="148" rx="11" ry="12" fill="#e8afa0"/>
 <ellipse cx="220" cy="160" rx="9.5" ry="12" fill="#3c302b"/><circle cx="217" cy="156" r="3.5" fill="white"/><circle cx="223" cy="164" r="1.6" fill="#fff8e8"/>
 <ellipse cx="213" cy="181" rx="12" ry="7" fill="#f2b1a0"/>
 <ellipse cx="271" cy="176" rx="10" ry="7" fill="#42362e"/><ellipse cx="269" cy="173.5" rx="3" ry="1.5" fill="#fff0da"/>
 <path d="M251 190 q-8 7 -14 3" stroke="#946045" stroke-width="2.6" fill="none" stroke-linecap="round"/>
 {('<g><rect x="98" y="129" width="67" height="70" rx="22" fill="#cb8251" stroke="#a3623c" stroke-width="2"/><rect x="106" y="163" width="49" height="28" rx="10" fill="#efa665"/><path d="M113 129 q8 -15 21 0" stroke="#9e5a36" stroke-width="5" fill="none"/><circle cx="130" cy="177" r="4" fill="#fff0b1"/><path d="M166 144 q18 12 8 50" stroke="#ad663c" stroke-width="7" fill="none" stroke-linecap="round"/></g>') if o.get('back') else ''}
 <ellipse data-slot="paws" cx="213" cy="228" rx="19" ry="10" fill="{paws}"/>
 <path d="M209 198 q7 13 20 14" fill="none" stroke="#dfae79" stroke-width="13" stroke-linecap="round"/>
 <ellipse data-slot="paws" cx="233" cy="211" rx="13" ry="11" transform="rotate(-15 233 211)" fill="{paws}"/>
 {('<path d="M205 223 l17 1 m4 -17 13 -4" stroke="#ffe9db" stroke-width="4" stroke-linecap="round"/>') if o.get('paws') else ''}
 {('<g><path d="M105 219 q-5 -10 9 -11 h17 q8 1 8 13 l9 4 q6 10 -8 11 h-29 q-13 -1 -6 -17Z" fill="#719bd0" stroke="#4b7aaa" stroke-width="2"/><path d="M106 232 h36 M119 218 h12" stroke="#fff4dc" stroke-width="4" stroke-linecap="round"/></g>') if o.get('feet') else '<ellipse data-slot="feet" cx="126" cy="228" rx="25" ry="11" fill="url(#fur)"/>'}
 {('<path d="M182 186 q18 18 37 12 l-1 14 q-24 4 -43 -16Z" fill="#e77f6b"/><path d="M185 201 q-10 9 -7 27 l17 1 q-3 -13 5 -22Z" fill="#cd6255"/><path d="M180 218 h13 m-14 6 h14" stroke="#ffe2b2" stroke-width="3"/>') if o.get('neck') else ''}
 {('<path d="M184 150 l22 5" stroke="#394758" stroke-width="4"/><rect x="207" y="149" width="27" height="22" rx="8" fill="#394758"/><path d="M213 154 l9 1" stroke="#b0e1e6" stroke-width="3" stroke-linecap="round"/>') if o.get('eyes') else ''}
 {('<g transform="rotate(11 211 135)"><ellipse cx="211" cy="135" rx="33" ry="7" fill="#3d495b"/><path d="M189 133 l2 -33 q20 -8 40 0 l2 33Z" fill="#485971"/><path d="M191 123 h41" stroke="#ef9d81" stroke-width="7"/></g>') if hat else ''}
 {('<g transform="rotate(11 211 135)"><path d="M183 132 l-2 -27 17 12 12 -24 13 24 17 -12 -3 27Z" fill="#ffd66d" stroke="#d7a245" stroke-width="2"/><path d="M184 133 h53" stroke="#e7b047" stroke-width="6" stroke-linecap="round"/><circle cx="211" cy="121" r="4" fill="#e8879d"/></g>') if crown else ''}
 </svg>'''
p=root/'tools/art-source.json';data=json.loads(p.read_text())
specs={'base':{},'hat':{'head':'hat'},'crown':{'head':'crown'},'glasses':{'eyes':True},'scarf':{'neck':True},'mittens':{'paws':True},'shoes':{'feet':True},'backpack':{'back':True}}
data['hero']={k:hero(v) for k,v in specs.items()};p.write_text(json.dumps(data,ensure_ascii=False))
