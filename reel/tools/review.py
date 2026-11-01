# Draw mask circles from a track json onto frames; make contact sheet. args: src track.json t0 t1 step out.jpg
import cv2, numpy as np, sys, json
src, tj, t0, t1, step, outp = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
sys.path.insert(0, "/home/user/data/reel/tools")
from maskmodel import head_at
tr = json.load(open(tj))
cap=cv2.VideoCapture(src); tiles=[]
t=t0
while t<=t1+1e-6:
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000); ok,f=cap.read()
    if not ok: break
    h = head_at(tr,t)
    if h:
        cx,cy,r=h; cv2.circle(f,(int(cx),int(cy)),int(r),(0,255,0),2)
    f=cv2.resize(f,(240,427)); cv2.putText(f,f"{t:.2f}",(4,16),0,0.5,(0,255,255),1)
    # grid
    for gx in range(0,240,30): cv2.line(f,(gx,0),(gx,427),(80,80,80),1)
    for gy in range(0,427,30): cv2.line(f,(0,gy),(240,gy),(80,80,80),1)
    tiles.append(f); t+=step
cols=8
while len(tiles)%cols: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[i:i+cols]) for i in range(0,len(tiles),cols)]
cv2.imwrite(outp,np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,85])
