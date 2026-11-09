import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, geopandas as gpd, json
from scipy import stats
SC='/tmp/claude-0/-home-user-data/9733eecb-671a-58d6-bbe9-c7d4a40590cd/scratchpad'
GEO=f'{SC}/geo/nga_admin1.geojson'; RAW=f'{SC}/acled_raw'; BASE='/home/user/data/geography_of_armed_conflict'
R=json.load(open(f'{SC}/pub_results.json'))

pop={'Kano':16253549,'Lagos':15772884,'Katsina':9300382,'Kaduna':8324285,'Bauchi':7540663,'Oyo':7512855,
'Anambra':7299910,'Rivers':7234973,'Jigawa':6979080,'Niger':6720617,'Benue':6687706,'Borno':6651590,
'Ogun':6445275,'Sokoto':6163187,'Delta':6107543,'Imo':6067722,'Kebbi':6001610,'Akwa Ibom':5780581,
'Edo':5527810,'Zamfara':5517793,'Ondo':5469707,'Plateau':5400974,'Enugu':5396098,'Adamawa':5236948,
'Kogi':5053734,'Abia':4841943,'FCT':4802443,'Gombe':4623462,'Yobe':4350401,'Taraba':4331885,
'Kwara':4259613,'Osun':4237396,'Cross River':4175020,'Ebonyi':4007155,'Nasarawa':3632239,
'Ekiti':3398177,'Bayelsa':2394725}
north={'Kano','Katsina','Kaduna','Jigawa','Sokoto','Kebbi','Zamfara','Bauchi','Borno','Adamawa','Gombe','Yobe','Taraba','Niger','Benue','Plateau','Kogi','Kwara','Nasarawa','FCT'}
mpi={'Zamfara':71.87,'Sokoto':70.74,'Bauchi':75.36,'Kano':40,'Katsina':61.13,'Kaduna':34.09,'Jigawa':70,'Kebbi':75,'Borno':53.89,'Yobe':63.02,'Adamawa':39.10,'Gombe':50,'Taraba':56.70,'Niger':44.56,'Benue':27.02,'Plateau':42.47,'Kogi':28,'Kwara':20,'Nasarawa':30,'FCT':10.18,'Lagos':4.5,'Oyo':12,'Ogun':9,'Ondo':12,'Osun':8,'Ekiti':12,'Anambra':2.04,'Imo':5,'Enugu':13,'Abia':9.40,'Ebonyi':38,'Rivers':12,'Delta':14,'Akwa Ibom':9.81,'Edo':12,'Cross River':30,'Bayelsa':22}
norm=lambda n:{'Nassarawa':'Nasarawa','Federal Capital Territory':'FCT'}.get(str(n).strip(),str(n).strip())
pv=pd.read_excel(f'{RAW}/pv.xlsx',sheet_name='Data'); pv['Admin1']=pv['Admin1'].map(norm)
yr=pv.groupby(['Admin1','Year'])['Fatalities'].sum().unstack(fill_value=0)
g=gpd.read_file(GEO)[['adm1_name','geometry']].copy(); g['state']=g['adm1_name'].replace({'Federal Capital Territory':'FCT'})
g=g.set_index('state').loc[list(pop)]
geom=g.geometry.values; n=len(pop); states=list(pop)
Wc=np.zeros((n,n))
for i in range(n):
    for j in range(i+1,n):
        if geom[i].touches(geom[j]) or geom[i].intersects(geom[j]): Wc[i,j]=Wc[j,i]=1
Wr=np.divide(Wc,Wc.sum(1)[:,None],where=Wc.sum(1)[:,None]!=0)
def fy(s,t): return float(yr.loc[s,t]) if (s in yr.index and t in yr.columns) else 0.0
L=np.log1p

