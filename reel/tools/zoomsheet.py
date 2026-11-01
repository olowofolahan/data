# crops source region, scales 2x, draws labelled grid in SOURCE px. args: src t0 t1 step x0 y0 w h out
import cv2,sys,numpy as np,json
src,t0,t1,step,x0,y0,w,h,outp=sys.argv[1],*map(float,sys.argv[2:9]),sys.argv[9]
x0,y0,w,h=int(x0),int(y0),int(w),int(h)
trk=json.load(open('edit/tracks.json')).get(sys.argv[10]) if len(sys.argv)>10 else None
sys.path.insert(0,'tools')
cap=cv2.VideoCapture(src); tiles=[]; t=t0
while t<=t1+1e-6:
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000); ok,f=cap.read()
    c=f[y0:y0+h,x0:x0+w].copy(); c=cv2.resize(c,(w*2,h*2))
    for gx in range(0,w,25): cv2.line(c,(gx*2,0),(gx*2,h*2),(0,255,255) if (x0+gx)%100==0 else (90,90,90),1); cv2.putText(c,str(x0+gx),(gx*2+2,h*2-4),0,0.35,(0,255,255),1) if (x0+gx)%50==0 else None
    for gy in range(0,h,25): cv2.line(c,(0,gy*2),(w*2,gy*2),(0,255,255) if (y0+gy)%100==0 else (90,90,90),1); cv2.putText(c,str(y0+gy),(2,gy*2+12),0,0.35,(0,255,255),1) if (y0+gy)%50==0 else None
    if trk:
        d=trk['data']; ts=[k[0] for k in d]; tt=min(max(t,ts[0]),ts[-1]); i=min(max(int(np.searchsorted(ts,tt)),1),len(d)-1); a,b=d[i-1],d[i]; u=(tt-a[0])/max(1e-9,b[0]-a[0])
        hx,hy,hr=[a[j]+(b[j]-a[j])*u for j in (1,2,3)]
        cv2.circle(c,(int((hx-x0)*2),int((hy-y0)*2)),int(hr*1.5*2),(0,255,0),2)
    cv2.putText(c,f"{t:.2f}",(4,30),0,0.8,(0,0,255),2); tiles.append(c); t+=step
cols=6
while len(tiles)%cols: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(outp,np.vstack([np.hstack(tiles[i:i+cols]) for i in range(0,len(tiles),cols)]),[cv2.IMWRITE_JPEG_QUALITY,85])
