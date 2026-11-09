import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, geopandas as gpd, json
from libpysal.weights import Queen, KNN, DistanceBand
from esda.moran import Moran
import spreg
SC='/tmp/claude-0/-home-user-data/9733eecb-671a-58d6-bbe9-c7d4a40590cd/scratchpad'
GEO=f'{SC}/geo/nga_admin1.geojson'; BASE='/home/user/data/geography_of_armed_conflict'
RAW=f'{SC}/acled_raw'
d=pd.read_csv(f'{BASE}/outputs/determinants_merged.csv')
g=gpd.read_file(GEO)[['adm1_name','geometry']].copy()
g['state']=g['adm1_name'].replace({'Federal Capital Territory':'FCT'})
gdf=g.merge(d,on='state').reset_index(drop=True)

R={}  # results container
z=lambda s:(s-s.mean())/s.std(ddof=1)
gdf['ln_rate']=np.log(gdf['pv_fat_per100k_2020_2025'].clip(lower=.01))
gdf['ln_density']=np.log(gdf['pop_density']); gdf['ln_igr']=np.log(gdf['igr_per_capita'])
# standardised predictors
for c in ['ln_density','temp_c','ruggedness','ln_igr','rainfall_mm']:
    gdf['Z_'+c]=z(gdf[c])
Xcols=['Z_ln_density','border_state','Z_temp_c','Z_ruggedness','Z_ln_igr']
Xlab=['Population density (ln, z)','Border state','Temperature (z)','Terrain ruggedness (z)','Economic resources (ln IGR, z)']
y=gdf['ln_rate'].values.reshape(-1,1); X=gdf[Xcols].values

# ---- descriptives ----
desc_vars={'pv_fat_per100k_2020_2025':'Conflict death rate (/100k)','pv_fatalities_2020_2025':'Conflict deaths (count)',
 'pop_density':'Population density (/km²)','temp_c':'Temperature (°C)','rainfall_mm':'Rainfall (mm)',
 'ruggedness':'Terrain ruggedness (elev. SD)','igr_per_capita':'IGR per capita (₦)','mpi_headcount_pct':'Poverty (MPI %)',
 'border_state':'Border state (0/1)'}
R['descriptives']=[[lbl,round(gdf[c].mean(),2),round(gdf[c].std(ddof=1),2),round(gdf[c].min(),2),round(gdf[c].max(),2)]
                   for c,lbl in desc_vars.items()]
R['N']=len(gdf)

# ---- correlations (key) ----
cormat_vars={'ln_rate':'1. Conflict rate (ln)','Z_ln_density':'2. Pop density (ln)','border_state':'3. Border',
 'Z_temp_c':'4. Temperature','Z_ruggedness':'5. Ruggedness','Z_ln_igr':'6. Economic (IGR)'}
cm=gdf[list(cormat_vars)].corr().round(2)
R['corr_labels']=list(cormat_vars.values()); R['corr']=cm.values.tolist()

# ---- weights ----
wq=Queen.from_dataframe(gdf); wq.transform='r'
wk=KNN.from_dataframe(gdf,k=5); wk.transform='r'
# inverse distance on centroids
cent=gdf.geometry.representative_point()
wd=DistanceBand.from_dataframe(gdf.assign(geometry=cent), threshold=3.0, binary=False, alpha=-1.0, silence_warnings=True); wd.transform='r'

# ---- Global Moran's I of outcome ----
mi=Moran(y.flatten(), wq, permutations=999)
R['moran']={'I':round(mi.I,3),'EI':round(mi.EI,3),'z':round(mi.z_sim,3),'p':round(mi.p_sim,3)}

# ---- OLS + LM ----
ols=spreg.OLS(y,X,w=wq,name_x=Xcols,name_y='ln_rate',spat_diag=True,moran=True)
def tp(obj,attr):
    v=getattr(obj,attr); return [round(v[0],3),round(v[1],3)]
R['ols']={'beta':[round(float(b),3) for b in ols.betas.flatten()],
          'se':[round(float(s),3) for s in np.array(ols.std_err).flatten()],
          't':[[round(t,3),round(p,4)] for t,p in ols.t_stat],
          'r2':round(ols.r2,3),'ar2':round(ols.ar2,3),'f':[round(ols.f_stat[0],3),round(ols.f_stat[1],4)],
          'aic':round(ols.aic,2),'lm_lag':tp(ols,'lm_lag'),'rlm_lag':tp(ols,'rlm_lag'),
          'lm_error':tp(ols,'lm_error'),'rlm_error':tp(ols,'rlm_error'),
          'moran_res':[round(ols.moran_res[0],3),round(ols.moran_res[2],4)]}
# max VIF
from numpy.linalg import lstsq
vifs=[]
for i,c in enumerate(Xcols):
    others=[cc for cc in Xcols if cc!=c]; Xo=np.column_stack([np.ones(len(gdf))]+[gdf[o] for o in others])
    yc=gdf[c].values; b,_,_,_=lstsq(Xo,yc,rcond=None); r2=1-((yc-Xo@b)**2).sum()/((yc-yc.mean())**2).sum()
    vifs.append(1/(1-r2))
