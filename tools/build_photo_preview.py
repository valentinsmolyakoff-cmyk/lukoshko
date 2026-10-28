"""Build an isolated, self-contained photo redesign prototype. Production is not modified."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
import base64,json,re
root=Path(__file__).resolve().parents[1];assets=root/'assets/photo'
def uri(p):
 return 'data:image/'+('jpeg' if p.suffix=='.jpg' else 'png')+';base64,'+base64.b64encode(p.read_bytes()).decode()
def keep_largest(alpha,min_share):
 from collections import deque
 a=np.array(alpha)>128;h,w=a.shape;seen=np.zeros_like(a);parts=[]
 for y in range(h):
  for x in range(w):
   if a[y,x] and not seen[y,x]:
    q=deque([(y,x)]);seen[y,x]=1;px=[]
    while q:
     cy,cx=q.popleft();px.append((cy,cx))
     for ny,nx in ((cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)):
      if 0<=ny<h and 0<=nx<w and a[ny,nx] and not seen[ny,nx]:seen[ny,nx]=1;q.append((ny,nx))
    parts.append(px)
 if not parts:return alpha
 biggest=max(len(part) for part in parts);keep=np.zeros_like(a)
 for part in parts:
  if len(part)>=biggest*min_share:
   ys,xs=zip(*part);keep[np.array(ys),np.array(xs)]=True
 return Image.fromarray((keep*255).astype('uint8'))

CACHE_DIR=Path('/tmp/lukoshko-photo-cache');CACHE_DIR.mkdir(exist_ok=True)
def cut_cached(name):
 src=assets/(name+'-source.png');key=CACHE_DIR/(name+'-'+str(int(src.stat().st_mtime))+'-'+str(src.stat().st_size)+'.png')
 return key
photos={}
manifest=json.loads((assets/'manifest.json').read_text())
for glyph,name in manifest.items():
 if name=='apple-green' or (name.startswith('token-') and name!='token-red'):continue
 # Sources come from different studios: some backdrops are pure white, others a grey
 # card or an unevenly lit sweep. Compare each pixel with the backdrop colour sampled
 # from the border, then flood the outer region instead of assuming pure white.
 cached=cut_cached(name)
 if cached.exists():
  photos[glyph]=uri(cached);continue
 im=Image.open(assets/(name+'-source.png')).convert('RGB');a=np.array(im).astype(np.int16)
 border=np.concatenate([a[0:3].reshape(-1,3),a[-3:].reshape(-1,3),a[:,0:3].reshape(-1,3),a[:,-3:].reshape(-1,3)])
 bg=np.median(border,axis=0)
 near=((np.abs(a-bg).max(axis=2))<=34).astype('uint8')*255
 mask=Image.fromarray(np.pad(near,1,constant_values=255)).copy()
 ImageDraw.floodfill(mask,(0,0),128,thresh=0)
 alpha=Image.fromarray(np.where(np.array(mask)[1:-1,1:-1]==128,0,255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.6))
 alpha=keep_largest(alpha,0.04)
 bbox=alpha.getbbox();assert bbox,(name,'empty cut-out')
 im=im.convert('RGBA');im.putalpha(alpha);im=im.crop(bbox);im.thumbnail((220,220),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',(256,256));out.alpha_composite(im,((256-im.width)//2,(256-im.height)//2));out.save(assets/(name+'.png'));photos[glyph]=uri(assets/(name+'.png'));cached.write_bytes((assets/(name+'.png')).read_bytes())
# Colour variants of real objects: repaint hue/saturation of the photographed token
# instead of generating near-identical photos.
def variant(src_name,dst_name,hue,sat=1.0,val=1.0):
 im=Image.open(assets/(src_name+'.png')).convert('RGBA');arr=np.array(im)
 hsv=np.array(Image.fromarray(arr[:,:,:3]).convert('HSV')).astype(np.float32)
 if hue is not None:hsv[:,:,0]=hue
 hsv[:,:,1]=np.clip(hsv[:,:,1]*sat,0,255);hsv[:,:,2]=np.clip(hsv[:,:,2]*val,0,255)
 rgb=Image.fromarray(hsv.astype('uint8'),'HSV').convert('RGB').convert('RGBA');rgb.putalpha(im.getchannel('A'))
 rgb.save(assets/(dst_name+'.png'));photos[{'token-yellow':'🟡','token-green':'🟢','token-blue':'🔵','token-orange':'🟠','token-purple':'🟣','token-black':'⬛'}[dst_name]]=uri(assets/(dst_name+'.png'))
variant('token-red','token-yellow',30,1.05,1.12)
variant('token-red','token-green',60,0.9,0.92)
variant('token-red','token-blue',150,0.95,1.0)
variant('token-red','token-orange',15,1.1,1.05)
variant('token-red','token-purple',200,0.95,0.95)
variant('token-red','token-black',0,0.25,0.3)

# A separately labelled colour variant for the existing green-apple target.
im=Image.open(assets/'apple-red.png');rgba=np.array(im);rgb=Image.fromarray(rgba[:,:,:3]).convert('HSV');hsv=np.array(rgb);hsv[:,:,0]=np.where((hsv[:,:,0]<30)|(hsv[:,:,0]>225),60,hsv[:,:,0]);hsv[:,:,1]=(hsv[:,:,1].astype(float)*.78).astype('uint8');rgb=Image.fromarray(hsv,'HSV').convert('RGB').convert('RGBA');rgb.putalpha(im.getchannel('A'));rgb.save(assets/'apple-green.png');photos['🍏']=uri(assets/'apple-green.png')
scenes={}
for n in ['forest','house','table']:
 im=Image.open(assets/(n+'.jpg')).convert('RGB');im.thumbnail((1000,1300),Image.Resampling.LANCZOS);p=assets/(n+'-web.jpg');im.save(p,quality=84,optimize=True);scenes[n]=uri(p)
s=(root/'index.html').read_text()
_old,_new=(Path(__file__).with_name('basket_patch.txt')).read_text().split('===OLD===',1)[1].split('===NEW===',1)
assert _old in s
s=s.replace(_old,_new)
s=s.replace('drawHero(outfit(),-70,-108,140,122);','drawHero(outfit(),-96,-148,192,168);')
a=s.index('const GAME_PICTURES=')+len('const GAME_PICTURES=');b=s.index(';\nconst TISHKA_LAYERS',a);pict=json.loads(s[a:b]);pict.update(photos);s=s[:a]+json.dumps(pict,ensure_ascii=False,separators=(',',':'))+s[b:]
s=s.replace('const GAME_PICTURES=', 'const PHOTO_SCENES='+json.dumps(scenes,separators=(',',':'))+';\nconst GAME_PICTURES=',1)
s=s.replace('const pictureImages=new Map(),heroLayers=new Map();','const photoBackgroundImages=new Map();\nconst pictureImages=new Map(),heroLayers=new Map();')
s=s.replace('const picturesReady=Promise.all([','const picturesReady=Promise.all([\n ...Object.entries(PHOTO_SCENES).map(([k,src])=>loadArt(photoBackgroundImages,k,src)),')
a=s.index('function drawBackground(){');b=s.index('\nfunction drawItem(',a)
s=s[:a]+'''function drawBackground(){
 const kind=R?.spec?.k||'catch', table=['mem','odd','choice','seq','diff','dots','maze'].includes(kind);
 const img=photoBackgroundImages.get(table?'table':'forest');
 ctx.fillStyle='#eee5d0';ctx.fillRect(0,0,Wd,Hd);
 if(img?.complete&&img.naturalWidth){const scale=Math.max(Wd/img.naturalWidth,Hd/img.naturalHeight),w=img.naturalWidth*scale,h=img.naturalHeight*scale;ctx.drawImage(img,(Wd-w)/2,(Hd-h)/2,w,h);}
 ctx.fillStyle=table?'rgba(255,250,236,.50)':'rgba(248,245,227,.20)';ctx.fillRect(0,0,Wd,Hd);
}
''' +s[b:]
s=s.replace('<div class="mascot" id="menuMascot" style="width:150px;height:126px;margin:0 auto"></div>','<div class="menuLandscape"><span class="landscapeLabel">МАЛЕНЬКИЕ ОТКРЫТИЯ В БОЛЬШОМ ЛЕСУ</span><div class="mascot" id="menuMascot"></div></div>')
css='''
/* Photographic prototype: opaque text surfaces, natural tactile materials. */
:root{--ink:#303c2c;--muted:#5c604d;--paper:#fcf8ed;--forest:#3c5534;--edge:#d4c6aa;__SCENES__}
html,body{font-family:"Segoe UI",system-ui,sans-serif;background:#30432d;color:var(--ink)}
.screen{background:linear-gradient(#172a1930,#172a1960),var(--photo-forest) center/cover fixed;padding:24px 18px}
.card{background:var(--paper);border:1px solid #e2d5bb;border-radius:24px;box-shadow:0 22px 70px #14220e80;padding:22px 24px;color:var(--ink)}
h1,h2,.bigscore{color:var(--ink)}h1{letter-spacing:.12em;font-size:clamp(32px,6vw,46px);font-weight:850}
p.sub,.tiny,.skNote,.dayHead,.parentLink{color:var(--muted)}
.btn{background:linear-gradient(#4f6b42,#354c2e);color:#fffced;box-shadow:0 4px 0 #23371e,0 6px 12px #25331d22;border:1px solid #57724b;border-radius:15px;font-weight:750;padding:13px 27px;letter-spacing:.01em}
.btn.blue,.btn.pink{background:linear-gradient(#fff9eceb,#f3e9d3ed),var(--photo-table) center/cover;color:#35432e;border-color:#cebd9b;box-shadow:0 4px 0 #baa785,0 6px 12px #25331d18}
.btn:active,.btn.blue:active,.btn.pink:active{box-shadow:0 1px 0 #95876b;transform:translateY(3px)}
.btn:disabled{opacity:1;background:#e2ded1;color:#555749;border-color:#c5bda9;box-shadow:0 4px 0 #b7ad98}
.btn.small{border-radius:12px}
#scrMenu .card{max-width:670px;padding:0 26px 22px;overflow:hidden}
.menuLandscape{position:relative;height:235px;margin:0 -26px 18px;background:var(--photo-forest) center 62%/cover;isolation:isolate}
.menuLandscape:after{content:'';position:absolute;bottom:0;inset-inline:0;height:75px;background:linear-gradient(transparent,#14230a30);z-index:-1}
.landscapeLabel{position:absolute;top:18px;left:50%;transform:translateX(-50%);white-space:nowrap;font-size:10px;font-weight:750;letter-spacing:.13em;padding:8px 11px;border:1px solid #e8dec4;background:#fcf8ed;color:#465238;border-radius:7px}
#menuMascot{position:absolute;bottom:-20px;left:50%;transform:translateX(-50%);width:330px;height:288px;margin:0;filter:drop-shadow(0 10px 6px #18200c44)}
#scrMenu p.sub{font-size:14px;margin-bottom:18px}
#scrMenu .rankBox{display:grid;grid-template-columns:1fr;gap:1px;text-align:left;margin:0 0 20px;padding:14px 16px;border:1px solid var(--edge);border-radius:15px;background:#f0ead9;color:#57502e}
.rankBar{height:9px;background:#fffdf5;margin-top:7px}.rankBar div{background:linear-gradient(90deg,#a98b41,#6e793e)}
#rankName{font-size:16px;color:#3f4a2d}#rankInfo{color:#605330}
.dayHead{text-align:left;font-size:11px;letter-spacing:.13em}.dayBox{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:18px}.dayChip{width:100%;max-width:none;min-height:65px;padding:10px;border:1px solid #d8ccb4;border-radius:12px;background:#fffcf4;color:#4a513c;font-size:12px;box-shadow:0 3px 8px #433b2010}
.dayChip.done{background:#e9efdf;border-color:#98a77c;color:#355128}
#scrMenu .row:first-of-type{display:flex}#btnPlay{min-width:165px}#btnMap{font-size:17px}#btnHouse{font-size:15px}#scrMenu .tiny{font-size:11px;margin-top:16px;line-height:1.5}
.mapHead{background:var(--paper);border-color:#dfd3bb}.world{background:#f3eddf;border:1px solid #e1d5be;border-radius:17px;box-shadow:0 3px 10px #3d331413}.world h3{color:#3e4b33}.tile{background:#fffcf4;border:1px solid #dfd2b6;box-shadow:0 3px 0 #cbbd9d;color:#3d4930;border-radius:12px}.tile.boss{background:#f3e4b9}.tile.locked{background:#e9e6dd;color:#5e5e51;box-shadow:0 3px 0 #cbc6b8}.tile.locked .st{color:#68614d}.tile .st{color:#78561e}
#scrHouse{background:linear-gradient(#2f261b40,#251d1560),var(--photo-house) center/cover fixed}
#tishkaScene{width:min(600px,100%);aspect-ratio:6/4;background:var(--photo-house) center 72%/cover;box-shadow:inset 0 0 0 1px #79644250;border-radius:18px;overflow:hidden;margin:12px auto}
#tishkaScene .ground{display:none}#tishkaBody{inset:auto 8% -7%;height:auto;aspect-ratio:300/262;filter:drop-shadow(0 7px 4px #32261655)}
#tishkaName{color:#5d4b30}.hItem{background:#fffcf4;border:1px solid #dfd2b6;border-radius:13px;box-shadow:0 3px 0 #cbbd9d}.hItem .n,.hItem .need,.hItem .slot{color:#5b5846}.hItem.locked{background:#eae7de}.hItem.locked .n,.hItem.locked .need{color:#615e51}.hItem.on{outline:3px solid #81965b;background:#f4f4df}
.aiCard{background:#f2eddd;border:1px solid #c9bd9e;border-radius:16px;padding:19px}.aiTitle{color:#3d5133}.aiText{color:#35412f}.aiNote{color:#605a46}.sbar{background:#e4dfd1}.sbar div{background:linear-gradient(90deg,#9aae74,#5e7d47)}.skillRow .t{color:#3e4835}.stat{background:#f1ebdd;border:1px solid #e0d2b8}.stat .num{color:#425532}.stat .lbl{color:#5c604c}
#scrResult .card{max-width:640px}.rankLine{color:#69532e}#resAi{background:#f1eddf;border:1px solid #d1c3a5;color:#3b4831}
#hud .pill,#promptBox{background:#fffcf4;color:#35432d;border:1px solid #d8c8a5;box-shadow:0 3px 9px #27331922}#bar{background:#f5eddd}#barFill{background:linear-gradient(90deg,#9aae74,#5e7d47)}
#btnSay,.fab{background:linear-gradient(#f9f0d9,#e2d0a6);border:1px solid #bcaa82;box-shadow:0 3px 0 #a18f68}
#lvlIntro .box{background:#fffcf4;border:1px solid #d8c8a5;border-radius:18px;box-shadow:0 15px 50px #172a1980}#lvlIntro .num,#lvlIntro .ttl,#lvlIntro .wrld{color:#3d5032}
#toast{color:#35432d;background:#fffaf0;border:1px solid #d3c39f}
@media(max-width:480px){.screen{padding:12px}.card{padding:18px}.menuLandscape{height:205px}#scrMenu .card{padding:0 20px 18px}.menuLandscape{margin-inline:-20px}#menuMascot{width:300px;height:262px}.landscapeLabel{font-size:8px;top:14px}.dayBox{gap:6px}.dayChip{padding:8px 6px;font-size:11px;min-height:68px}#btnPlay{min-width:142px}#btnMap{font-size:15px;padding-inline:15px}#scrMenu .rankBox{margin-bottom:15px}#scrMenu p.sub{font-size:12px}#scrMenu .row{gap:3px}#tishkaScene{aspect-ratio:1.2}#tishkaBody{inset-inline:0;bottom:-3%}.mapHead{top:-18px}}
@media(min-width:800px){.menuLandscape{height:285px}#menuMascot{width:400px;height:349px}.dayChip{font-size:13px}#scrMenu .card{padding-inline:38px}.menuLandscape{margin-inline:-38px}}
'''
css=css.replace('__SCENES__',';'.join('--photo-'+k+':url("'+v+'")' for k,v in scenes.items())+';')
css+=(Path(__file__).with_name('day_chip.css')).read_text()
s=s.replace('</style>',css+'\n</style>',1)
# This prototype must not register itself in the production service-worker cache.
s=re.sub(r"if\('serviceWorker' in navigator\).*?(?=\n[^ ])",lambda m:m.group(0),s) if False else s
s=s.replace("navigator.serviceWorker.register('./sw.js')", "Promise.resolve({addEventListener(){},installing:null})")
s=s.replace("navigator.serviceWorker.register('sw.js')", "Promise.resolve({addEventListener(){},installing:null})")
s=s.replace('</body>','<script>'+Path(__file__).with_name('day_chip_fix.js').read_text()+'</script>\n</body>',1)
s=s.replace('</body>','<script>'+Path(__file__).with_name('photo_ui_fix.js').read_text()+'</script>\n</body>',1)
s=s.replace('</body>','<script>'+Path(__file__).with_name('photo_materials.js').read_text()+'</script>\n</body>',1)
s=s.replace('<title>Лукошко — развивающая игра для детей 5+</title>','<title>Лукошко — фотореалистичный макет</title>')
(root/'photo-preview.html').write_text(s)
print('Prototype ready:',root/'photo-preview.html', 'bytes',len(s.encode()),'photographic game assets',len(photos))
