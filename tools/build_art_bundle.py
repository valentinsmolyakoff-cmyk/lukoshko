"""Rebuild embedded PNG artwork: pip install cairosvg; python3 tools/build_art_bundle.py."""
from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as ET
import json,base64,cairosvg
root=Path(__file__).resolve().parents[1]
src=json.loads((root/'tools/art-source.json').read_text())
def png(svg,w=96,h=96):
 return 'data:image/png;base64,'+base64.b64encode(cairosvg.svg2png(bytestring=svg.encode(),output_width=w,output_height=h)).decode()
def serialize(e):return ET.tostring(e,encoding='unicode')
base=ET.fromstring(src['hero']['base']);nodes=list(base);defs=nodes[0]
neutral_paws=[n for n in nodes if n.tag.endswith('ellipse') and n.get('cx') in ['199','116'] and n.get('cy') in ['201','211']]
neutral_feet=[n for n in nodes if n.tag.endswith('ellipse') and n.get('cy')=='227']
def layer(children):
 e=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','width':'300','height':'262','viewBox':'0 0 300 262'})
 e.append(defs)
 for n in children:
  if n is not defs:e.append(n)
 return png(serialize(e),300,262)
original=Counter(serialize(n) for n in nodes)
layers={'base':layer([n for n in nodes if n not in neutral_paws+neutral_feet]),'paws':layer(neutral_paws),'feet':layer(neutral_feet)}
for name,svg in src['hero'].items():
 if name=='base':continue
 full=ET.fromstring(svg);seen=original.copy();delta=[]
 for n in list(full):
  t=serialize(n)
  if seen[t]:seen[t]-=1
  else:delta.append(n)
 layers[name]=layer(delta)
for g in ['🔦','🥕','🍯','🎨','🥁','🎸','🔭','🧭','🗺️','🏆','💎','🎈','🪁','🌟']:
 art=src['pictures'][g];inner=art[art.index('>')+1:art.rindex('</svg>')]
 # Full-size transparent layers keep hands aligned regardless of CSS aspect ratio.
 item='<svg xmlns="http://www.w3.org/2000/svg" width="300" height="262" viewBox="0 0 300 262"><svg x="207" y="177" width="42" height="42" viewBox="0 0 36 36">'+inner+'</svg></svg>'
 layers['hand:'+g]=png(item,300,262)
pictures={g:png(svg) for g,svg in src['pictures'].items()}
js='/* Embedded PNG art. Twemoji graphics © Twitter, Inc and contributors, CC-BY 4.0; PICTURES-LICENSE.md. */\nconst GAME_PICTURES='+json.dumps(pictures,ensure_ascii=False,separators=(',',':'))+';\nconst TISHKA_LAYERS='+json.dumps(layers,separators=(',',':'))+';\n'
(root/'tools/art-bundle.js').write_text(js)
p=root/'index.html';s=p.read_text()
if '<script id="artBundle">' in s:
 a=s.index('<script id="artBundle">');b=s.index('</script>',a)+9;s=s[:a]+'<script id="artBundle">\n'+js+'</script>'+s[b:]
else:s=s.replace('<script src="pictures.js"></script>','<script id="artBundle">\n'+js+'</script>')
p.write_text(s)
print('PNG assets:',len(pictures),'hero layers:',len(layers),'bundle bytes:',len(js))