R['max_vif']=round(max(vifs),2)

# ---- SAR / SEM / SDM ----
sar=spreg.ML_Lag(y,X,w=wq,name_x=Xcols); sem=spreg.ML_Error(y,X,w=wq,name_x=Xcols)
def grab(m,spatialattr):
    b=[round(float(x),3) for x in m.betas.flatten()]
    se=[round(float(x),3) for x in np.array(m.std_err).flatten()]
    zp=[[round(t,3),round(p,4)] for t,p in m.z_stat]
    return {'beta':b,'se':se,'zp':zp,'aic':round(m.aic,2),'logll':round(float(m.logll),2),
            'pr2':round(m.pr2,3),'spatial':round(float(getattr(m,spatialattr)),3),
            'spatial_p':round(m.z_stat[-1][1],4)}
R['sar']=grab(sar,'rho'); R['sem']=grab(sem,'lam')
# SAR impacts (simple): total=b/(1-rho)
rho=float(np.ravel(sar.rho)[0])
betas_flat=np.ravel(sar.betas)
R['impacts']=[]
for i,c in enumerate(Xcols):
    bk=float(betas_flat[i+1]); tot=bk/(1-rho); dir_=bk; ind=tot-dir_
    R['impacts'].append([Xlab[i],round(dir_,3),round(ind,3),round(tot,3)])
try:
    sdm=spreg.ML_Lag(y,X,w=wq,name_x=Xcols,slx_lags=1)
    R['sdm']={'aic':round(sdm.aic,2),'rho':round(float(sdm.rho),3),'pr2':round(sdm.pr2,3)}
except Exception as e: R['sdm']={'error':str(e)[:80]}

# ---- robustness: rho/lambda under alt weights ----
R['robust']=[]
for wl,wname in [(wq,'Queen contiguity'),(wk,'k-nearest (k=5)'),(wd,'Inverse distance')]:
    s1=spreg.ML_Lag(y,X,w=wl); s2=spreg.ML_Error(y,X,w=wl)
    mi2=Moran(y.flatten(),wl,permutations=999)
    R['robust'].append([wname,round(float(s1.rho),3),round(s1.z_stat[-1][1],3),
                        round(float(s2.lam),3),round(s2.z_stat[-1][1],3),round(mi2.I,3),round(mi2.p_sim,3)])

# ---- spatial panel FE lag (dynamic-ish: temporal lag regressor) ----
try:
    pv=pd.read_excel(f'{RAW}/pv.xlsx',sheet_name='Data')
    pv['Admin1']=pv['Admin1'].map(lambda n:{'Nassarawa':'Nasarawa','Federal Capital Territory':'FCT'}.get(str(n).strip(),str(n).strip()))
    yr=pv.groupby(['Admin1','Year'])['Fatalities'].sum().unstack(fill_value=0)
    popcol=[c for c in gdf.columns if c=='population' or c.startswith('population_')][0]
    pop=dict(zip(gdf['state'],gdf[popcol]))
    order=list(gdf['state'])
    yrs=list(range(2011,2026))
    M=np.array([[np.log(yr.loc[s,t]/pop[s]*1e5+0.5) if (s in yr.index and t in yr.columns) else np.log(0.5) for t in yrs] for s in order])
    Ypan=M[:,1:]            # t=2012..2025 (N x 14)
    Xpan=M[:,:-1].reshape(len(order),-1)   # temporal lag t=2011..2024
    pan=spreg.Panel_FE_Lag(Ypan, Xpan, wq, name_y='ln_rate', name_x=['ln_rate_lag1'])
    pb=np.ravel(pan.betas)
    R['panel']={'ok':True,'N':len(order),'T':int(Ypan.shape[1]),
        'rho':round(float(np.ravel(pan.rho)[0]),3),'rho_p':round(float(pan.z_stat[-1][1]),4),
        'beta_tlag':round(float(pb[0]),3),'beta_tlag_p':round(float(pan.z_stat[0][1]),4),
        'pr2':round(float(getattr(pan,'pr2',float('nan'))),3)}
except Exception as e:
    R['panel']={'ok':False,'error':str(e)[:160]}

def _ser(o):
    import numpy as _np
    if isinstance(o,(_np.integer,)): return int(o)
    if isinstance(o,(_np.floating,)): return float(o)
    if isinstance(o,_np.ndarray): return o.tolist()
    return str(o)
json.dump(R, open(f'{SC}/pub_results.json','w'), indent=1, default=_ser)
print("Moran I:",R['moran'])
print("OLS LM-lag",R['ols']['lm_lag'],"LM-err",R['ols']['lm_error'],"max VIF",R['max_vif'])
print("SAR rho",R['sar']['spatial'],"p",R['sar']['spatial_p'],"AIC",R['sar']['aic'])
print("SEM lam",R['sem']['spatial'],"p",R['sem']['spatial_p'],"AIC",R['sem']['aic'],"| OLS AIC",R['ols']['aic'])
print("Robustness:",*R['robust'],sep="\n  ")
print("PANEL:",R['panel'])
print("\nSaved pub_results.json")