# ---- prediction models (LOOCV via PRESS) ----
d=pd.DataFrame({'state':states})
d['fat_2025']=[fy(s,2025) for s in states]; d['fat_2024']=[fy(s,2024) for s in states]
d['hist']=[np.mean([fy(s,y) for y in (2022,2023,2024)]) for s in states]
d['mpi']=[mpi[s] for s in states]; d['pop']=[pop[s] for s in states]; d['north']=[1 if s in north else 0 for s in states]
f24=np.array([fy(s,2024) for s in states]); d['splag']=Wr@f24
y=L(d['fat_2025'].values)
def loocv(cols):
    X=np.column_stack([np.ones(n)]+[ (L(d[c].values) if c in('fat_2024','hist','splag','pop') else d[c].values) for c in cols])
    beta,_,_,_=np.linalg.lstsq(X,y,rcond=None); yhat=X@beta; resid=y-yhat
    H=X@np.linalg.pinv(X.T@X)@X.T; h=np.diag(H); loo=resid/(1-h); TSS=((y-y.mean())**2).sum()
    return round(1-(resid**2).sum()/TSS,3), round(1-(loo**2).sum()/TSS,3), yhat
mods={'M1 Persistence (prior-year violence)':['fat_2024'],
 'M2 + spatial spillover':['fat_2024','splag'],
 'M3 + 3-year history':['hist','splag'],
 'M4 + structural covariates':['hist','splag','mpi','pop','north']}
R['pred']={'r_persist':round(np.corrcoef(L(d.fat_2024),y)[0,1],3),'models':[]}
for nm,cols in mods.items():
    r2,r2cv,yhat=loocv(cols); R['pred']['models'].append([nm,r2,r2cv])
    if nm.startswith('M4'): d['pred_fat']=np.expm1(yhat); d['resid']=(y-yhat)
rp=d.sort_values('resid',ascending=False)
R['pred']['pos']=[[r['state'],int(r['fat_2024']),int(r['fat_2025']),int(round(r['pred_fat'])),round(r['resid'],2)] for _,r in rp.head(4).iterrows()]
R['pred']['neg']=[[r['state'],int(r['fat_2024']),int(r['fat_2025']),int(round(r['pred_fat'])),round(r['resid'],2)] for _,r in rp.tail(4).iloc[::-1].iterrows()]

# ---- flow: mean-centre drift + directed edges count ----
cent=g.geometry.representative_point(); cx=cent.x.values; cy=cent.y.values
years=list(range(2010,2026)); F=np.array([[fy(s,t) for t in years] for s in states])
mc=np.array([(np.average(cx,weights=F[:,k]),np.average(cy,weights=F[:,k])) if F[:,k].sum()>0 else (np.nan,np.nan) for k in range(len(years))])
from math import atan2,degrees,hypot
dx=mc[-1,0]-mc[0,0]; dy=mc[-1,1]-mc[0,1]; bearing=(degrees(atan2(dx,dy))+360)%360; km=hypot(dx,dy)*111
R['flow']={'drift_km':round(km),'bearing':round(bearing)}
ed=pd.read_csv(f'{BASE}/outputs/flow_edges.csv')
R['flow']['n_edges']=int(len(ed))
R['flow']['key']=[[r['from'],r['to'],round(r['coef'],2),round(r['p'],3)] for _,r in ed[ed['from'].isin(['Kebbi','Kaduna','Benue'])].head(4).iterrows()]

def _ser(o):
    if isinstance(o,(np.integer,)):return int(o)
    if isinstance(o,(np.floating,)):return float(o)
    if isinstance(o,np.ndarray):return o.tolist()
    return str(o)
json.dump(R,open(f'{SC}/final_results.json','w'),indent=1,default=_ser)
print("pred models:",R['pred']['models'])
print("r persist:",R['pred']['r_persist'])
print("pos surprises:",R['pred']['pos'])
print("neg surprises:",R['pred']['neg'])
print("flow:",R['flow'])
print("panel:",R['panel'])
print("saved final_results.json")
