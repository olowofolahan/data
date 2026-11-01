import numpy as np, wave, sys
sys.path.insert(0,'tools'); from edl import *
SR=48000
def rd(p):
    w=wave.open(p); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).reshape(-1,w.getnchannels())/32768.0; return x
mus=rd('edit/audio/music.wav'); T=90.0; N=int(SR*T)
nat=np.zeros((N,2)); duck=np.ones(N)
src={v:rd(f'edit/audio/{v}_48.wav') for v in ['v17','v19','v20','v21']}
tl,_=timeline()
for st,s,tin,dur,trk,note,opt in tl:
    if s.startswith('P'): continue
    dpre=DISSOLVE.get(round(st,3),0)/2; dpost=DISSOLVE.get(round(st+dur,3),0)/2
    a=st-dpre; b=st+dur+dpost; f_in=max(0.04,dpre*2); f_out=max(0.04,dpost*2)
    i0=int(a*SR); i1=min(N,int(b*SR)); n=i1-i0
    j0=int((tin-dpre)*SR); seg=src[s][j0:j0+n]
    if len(seg)<n: seg=np.pad(seg,((0,n-len(seg)),(0,0)))
    env=np.ones(n); fi=int(f_in*SR); fo=int(f_out*SR)
    env[:fi]=np.linspace(0,1,fi); env[-fo:]=np.minimum(env[-fo:],np.linspace(1,0,fo))
    g=0.45*opt.get('nat',1.0)
    nat[i0:i1]+=seg*(env*g)[:,None]
    if opt.get('nat',1.0)>=1.4:
        dk=np.ones(n)*0.55; r=int(0.25*SR); dk[:r]=np.linspace(1,0.55,r); dk[-r:]=np.linspace(0.55,1,r)
        duck[i0:i1]=np.minimum(duck[i0:i1],dk)
# gentle highpass on natural sound to remove rumble (one-pole)
y=np.zeros_like(nat); a=np.exp(-2*np.pi*80/SR); prev_x=np.zeros(2); prev_y=np.zeros(2)
for k in range(0,N,SR):
    pass
from numpy.fft import rfft,irfft
for c in range(2):
    X=rfft(nat[:,c]); f=np.fft.rfftfreq(N,1/SR); X*=np.clip((f-60)/60,0,1); nat[:,c]=irfft(X,N)
mix=mus[:N]*duck[:,None]*0.9+nat
fo=int(1.3*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
mix[:int(0.3*SR)]*=np.linspace(0,1,int(0.3*SR))[:,None]
mix/=max(1e-9,np.abs(mix).max())/0.9
w=wave.open('edit/audio/mix.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()
print('mix ok')
