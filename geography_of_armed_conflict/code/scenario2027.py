import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, geopandas as gpd, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SC='/tmp/claude-0/-home-user-data/9733eecb-671a-58d6-bbe9-c7d4a40590cd/scratchpad'
GEO=f'{SC}/geo/nga_admin1.geojson'; RAW=f'{SC}/acled_raw'; BASE='/home/user/data/geography_of_armed_conflict'
pop={'Kano':16253549,'Lagos':15772884,'Katsina':9300382,'Kaduna':8324285,'Bauchi':7540663,'Oyo':7512855,
'Anambra':7299910,'Rivers':7234973,'Jigawa':6979080,'Niger':6720617,'Benue':6687706,'Borno':6651590,
'Ogun':6445275,'Sokoto':6163187,'Delta':6107543,'Imo':6067722,'Kebbi':6001610,'Akwa Ibom':5780581,
'Edo':5527810,'Zamfara':5517793,'Ondo':5469707,'Plateau':5400974,'Enugu':5396098,'Adamawa':5236948,
'Kogi':5053734,'Abia':4841943,'FCT':4802443,'Gombe':4623462,'Yobe':4350401,'Taraba':4331885,
'Kwara':4259613,'Osun':4237396,'Cross River':4175020,'Ebonyi':4007155,'Nasarawa':3632239,'Ekiti':3398177,'Bayelsa':2394725}
states=list(pop); norm=lambda n:{'Nassarawa':'Nasarawa','Federal Capital Territory':'FCT'}.get(str(n).strip(),str(n).strip())
pv=pd.read_excel(f'{RAW}/pv.xlsx',sheet_name='Data'); pv['Admin1']=pv['Admin1'].map(norm)
yr=pv.groupby(['Admin1','Year'])['Fatalities'].sum().unstack(fill_value=0)
natyr={t:int(pv[pv.Year==t]['Fatalities'].sum()) for t in range(2011,2026)}
g=gpd.read_file(GEO)[['adm1_name','geometry']].copy(); g['state']=g['adm1_name'].replace({'Federal Capital Territory':'FCT'})
g=g.set_index('state').loc[states]; geom=g.geometry.values; n=len(states)
W=np.zeros((n,n))
for i in range(n):
    for j in range(i+1,n):
        if geom[i].touches(geom[j]) or geom[i].intersects(geom[j]): W[i,j]=W[j,i]=1
Wr=np.divide(W,W.sum(1)[:,None],where=W.sum(1)[:,None]!=0)
def fy(s,t): return float(yr.loc[s,t]) if (s in yr.index and t in yr.columns) else 0.0
L=np.log1p; E=np.expm1; Fy={t:np.array([fy(s,t) for s in states]) for t in range(2011,2026)}
ann26=np.array([fy(s,2026)*12/10 for s in states])

# ---- election-year empirical check (national) ----
elec={2015:natyr[2015],2019:natyr[2019],2023:natyr[2023]}
prior={2015:natyr[2014],2019:natyr[2018],2023:natyr[2022]}
ratios={y:elec[y]/prior[y] for y in elec}
print("Election-year national fatalities vs prior year:")
for y in elec: print(f"  {y}: {elec[y]:,} vs {prior[y]:,} (prior) -> ratio {ratios[y]:.2f}")
print(f"  mean election/prior ratio = {np.mean(list(ratios.values())):.2f}  (>1 would mean uplift)")

# ---- baseline 2027 sim (same model) ----
Xr=[]; Yr=[]
for t in range(2015,2026):
    Xr.append(np.column_stack([np.ones(n),L(Fy[t-1]),Wr@L(Fy[t-1])])); Yr.append(L(Fy[t]))
X=np.vstack(Xr); Y=np.concatenate(Yr); beta,_,_,_=np.linalg.lstsq(X,Y,rcond=None); b0,b1,b2=beta
resid=Y-X@beta
rng=np.random.default_rng(7); Nd=5000
Sim26=L(ann26)+rng.normal(0,0.15,(Nd,n))
Yh27=b0+b1*Sim26+b2*(Sim26@Wr.T)
Sim27=np.clip(E(Yh27+rng.choice(resid,size=(Nd,n))),0,None)   # baseline fatalities (Nd,n)

# ---- election scenarios: illustrative multiplicative uplift on the 2027 draws ----
scen={'Baseline (no election effect)':1.00,'Moderate election uplift (+20%)':1.20,'Severe election uplift (+40%)':1.40}
rows=[]; natdist={}
for name,f in scen.items():
    S=Sim27*f; nat=S.sum(1); natdist[name]=nat
    rows.append([name,int(np.median(nat)),int(nat.mean()),int(np.percentile(nat,10)),int(np.percentile(nat,90))])
res=pd.DataFrame(rows,columns=['Scenario','National median','National mean','Lo80','Hi80'])
print("\n2027 national scenarios:"); print(res.to_string(index=False))
json.dump({'elec_ratios':{str(k):round(v,2) for k,v in ratios.items()},
 'elec_mean_ratio':round(float(np.mean(list(ratios.values()))),2),
 'scenarios':rows}, open(f'{SC}/scenario27_results.json','w'),indent=1)

# ---- scenario fan chart ----
fig,ax=plt.subplots(figsize=(8.2,5))
yrs=[2023,2024,2025,2026]; central=[natyr[2023],natyr[2024],natyr[2025],int(ann26.sum())]
ax.plot(yrs,central,'o-',color='#1F2A44',lw=2,label='actual / annualised-so-far')
cols={'Baseline (no election effect)':'#4C72B0','Moderate election uplift (+20%)':'#E6845A','Severe election uplift (+40%)':'#8C2D04'}
for name,f in scen.items():
    nat=natdist[name]; med=int(np.median(nat))
    ax.plot([2026,2027],[int(ann26.sum()),med],'o--',color=cols[name],lw=1.8,label=name)
    ax.fill_between([2026,2027],[int(ann26.sum()),int(np.percentile(nat,10))],[int(ann26.sum()),int(np.percentile(nat,90))],color=cols[name],alpha=.08)
ax.set_xticks([2023,2024,2025,2026,2027]); ax.set_ylabel('National political-violence fatalities')
ax.set_title('2027 national conflict: baseline vs. illustrative election-year scenarios\n(shaded = 80% intervals; uplifts are assumed, not estimated)',fontweight='bold',fontsize=10.5)
ax.legend(frameon=False,fontsize=7.5,loc='upper left'); ax.spines[['top','right']].set_visible(False)
plt.tight_layout(); plt.savefig(f'{BASE}/outputs/fig_election_scenarios_2027.png',dpi=150); plt.close()
print("\nSaved fig_election_scenarios_2027.png, scenario27_results.json")
