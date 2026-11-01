# Estimate toddler head position from red-pajama blob. Output JSON keyframes per frame.
import cv2, numpy as np, sys, json
src, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_POS_MSEC, t0*1000)
out=[]
while True:
    t = cap.get(cv2.CAP_PROP_POS_MSEC)/1000
    ok, f = cap.read()
    if not ok or t > t1: break
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    m = (((hsv[...,0]<8)|(hsv[...,0]>168)) & (hsv[...,1]>110) & (hsv[...,2]>45)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n<2: out.append([round(t,3),None]); continue
    i = 1+np.argmax(st[1:,cv2.CC_STAT_AREA])
    x,y,w,h,a = st[i]
    if a < 150: out.append([round(t,3),None]); continue
    ys,xs = np.where(lab==i)
    top = ys.min(); band = ys < top + max(6,h*0.12)
    cx = xs[band].mean()
    # shoulder width ~ width of rows near top+0.2h
    rows = (ys > top+h*0.1)&(ys < top+h*0.3)
    sw = (np.percentile(xs[rows],95)-np.percentile(xs[rows],5)) if rows.sum()>10 else w
    out.append([round(t,3), [round(float(cx),1), int(top), int(sw), int(w), int(h)]])
json.dump(out, open(sys.argv[4],"w"))
print(len(out), "frames", fps)
