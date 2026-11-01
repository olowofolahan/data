# Original synthesized arrangement of "Deck the Halls" (traditional, public domain). 96 BPM, 36 bars = 90 s.
import numpy as np, wave
SR=48000; BPM=96; BEAT=60/BPM; BAR=4*BEAT; DUR=90.0
N=int(SR*(DUR+3)); L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
NOTE={'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
def hz(n):  # 'C4'
    name=n[:-1]; o=int(n[-1]); return 440*2**((NOTE[name]+12*(o+1)-69)/12)
def add(sig,t,pan=0.0,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig)); s=sig[:j-i]*g
    L[i:j]+=s*np.sqrt(0.5*(1-pan)); R[i:j]+=s*np.sqrt(0.5*(1+pan))
def bell(f,dur=1.6,amp=0.25):
    t=np.arange(int(SR*dur))/SR
    s=sum(a*np.sin(2*np.pi*f*m*t)*np.exp(-t*d) for m,a,d in [(1,1,2.2),(2,0.35,3.5),(3.0,0.12,5),(4.07,0.08,7),(5.4,0.03,9)])
    s*=np.minimum(1,t/0.003); return amp*s
def pad(freqs,dur,amp=0.05,att=0.6,rel=0.8):
    t=np.arange(int(SR*(dur+rel)))/SR; s=np.zeros_like(t)
    for f in freqs:
        for det in (-0.004,0,0.004):
            for h in range(1,7): s+=np.sin(2*np.pi*f*(1+det)*h*t+h)/h**1.7
    env=np.minimum(1,t/att)*np.where(t<dur,1,np.exp(-(t-dur)/rel*3))
    return amp*s*env/len(freqs)
