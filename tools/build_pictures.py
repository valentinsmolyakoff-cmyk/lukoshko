from pathlib import Path
import regex,json,urllib.request,concurrent.futures,time
root=Path(__file__).resolve().parents[1];s=(root/'index.html').read_text()
pat=regex.compile(r'\p{Regional_Indicator}{2}|[\p{Extended_Pictographic}\U0001F170-\U0001F1FF](?:\uFE0F|\p{Emoji_Modifier})?(?:\u200D[\p{Extended_Pictographic}](?:\uFE0F|\p{Emoji_Modifier})?)*')
glyphs=sorted(set(pat.findall(s)))
cache=root/'tools'/'picture-source';cache.mkdir(exist_ok=True)
def get(g):
 code='-'.join(format(ord(c),'x') for c in g if ord(c)!=0xfe0f)
 path=cache/(code+'.svg')
 if not path.exists():
  variants=[code]
  if '\u200d' in g:variants.append('-'.join(format(ord(c),'x') for c in g))
  for fullcode in variants:
   for host in ['https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/svg/','https://raw.githubusercontent.com/jdecked/twemoji/main/assets/svg/']:
    try:
     data=urllib.request.urlopen(host+fullcode+'.svg',timeout=20).read().decode();assert '<svg' in data;path.write_text(data);break
    except Exception:pass
   if path.exists():break
 if path.exists():return (g,path.read_text())
 return (g,None)
with concurrent.futures.ThreadPoolExecutor(max_workers=14) as pool:results=list(pool.map(get,glyphs))
missing=[g for g,d in results if not d]; print('glyphs',len(glyphs),'loaded',len(results)-len(missing),'missing',missing)
(root/'pictures.js').write_text('/* Twemoji graphics: Twitter, Inc and contributors, CC-BY 4.0. See PICTURES-LICENSE.md. */\nconst GAME_PICTURES = '+json.dumps({g:d for g,d in results if d},ensure_ascii=False,separators=(',',':'))+';\n')
(root/'PICTURES-LICENSE.md').write_text('# Иллюстрации игровых предметов\n\nTwemoji graphics © Twitter, Inc and contributors, лицензия CC-BY 4.0.\nИсточник: https://github.com/jdecked/twemoji/tree/main/assets/svg\nЛицензия: https://creativecommons.org/licenses/by/4.0/\nИзображения включены в pictures.js, работают без сети и без системного шрифта эмодзи.\n')
(root/'tools'/'picture-coverage.json').write_text(json.dumps({'count':len(glyphs),'missing':missing},ensure_ascii=False))
