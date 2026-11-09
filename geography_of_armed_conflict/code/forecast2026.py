import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, geopandas as gpd, json
from scipy import stats
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
# partial 2026 (10 months) annualised x12/10
part26={s:(float(yr.loc[s,2026]) if (s in yr.index and 2026 in yr.columns) else 0.0) for s in states}
ann26={s:part26[s]*12/10 for s in states}

g=gpd.read_file(GEO)[['adm1_name','geometry']].copy(); g['state']=g['adm1_name'].replace({'Federal Capital Territory':'FCT'})
g=g.set_index('state').loc[states]; geom=g.geometry.values; n=len(states)
W=np.zeros((n,n))
for i in range(n):
    for j in range(i+1,n):
        if geom[i].touches(geom[j]) or geom[i].intersects(geom[j]): W[i,j]=W[j,i]=1
Wr=np.divide(W,W.sum(1)[:,None],where=W.sum(1)[:,None]!=0)
def fy(s,t): return float(yr.loc[s,t]) if (s in yr.index and t in yr.columns) else 0.0
L=np.log1p; E=np.expm1
Fy={t:np.array([fy(s,t) for s in states]) for t in range(2011,2026)}

# ---- pooled one-step model: log(fat_t) ~ log(fat_{t-1}) + splag(log fat_{t-1}) ----
# persistence on LAST YEAR's level (preserves level during escalation, less mean-reversion)
Xr=[]; yr_=[]
for t in range(2015,2026):
    sl=Wr@L(Fy[t-1])
    Xr.append(np.column_stack([np.ones(n),L(Fy[t-1]),sl])); yr_.append(L(Fy[t]))
X=np.vstack(Xr); Y=np.concatenate(yr_)
beta,_,_,_=np.linalg.lstsq(X,Y,rcond=None)
resid=Y-X@beta; sigma=resid.std(ddof=3)
R2=1-(resid**2).sum()/((Y-Y.mean())**2).sum()

# ---- forecast 2026 (Duan smearing for unbiased mean; empirical residual quantiles for PIs) ----
sl26=Wr@L(Fy[2025]); Xf=np.column_stack([np.ones(n),L(Fy[2025]),sl26])
yhat=Xf@beta
# Duan smearing: E[Y]=mean_i expm1(yhat + resid_i)
pred=np.array([np.mean(E(yh+resid)) for yh in yhat])
q=lambda p:np.quantile(resid,p)
lo80=E(yhat+q(.10)); hi80=E(yhat+q(.90)); lo95=E(yhat+q(.025)); hi95=E(yhat+q(.975))

df=pd.DataFrame({'state':states,'pop':[pop[s] for s in states],
 'fat_2024':Fy[2024],'fat_2025':Fy[2025],'partial_2026_10mo':[part26[s] for s in states],
 'annualised_2026':[round(ann26[s]) for s in states],
 'forecast_2026':np.round(pred),'lo80':np.round(lo80),'hi80':np.round(hi80),'lo95':np.round(lo95),'hi95':np.round(hi95)})
df['forecast_rate_per100k']=(df['forecast_2026']/df['pop']*1e5).round(1)
df['pct_change_vs2025']=((df['forecast_2026']-df['fat_2025'])/df['fat_2025'].replace(0,np.nan)*100).round(0)
df=df.sort_values('forecast_2026',ascending=False)
df.to_csv(f'{BASE}/outputs/forecast_2026.csv',index=False)

# ---- validation vs annualised partial 2026 ----
m=df[df['annualised_2026']>0]
rp=stats.pearsonr(L(m['forecast_2026']),L(m['annualised_2026']))
rs=stats.spearmanr(m['forecast_2026'],m['annualised_2026'])
# coverage: share of states whose annualised actual falls in 80% PI
cov=((df['annualised_2026']>=df['lo80'])&(df['annualised_2026']<=df['hi80'])).mean()