def bass(f,dur=0.9,amp=0.22):
    t=np.arange(int(SR*dur))/SR
    s=(np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*np.exp(-t*3.0)*np.minimum(1,t/0.005); return amp*s
def sleigh(amp=0.03):
    n=int(SR*0.12); x=rng.standard_normal(n); x=np.diff(np.diff(x,prepend=0),prepend=0)
    t=np.arange(n)/SR; jingle=sum(np.sin(2*np.pi*f*t) for f in (5200,6800,8100))*0.3
    return amp*(x*0.5+jingle*rng.standard_normal(n)*0.5)*np.exp(-t*35)
def kick(amp=0.25):
    t=np.arange(int(SR*0.35))/SR; f=45+50*np.exp(-t*30)
    return amp*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def swell(dur,amp=0.06):
    n=int(SR*dur); t=np.arange(n)/SR; x=rng.standard_normal(n); x=np.convolve(x,np.ones(6)/6,'same')
    return amp*x*(t/dur)**2.5
CH={'C':['C3','E3','G3','C4'],'F':['F2','A3','C4','F3'],'G':['G2','B3','D4','G3'],'G7':['G2','B3','F4','D4'],
    'Am':['A2','C4','E4','A3'],'Dm':['D3','F3','A3','D4'],'Em':['E3','G3','B3','E4'],'D7':['D3','F#3','A3','C4'],'Fmaj7':['F2','A3','C4','E4'],'Gsus':['G2','C4','D4','G3']}
def root(c): return hz(CH[c][0])
def arps(c,t0,dur,step,amp=0.10,oct=1):
    notes=[hz(n)*2**oct for n in CH[c][1:]]+[hz(CH[c][1])*2**(oct+1)]
    k=0;t=t0
    while t<t0+dur-1e-6:
        add(bell(notes[k%len(notes)],1.2,amp),t,pan=0.35*np.sin(k)); k+=1; t+=step
def chordbar(c,t0,dur,padamp=0.05,bassamp=0.2,arp=None,arpamp=0.09,kickon=False,bells=False):
    add(pad([hz(n) for n in CH[c]],dur,padamp),t0,pan=0)
    if bassamp:
        for b in range(int(round(dur/BEAT))):
            if b%2==0: add(bass(root(c)),t0+b*BEAT,g=bassamp/0.22)
    if arp: arps(c,t0,dur,arp,arpamp)
    if kickon:
        for b in range(int(round(dur/BEAT))):
            if b%2==0: add(kick(),t0+b*BEAT)
    if bells:
        for e in range(int(round(dur/(BEAT/2)))):
            add(sleigh(0.035 if e%2 else 0.05),t0+e*BEAT/2+0.012,pan=0.3)
# ---- melody (C major, octave 5) as (note, beats)
m=[[('G5',1.5),('F5',.5),('E5',1),('D5',1)],[('C5',1),('D5',1),('E5',1),('C5',1)],
   [('D5',.5),('E5',.5),('F5',.5),('D5',.5),('E5',1.5),('D5',.5)],[('C5',1),('B4',1),('C5',2)]]
m+= m[:4]
m+=[[('D5',1.5),('E5',.5),('F5',1),('D5',1)],[('E5',1.5),('F5',.5),('G5',1),('D5',1)],
    [('E5',.5),('F#5',.5),('G5',1),('A5',.5),('B5',.5),('C6',1)],[('B5',1),('A5',1),('G5',2)],
    [('G5',1.5),('F5',.5),('E5',1),('D5',1)],[('C5',1),('D5',1),('E5',1),('C5',1)],
    [('A5',.5),('A5',.5),('A5',.5),('A5',.5),('G5',1.5),('F5',.5)],[('E5',1),('D5',1),('C5',2)]]
mch=[['C','C'],['C','C'],['Dm','G7'],['C','C'],['C','C'],['C','C'],['Dm','G7'],['G','C'],
     ['G','G'],['C','G'],['Em','D7'],['G','G'],['C','C'],['C','C'],['F','G7'],['C','C']]
def play_melody(bars,t0,amp=0.22,chords=True,full=True):
    for bi in bars:
        t=t0+(bi-bars[0])*BAR; tt=t
        for n,b in m[bi]:
            add(bell(hz(n),1.8,amp),tt,pan=-0.1); add(bell(hz(n)*2,1.0,amp*0.18),tt,pan=0.2); tt+=b*BEAT
        if chords:
            for h,c in enumerate(mch[bi]):
                chordbar(c,t+h*BAR/2,BAR/2,padamp=0.045,bassamp=0.2 if full else 0.12,arp=BEAT/2 if full else None,arpamp=0.05,kickon=full,bells=full)
# ---- arrangement
bar=lambda k:k*BAR
# Intro bars 0-1: shimmer
chordbar('Fmaj7',0,BAR,padamp=0.04,bassamp=0,arp=BEAT/2,arpamp=0.08)
chordbar('C',bar(1),BAR,padamp=0.045,bassamp=0,arp=BEAT/2,arpamp=0.08)
# Verse bars 2-9 gentle (setup)
prog=['C','F','C','G','Am','F','C','G']
for i,c in enumerate(prog):
    chordbar(c,bar(2+i),BAR,padamp=0.05,bassamp=0.16,arp=BEAT/2,arpamp=0.085,bells=(i>=4))
# Melody bars 10-25 (decorating)
play_melody(list(range(16)),bar(10),amp=0.2)
# Build bars 26-27, hold bar 28 (lights on at 70.0 = bar 28 downbeat)
chordbar('F',bar(26),BAR,padamp=0.06,bassamp=0.18,arp=BEAT/2,arpamp=0.08)
chordbar('Gsus',bar(27),BAR,padamp=0.07,bassamp=0.18,arp=BEAT/4,arpamp=0.07)
add(swell(BAR*0.9,0.05),bar(28)-BAR*0.9)
# BLOOM at bar 28: big chord + bell cascade
for k,n in enumerate(['C5','E5','G5','C6','E6','G6','C7']):
    add(bell(hz(n),3.0,0.12),bar(28)+k*0.06,pan=-0.6+0.2*k)
add(kick(0.3),bar(28))
chordbar('C',bar(28),BAR,padamp=0.08,bassamp=0.22,arp=BEAT/2,arpamp=0.07,bells=True)
chordbar('Am',bar(29),BAR,padamp=0.07,bassamp=0.2,arp=BEAT/2,arpamp=0.07,bells=True,kickon=True)
chordbar('F',bar(30),BAR,padamp=0.07,bassamp=0.2,arp=BEAT/2,arpamp=0.07,bells=True,kickon=True)
chordbar('G',bar(31),BAR,padamp=0.07,bassamp=0.2,arp=BEAT/2,arpamp=0.07,bells=True,kickon=True)
# Final line bars 32-35 (melody bars 12-15), softer, ending ring
play_melody([12,13,14,15],bar(32),amp=0.2,full=False)
add(pad([hz(n) for n in CH['C']],2.5,0.05),bar(35)+BAR*0.5)
for k,n in enumerate(['G5','C6','E6','G6']): add(bell(hz(n),3.0,0.06),bar(35)+BAR*0.5+k*0.09)
# ---- reverb (synthetic IR)
irn=int(SR*2.2); t=np.arange(irn)/SR
def ir(seed):
    r=np.random.default_rng(seed).standard_normal(irn)*np.exp(-t*3.2); r[:int(0.012*SR)]=0; return r/np.sqrt((r**2).sum())
def conv(x,h):
    n=1<<int(np.ceil(np.log2(len(x)+len(h)))); return np.fft.irfft(np.fft.rfft(x,n)*np.fft.rfft(h,n),n)[:len(x)]
Lw=L+0.35*conv(L,ir(1)); Rw=R+0.35*conv(R,ir(2))
out=np.stack([Lw,Rw],1)[:int(SR*DUR)]
# end fade
fo=int(SR*1.5); out[-fo:]*=np.linspace(1,0,fo)[:,None]**1.5
out/=np.abs(out).max()/0.8
w=wave.open('edit/audio/music.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).astype(np.int16).tobytes()); w.close(); print("music ok", out.shape[0]/SR)
