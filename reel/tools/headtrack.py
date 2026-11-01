# Toddler head tracker: red pajama blob -> dark (hair/skin) region just above it.
import cv2, numpy as np, sys, json
src, t0, t1, outp = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
cap = cv2.VideoCapture(src); cap.set(cv2.CAP_PROP_POS_MSEC, t0*1000)
kf=[]; prev=None
while True:
    t = cap.get(cv2.CAP_PROP_POS_MSEC)/1000
    ok, f = cap.read()
    if not ok or t > t1: break
    H,W=f.shape[:2]
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    red = (((hsv[...,0]<8)|(hsv[...,0]>168)) & (hsv[...,1]>110) & (hsv[...,2]>45)).astype(np.uint8)
    red = cv2.morphologyEx(red, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(red)
    if n<2 or st[1:,4].max()<150: kf.append([round(t,3),None,None,None]); continue
    i=1+np.argmax(st[1:,4]); ys,xs=np.where(lab==i); top=ys.min()
    w=st[i,2]; s=max(25, min(w, float(sys.argv[5]) if len(sys.argv)>5 else 90))
    cx=xs[ys<top+max(6,s*0.3)].mean()
    x0=int(max(0,cx-s*0.9)); x1=int(min(W,cx+s*0.9)); y0=int(max(0,top-s*1.3)); y1=int(min(H,top+s*0.25))
    win=hsv[y0:y1,x0:x1,2]
    dark=(win<85).astype(np.uint8)
    dark=cv2.morphologyEx(dark,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m,l2,s2,c2=cv2.connectedComponentsWithStats(dark)
    if m<2: kf.append([round(t,3),None,None,None]); continue
    # choose component closest to (cx, top - s*0.4) weighted by area
    best=None;bs=-1
    for j in range(1,m):
        a=s2[j,4]
        if a<20: continue
        dx=c2[j,0]+x0-cx; dy=c2[j,1]+y0-(top-s*0.4)
        sc=a/(1+(dx*dx+dy*dy)/(s*s))
        if sc>bs: bs=sc;best=j
    if best is None: kf.append([round(t,3),None,None,None]); continue
    bx,by,bw,bh,_=s2[best]
    hx=x0+bx+bw/2; hy=y0+by+bh/2; r=max(bw,bh)/2
    kf.append([round(t,3),round(float(hx),1),round(float(hy),1),round(float(r),1)])
json.dump({'type':'kf','data':kf},open(outp,"w"))
print(len(kf), sum(k[1] is None for k in kf),"missing")
