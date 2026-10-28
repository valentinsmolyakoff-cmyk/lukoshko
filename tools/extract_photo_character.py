from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import numpy as np
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else '/home/user/tishka-photo-source.png');im=Image.open(p).convert('RGB');a=np.array(im)
lo=a.min(2);hi=a.max(2);candidate=(lo>229)|((hi-lo<22)&(lo>180))
m=Image.fromarray(np.pad(candidate.astype('uint8')*255,1,constant_values=255)).copy();ImageDraw.floodfill(m,(0,0),128,thresh=0)
assert m.getpixel((571,621))==255
ImageDraw.floodfill(m,(571,621),128,thresh=0) # enclosed white background between the hind legs
alpha=np.where(np.array(m)[1:-1,1:-1]==128,0,255).astype('uint8');mask=Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(.25));im=im.convert('RGBA');im.putalpha(mask)
bbox=im.getchannel('A').getbbox();im=im.crop(bbox);w=490;h=round(im.height*w/im.width);im=im.resize((w,h),Image.Resampling.LANCZOS)
out=Image.new('RGBA',(600,524));out.alpha_composite(im,(66,468-h))
out.save(Path(__file__).with_name('tishka-photo.png'));print('Photo extracted',bbox,'normalized size',w,h)
