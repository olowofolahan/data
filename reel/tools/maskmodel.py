import numpy as np
def head_at(tr, t):
    """tr: {'type':'red', 'data':[[t,[cx,top,sw,w,h]|None],...], 'k':..} or {'type':'kf','data':[[t,cx,cy,r],...]}"""
    if tr['type']=='kf':
        d=tr['data']; ts=[k[0] for k in d]
        if not d: return None
        if t<ts[0]-0.05 or t>ts[-1]+0.05: return None
        i=np.searchsorted(ts,t)
        if i<=0: k=d[0]; return (k[1],k[2],k[3]) if k[1] is not None else None
        if i>=len(d): k=d[-1]; return (k[1],k[2],k[3]) if k[1] is not None else None
        a,b=d[i-1],d[i]
        if a[1] is None or b[1] is None: return None
        u=(t-a[0])/(b[0]-a[0]+1e-9)
        return tuple(a[j]+(b[j]-a[j])*u for j in (1,2,3))
    return None
