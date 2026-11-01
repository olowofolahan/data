import cv2, numpy as np, json, subprocess, sys
sys.path.insert(0,'/home/user/data/reel/tools')
from edl import *
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
TR=json.load(open('edit/tracks.json'))
STK=cv2.imread('edit/santa_sticker.png',cv2.IMREAD_UNCHANGED)  # BGRA
OUT=sys.argv[1] if len(sys.argv)>1 else 'edit/video_noaudio.mp4'
ONLY=(float(sys.argv[2]),float(sys.argv[3])) if len(sys.argv)>3 else None
LOG=[]
import os; NOMASK=os.environ.get('NOMASK')=='1'
def head(track,t):
    d=TR[track]['data']; ts=np.array([k[0] for k in d]); t=float(np.clip(t,ts[0],ts[-1]))
    i=int(np.searchsorted(ts,t)); i=min(max(i,1),len(d)-1); a,b=d[i-1],d[i]
    u=0 if b[0]==a[0] else (t-a[0])/(b[0]-a[0]); u=min(max(u,0),1)
    return [a[j]+(b[j]-a[j])*u for j in (1,2,3)]
# ---- grade LUTs
def make_lut(warm):
    x=np.arange(256)/255.0
    y=0.5+(x-0.5)*1.07; y=y*0.97+0.018
    k=0.80; y=np.where(y>k,k+(1-k)*np.tanh((y-k)/(1-k)),y)
    r=np.clip(y*(1+0.035*warm),0,1); g=np.clip(y*(1+0.008*warm),0,1); b=np.clip(y*(1-0.045*warm),0,1)
    return [(np.clip(c,0,1)*255).astype(np.uint8) for c in (b,g,r)]
LUTS={1:make_lut(1.0),0:make_lut(0.25)}
def grade(img,warm):
    l=LUTS[warm]; img=cv2.merge([cv2.LUT(img[...,i],l[i]) for i in range(3)])
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(np.float32); hsv[...,1]=np.clip(hsv[...,1]*1.08,0,255)
    return cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2BGR)
# ---- readers
class Reader:
    def __init__(s,src):
        s.cap=cv2.VideoCapture(f'raw/{src}.mp4'); s.t=-1; s.f=None; s.nt=None; s.nf=None
    def get(s,t):
        if s.f is None or t < s.t-0.02 or t > s.t+1.0:
            s.cap.set(cv2.CAP_PROP_POS_MSEC,max(0,t-0.2)*1000); s.f=None; s.nf=None
        while True:
            if s.nf is None:
                tt=s.cap.get(cv2.CAP_PROP_POS_MSEC)/1000; ok,f=s.cap.read()
                if not ok: return s.f
                s.nt,s.nf=tt,f
            if s.f is None or abs(s.nt-t) <= abs(s.t-t) or s.nt<=t:
                s.t,s.f=s.nt,s.nf; s.nf=None
                if s.t>=t: return s.f
            else: return s.f
readers={}
photos={}
def photo(k):
    if k not in photos: photos[k]=cv2.imread(PH[k])
    return photos[k]
def paste_sticker(frame,x,y,rc):
    k=rc/200.0; sz=max(8,int(600*k))
    st=cv2.resize(STK,(sz,sz),interpolation=cv2.INTER_AREA)
    x0=int(round(x-300*k)); y0=int(round(y-340*k))
    X0,Y0=max(0,x0),max(0,y0); X1,Y1=min(W,x0+sz),min(H,y0+sz)
    if X1<=X0 or Y1<=Y0: return
    s=st[Y0-y0:Y1-y0, X0-x0:X1-x0].astype(np.float32); a=s[...,3:4]/255.0
    roi=frame[Y0:Y1,X0:X1].astype(np.float32); frame[Y0:Y1,X0:X1]=(roi*(1-a)+s[...,:3]*a).astype(np.uint8)
