import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, geopandas as gpd
from scipy import stats
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SC='/tmp/claude-0/-home-user-data/9733eecb-671a-58d6-bbe9-c7d4a40590cd/scratchpad'
GEO=f'{SC}/geo/nga_admin1.geojson'; RAW=f'{SC}/acled_raw'; BASE='/home/user/data/geography_of_armed_conflict'

pop={'Kano':16253549,'Lagos':15772884,'Katsina':9300382,'Kaduna':8324285,'Bauchi':7540663,'Oyo':7512855,
'Anambra':7299910,'Rivers':7234973,'Jigawa':6979080,'Niger':6720617,'Benue':6687706,'Borno':6651590,
'Ogun':6445275,'Sokoto':6163187,'Delta':6107543,'Imo':6067722,'Kebbi':6001610,'Akwa Ibom':5780581,
'Edo':5527810,'Zamfara':5517793,'Ondo':5469707,'Plateau':5400974,'Enugu':5396098,'Adamawa':5236948,
'Kogi':5053734,'Abia':4841943,'FCT':4802443,'Gombe':4623462,'Yobe':4350401,'Taraba':4331885,
'Kwara':4259613,'Osun':4237396,'Cross River':4175020,'Ebonyi':4007155,'Nasarawa':3632239,
'Ekiti':3398177,'Bayelsa':2394725}
norm=lambda n:{'Nassarawa':'Nasarawa','Federal Capital Territory':'FCT'}.get(str(n).strip(),str(n).strip())
pv=pd.read_excel(f'{RAW}/pv.xlsx',sheet_name='Data'); pv['Admin1']=pv['Admin1'].map(norm)
yr=pv.groupby(['Admin1','Year'])['Fatalities'].sum().unstack(fill_value=0)

g=gpd.read_file(GEO)[['adm1_name','geometry']].copy()
g['state']=g['adm1_name'].replace({'Federal Capital Territory':'FCT'})
g=g.set_index('state').loc[list(pop)]
cent=g.geometry.representative_point()
cx=cent.x.values; cy=cent.y.values; states=list(pop)
idx={s:i for i,s in enumerate(states)}
geom=g.geometry.values; n=len(states)
# adjacency (queen)
A=np.zeros((n,n),bool)
for i in range(n):
    for j in range(i+1,n):
        if geom[i].touches(geom[j]) or geom[i].intersects(geom[j]): A[i,j]=A[j,i]=True

years=list(range(2010,2026))
def fat(s,t): return float(yr.loc[s,t]) if (s in yr.index and t in yr.columns) else 0.0
F=np.array([[fat(s,t) for t in years] for s in states])     # n x T
L=np.log1p(F)

# ---- (1) Mean center of violence per year (weighted by fatalities) ----
mc=[]
for k,t in enumerate(years):
    w=F[:,k];
    if w.sum()==0: mc.append((np.nan,np.nan)); continue
    mc.append((np.average(cx,weights=w), np.average(cy,weights=w)))
mc=np.array(mc)
# drift 2010->2025
from math import atan2,degrees,hypot
dx=mc[-1,0]-mc[0,0]; dy=mc[-1,1]-mc[0,1]
bearing=(degrees(atan2(dx,dy))+360)%360   # 0=N,90=E
km=hypot(dx,dy)*111
print(f"Mean-center drift 2010->2025: {km:.0f} km, bearing {bearing:.0f}deg "
      f"({'NE' if 22<bearing<67 else 'E' if bearing<=112 else 'SE' if bearing<=157 else 'S' if bearing<=202 else 'SW' if bearing<=247 else 'W' if bearing<=292 else 'NW' if bearing<=337 else 'N'})")
print("Mean center path (year: lon,lat):")
for t,(x,y) in zip(years,mc):
    if not np.isnan(x): print(f"  {t}: {x:.2f},{y:.2f}")

# ---- (2) Directed lead-lag diffusion (space-time Granger, neighbours) ----
edges=[]
for a in range(n):
    for b in range(n):
        if a==b or not A[a,b]: continue
        # B_t ~ B_{t-1} + A_{t-1}
        yb=L[b,1:]; xb=L[b,:-1]; xa=L[a,:-1]
        X=np.column_stack([np.ones(len(yb)),xb,xa])
        beta,_,_,_=np.linalg.lstsq(X,yb,rcond=None)
        resid=yb-X@beta; dof=len(yb)-3
        if dof<=0: continue
        s2=(resid**2).sum()/dof; cov=s2*np.linalg.pinv(X.T@X); se=np.sqrt(np.diag(cov))
        b2=beta[2]; t2=b2/se[2] if se[2]>0 else 0; p=2*(1-stats.t.cdf(abs(t2),dof))
        if b2>0: edges.append((states[a],states[b],round(b2,3),round(p,3)))
ed=pd.DataFrame(edges,columns=['from','to','coef','p']).sort_values('coef',ascending=False)
sig=ed[ed.p<0.10]
print(f"\nDirected diffusion edges (A_t-1 -> B_t, controlling B's own lag): {len(sig)} at p<.10")
print(sig.head(16).to_string(index=False))
sig.to_csv(f'{BASE}/outputs/flow_edges.csv',index=False)

# ---- map ----
fig,ax=plt.subplots(figsize=(10,9))
g.reset_index().plot(color='#f3f1ee',edgecolor='#bbb',linewidth=.5,ax=ax)
# directed edges (significant), width ~ coef
for _,r in sig.iterrows():
    i,j=idx[r['from']],idx[r['to']]
    ax.annotate('',xy=(cx[j],cy[j]),xytext=(cx[i],cy[i]),
        arrowprops=dict(arrowstyle='-|>',color='#C44E52',lw=0.6+3*r['coef'],alpha=.6,
                        shrinkA=4,shrinkB=4,mutation_scale=12))
# mean-center trajectory
good=~np.isnan(mc[:,0])
ax.plot(mc[good,0],mc[good,1],'-',color='#1F2A44',lw=2.5,zorder=5)
for t,(x,y) in zip(years,mc):
    if not np.isnan(x) and t%3==1 or t in(2010,2025):
        ax.scatter(x,y,s=28,color='#1F2A44',zorder=6)
        ax.annotate(str(t),(x,y),fontsize=7,color='#1F2A44',xytext=(4,4),textcoords='offset points',fontweight='bold')
ax.scatter(mc[0,0],mc[0,1],s=90,facecolor='white',edgecolor='#1F2A44',lw=2,zorder=7)
ax.scatter(mc[-1,0],mc[-1,1],s=110,marker='*',color='#1F2A44',zorder=7)
ax.set_title("Spatial flow of armed conflict in Nigeria, 2010–2025\n"
 "Navy = mean-centre of violence (drift path); red arrows = directed year-on-year diffusion between neighbours",
 fontweight='bold',fontsize=11); ax.axis('off')
plt.tight_layout(); plt.savefig(f'{BASE}/outputs/map8_conflict_flow.png',dpi=150); plt.close()
print("\nSaved map8_conflict_flow.png, flow_edges.csv")
