# Draws an opaque Santa-face sticker. Core disc (radius 200 around (300,340)) is fully opaque.
from PIL import Image, ImageDraw, ImageFilter
S=600; C=(300,340); R=200
img=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(img)
def ell(c,r,fill): d.ellipse([c[0]-r[0],c[1]-r[1],c[0]+r[0],c[1]+r[1]],fill=fill)
# white sticker border (disc + hat silhouette), drawn first
ell(C,(R+16,R+16),(255,255,255,255))
d.polygon([(95,250),(505,250),(470,40),(330,10),(250,80)],fill=(255,255,255,255))
ell((485,70),(52,52),(255,255,255,255))
# beard (white) fills lower disc
ell(C,(R,R),(246,244,240,255))
# face (skin)
ell((300,300),(130,115),(241,194,160,255))
# cheeks
ell((218,342),(26,18),(236,140,130,255)); ell((382,342),(26,18),(236,140,130,255))
# eyes (closed happy arcs)
d.arc([228,282,272,318],200,340,fill=(60,40,35,255),width=9)
d.arc([328,282,372,318],200,340,fill=(60,40,35,255),width=9)
# nose
ell((300,338),(22,18),(225,120,110,255))
# moustache
ell((258,370),(52,24),(255,255,255,255)); ell((342,370),(52,24),(255,255,255,255))
# beard curls texture
for x,y in [(190,420),(250,450),(310,460),(370,445),(420,410),(160,370),(440,360)]:
    d.arc([x-30,y-22,x+30,y+22],20,160,fill=(222,220,215,255),width=6)
# hat
d.polygon([(110,245),(490,245),(455,60),(330,25),(240,95)],fill=(200,30,40,255))
d.polygon([(330,25),(455,60),(475,110),(420,80)],fill=(170,20,30,255))
d.rounded_rectangle([90,205,510,275],radius=34,fill=(255,255,255,255))
ell((485,70),(42,42),(255,255,255,255))
# soft shadow
sh=Image.new('RGBA',(S,S),(0,0,0,0)); sd=ImageDraw.Draw(sh)
sd.ellipse([C[0]-R-16,C[1]-R-10,C[0]+R+16,C[1]+R+22],fill=(0,0,0,110))
sh=sh.filter(ImageFilter.GaussianBlur(14))
out=Image.alpha_composite(sh,img)
out.save('edit/santa_sticker.png'); print('ok')