def shot_frame(i,ot):
    st,src,tin,dur,trk,note,opt=TL[i]
    u=(ot-st)/dur; z0,z1=opt.get('zoom',(1.0,1.03)); z=z0+(z1-z0)*u
    if src.startswith('P'):
        img=photo(src); ih,iw=img.shape[:2]; base_w=ih*9/16; cx=opt.get('cx',iw/2); cy=ih/2
        w=base_w/z; h=ih/z; warm=1
    else:
        if src not in readers: readers[src]=Reader(src)
        t=tin+(ot-st); img=readers[src].get(t); ih,iw=img.shape[:2]; cx,cy=iw/2,ih/2; w=iw/z; h=ih/z
        warm=0 if (src=='v21' and tin>=60) else 1
    x0=cx-w/2; y0=cy-h/2; x0=min(max(0,x0),iw-w); y0=min(max(0,y0),ih-h)
    M=np.float32([[W/w,0,-x0*W/w],[0,H/h,-y0*H/h]])
    g=grade(img,warm)
    fr=cv2.warpAffine(g,M,(W,H),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REFLECT)
    bl=cv2.GaussianBlur(fr,(0,0),1.3); fr=cv2.addWeighted(fr,1.35,bl,-0.35,0)
    if trk and not NOMASK:
        tt=0 if src.startswith('P') else tin+(ot-st)
        hx,hy,hr=head(trk,tt); sx=W/w
        X=(hx-x0)*sx; Y=(hy-y0)*sx; rc=max(hr*1.5*sx, 46)
        paste_sticker(fr,X,Y,rc); LOG.append((round(ot,3),i,round(X),round(Y),round(rc)))
    return fr
TL,TOT=timeline()
TL=[(r[0],)+r[1:] for r in TL]
def text_layer(txt,kind):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    f=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',88 if kind=='open' else 92)
    lines=txt.split('\n'); y=1270 if kind=='open' else 1250
    em=None
    if kind=='open':
        ef=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',109)
        e=Image.new('RGBA',(140,140),(0,0,0,0)); ImageDraw.Draw(e).text((0,0),'\U0001F384',font=ef,embedded_color=True)
        e=e.crop(e.getbbox()).resize((104,112))
        em=e
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    for li,l in enumerate(lines):
        bb=d.textbbox((0,0),l,font=f); tw=bb[2]-bb[0]
        if li==0 and em is not None: lines_y=y
        x=(W-tw)//2; yy=y+li*112
        for dd in (sd,): dd.text((x+3,yy+4),l,font=f,fill=(0,0,0,200))
        d.text((x,yy),l,font=f,fill=(255,248,236,255))
    sh=sh.filter(ImageFilter.GaussianBlur(7))
    out=Image.alpha_composite(sh,im)
    if em is not None:
        out.alpha_composite(em,((W-em.width)//2, y+110))
    a=np.array(out).astype(np.float32); return a
TXT=[(text_layer(t,k),a,b) for t,a,b,k in TEXTS]
def boundary_d(t):
    for b,d in DISSOLVE.items():
        if abs(t-b)<1e-6: return d
    return 0
cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
     '-c:v','libx264','-preset','slow','-crf','16','-profile:v','high','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',OUT]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
NF=int(round(TOT*FPS))
fr_range=range(NF) if not ONLY else range(int(ONLY[0]*FPS),int(ONLY[1]*FPS))
for n in fr_range:
    ot=(n+0.5)/FPS
    idx=max(i for i,r in enumerate(TL) if r[0]<=ot)
    frame=None
    # dissolve with neighbour?
    st=TL[idx][0]; en=st+TL[idx][3]
    dprev=boundary_d(st); dnext=boundary_d(en)
    if dprev and ot<st+dprev/2 and idx>0:
        a=0.5+(ot-st)/dprev; A=shot_frame(idx-1,ot); B=shot_frame(idx,ot)
        frame=cv2.addWeighted(A,1-a,B,a,0)
    elif dnext and ot>en-dnext/2 and idx+1<len(TL):
        a=(ot-(en-dnext/2))/dnext; A=shot_frame(idx,ot); B=shot_frame(idx+1,ot)
        frame=cv2.addWeighted(A,1-a,B,a,0)
    else: frame=shot_frame(idx,ot)
    for lay,a0,a1 in TXT:
        if a0<=ot<=a1:
            al=min(1,(ot-a0)/0.6,(a1-ot)/0.6)
            al_=lay[...,3:4]/255.0*al; frame=(frame*(1-al_)+lay[...,[2,1,0]]*al_).astype(np.uint8)
    # fade from/to black
    fade=min(1,ot/0.35,(TOT-ot)/1.3)
    if fade<1: frame=(frame*max(0,fade)).astype(np.uint8)
    p.stdin.write(frame.tobytes())
    if n%300==0: print(n,flush=True)
p.stdin.close(); p.wait()
json.dump(LOG,open(OUT+'.masklog.json','w'))
print('done')