print(f"Pooled model (2015-2025 transitions): in-sample R2={R2:.3f}, sigma(log)={sigma:.3f}")
print(f"beta: const={beta[0]:.3f} hist={beta[1]:.3f} spillover={beta[2]:.3f}")
print(f"National forecast 2026 total = {int(df['forecast_2026'].sum()):,}  (2025 actual=15,771; 2026 annualised-so-far={int(sum(ann26.values())):,})")
print(f"Validation vs annualised partial-2026: Pearson(log) r={rp[0]:.2f} p={rp[1]:.3f}; Spearman rho={rs.correlation:.2f}")
print(f"80% PI coverage of annualised actuals: {cov*100:.0f}%")
print("\nTop 10 forecast 2026 (fatalities):")
print(df[['state','fat_2025','forecast_2026','lo80','hi80','annualised_2026','pct_change_vs2025']].head(10).to_string(index=False))

out={'R2':round(R2,3),'sigma':round(sigma,3),'beta':[round(float(b),3) for b in beta],
 'nat_forecast':int(df['forecast_2026'].sum()),'nat_ann_sofar':int(sum(ann26.values())),
 'val_pearson':[round(rp[0],2),round(rp[1],3)],'val_spearman':round(rs.correlation,2),'cov80':round(cov,2),
 'top':[[r['state'],int(r['fat_2025']),int(r['forecast_2026']),int(r['lo80']),int(r['hi80']),int(r['annualised_2026'])] for _,r in df.head(10).iterrows()]}
json.dump(out,open(f'{SC}/forecast26_results.json','w'),indent=1)

# ---- maps ----
gg=g.reset_index().merge(df,on='state')
fig,ax=plt.subplots(figsize=(9,8))
gg['_v']=np.log10(gg['forecast_rate_per100k'].clip(lower=0.1))
gg.plot(column='_v',cmap='YlOrRd',linewidth=.4,edgecolor='#555',ax=ax,legend=True,legend_kwds={'shrink':.5,'label':'forecast deaths per 100k (log colour)'})
c=gg.geometry.representative_point()
for _,r in gg.nlargest(7,'forecast_rate_per100k').iterrows():
    ax.annotate(r['state'],(r.geometry.representative_point().x,r.geometry.representative_point().y),fontsize=6.5,ha='center',fontweight='bold')
ax.set_title('Forecast armed-conflict intensity, 2026\n(one-step-ahead model; deaths per 100,000)',fontweight='bold',fontsize=12); ax.axis('off')
plt.tight_layout(); plt.savefig(f'{BASE}/outputs/map9_forecast2026.png',dpi=150); plt.close()

fig,ax=plt.subplots(figsize=(7.5,6.5))
ax.scatter(df['forecast_2026'],df['annualised_2026'],s=45,c='#8C2D04',alpha=.8,edgecolor='white')
mx=max(df['forecast_2026'].max(),df['annualised_2026'].max())
ax.plot([0,mx],[0,mx],'k--',lw=1,alpha=.6,label='1:1')
for _,r in df.iterrows():
    if r['forecast_2026']>800 or r['annualised_2026']>800: ax.annotate(r['state'],(r['forecast_2026'],r['annualised_2026']),fontsize=7,xytext=(3,3),textcoords='offset points')
ax.set_xscale('symlog'); ax.set_yscale('symlog')
ax.set_xlabel('Forecast 2026 fatalities (model)'); ax.set_ylabel('Annualised partial-2026 actual (Jan–Oct × 12/10)')
ax.set_title(f'2026 forecast vs. actual-so-far\nPearson(log) r = {rp[0]:.2f}',fontweight='bold')
ax.legend(frameon=False,fontsize=8); ax.spines[['top','right']].set_visible(False)
plt.tight_layout(); plt.savefig(f'{BASE}/outputs/fig_forecast2026_validation.png',dpi=150); plt.close()
print("\nSaved forecast_2026.csv, map9_forecast2026.png, fig_forecast2026_validation.png, forecast26_results.json")
