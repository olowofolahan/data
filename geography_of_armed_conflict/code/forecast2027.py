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
g=gpd.read_file(GEO)[['adm1_name','geometry']].copy(); g['state']=g['adm1_name'].replace({'Federal Capital Territory':'FCT'})
g=g.set_index('state').loc[states]; geom=g.geometry.values; n=len(states)
W=np.zeros((n,n))
for i in range(n):
    for j in range(i+1,n):
        if geom[i].touches(geom[j]) or geom[i].intersects(geom[j]): W[i,j]=W[j,i]=1
Wr=np.divide(W,W.sum(1)[:,None],where=W.sum(1)[:,None]!=0)
def fy(s,t): return float(yr.loc[s,t]) if (s in yr.index and t in yr.columns) else 0.0
L=np.log1p; E=np.expm1; Fy={t:np.array([fy(s,t) for s in states]) for t in range(2011,2026)}
ann26=np.array([fy(s,2026)*12/10 for s in states])   # annualised 10-month 2026

# ---- fit pooled one-step model (2015-2025) ----
Xr=[]; Yr=[]
for t in range(2015,2026):
    Xr.append(np.column_stack([np.ones(n),L(Fy[t-1]),Wr@L(Fy[t-1])])); Yr.append(L(Fy[t]))
X=np.vstack(Xr); Y=np.concatenate(Yr); beta,_,_,_=np.linalg.lstsq(X,Y,rcond=None)
resid=Y-X@beta; b0,b1,b2=beta

# ---- Monte Carlo recursive projection to 2027 (fan chart) ----
rng=np.random.default_rng(7); N=5000
s26=0.15                                   # uncertainty in annualising 10->12 months of 2026
base26=L(ann26)
Sim26=base26+rng.normal(0,s26,(N,n))       # 2026 input distribution (anchored on real data)
Splag=Sim26@Wr.T
Yh27=b0+b1*Sim26+b2*Splag
Res=rng.choice(resid,size=(N,n),replace=True)
Sim27=E(Yh27+Res)                          # fatalities, (N,n)
Sim27=np.clip(Sim27,0,None)
med=np.median(Sim27,0); mean=Sim27.mean(0)
lo80=np.percentile(Sim27,10,0); hi80=np.percentile(Sim27,90,0)
lo95=np.percentile(Sim27,2.5,0); hi95=np.percentile(Sim27,97.5,0)
natd=Sim27.sum(1)

df=pd.DataFrame({'state':states,'pop':[pop[s] for s in states],'fat_2025':Fy[2025],'annualised_2026':np.round(ann26),
 'proj_2027_median':np.round(med),'proj_2027_mean':np.round(mean),
 'lo80':np.round(lo80),'hi80':np.round(hi80),'lo95':np.round(lo95),'hi95':np.round(hi95)})
df['proj_2027_rate_per100k']=(df['proj_2027_median']/df['pop']*1e5).round(1)
df=df.sort_values('proj_2027_median',ascending=False)
df.to_csv(f'{BASE}/outputs/projection_2027.csv',index=False)

print(f"model: b0={b0:.3f} persist={b1:.3f} spill={b2:.3f}  resid n={len(resid)}")
print(f"National 2027 projection: median={int(np.median(natd)):,}  mean={int(natd.mean()):,}  "
      f"80% PI [{int(np.percentile(natd,10)):,}, {int(np.percentile(natd,90)):,}]")
print(f" (ref: 2025 actual=15,771; 2026 annualised-so-far={int(ann26.sum()):,})")
print("\nTop 10 projected 2027 (median fatalities, 80% PI):")
print(df[['state','fat_2025','annualised_2026','proj_2027_median','lo80','hi80']].head(10).to_string(index=False))

out={'beta':[round(b0,3),round(b1,3),round(b2,3)],
 'nat_med':int(np.median(natd)),'nat_mean':int(natd.mean()),
 'nat_lo80':int(np.percentile(natd,10)),'nat_hi80':int(np.percentile(natd,90)),
 'ann26':int(ann26.sum()),
 'top':[[r['state'],int(r['fat_2025']),int(r['annualised_2026']),int(r['proj_2027_median']),int(r['lo80']),int(r['hi80'])] for _,r in df.head(10).iterrows()]}
json.dump(out,open(f'{SC}/proj27_results.json','w'),indent=1)

# ---- map ----
gg=g.reset_index().merge(df,on='state')
fig,ax=plt.subplots(figsize=(9,8))
gg['_v']=np.log10(gg['proj_2027_rate_per100k'].clip(lower=0.1))
gg.plot(column='_v',cmap='YlOrRd',linewidth=.4,edgecolor='#555',ax=ax,legend=True,legend_kwds={'shrink':.5,'label':'projected deaths per 100k (log colour)'})
for _,r in gg.nlargest(7,'proj_2027_rate_per100k').iterrows():
    ax.annotate(r['state'],(r.geometry.representative_point().x,r.geometry.representative_point().y),fontsize=6.5,ha='center',fontweight='bold')
ax.set_title('Projected armed-conflict intensity, 2027 (baseline scenario)\nMonte-Carlo recursive projection; median deaths per 100,000',fontweight='bold',fontsize=11); ax.axis('off')
plt.tight_layout(); plt.savefig(f'{BASE}/outputs/map10_projection2027.png',dpi=150); plt.close()

# ---- national fan chart 2023-2027 ----
hist_nat={t:int(Fy[t].sum()) for t in range(2023,2026)}
fig,ax=plt.subplots(figsize=(8,5))
yrs=[2023,2024,2025,2026,2027]
central=[hist_nat[2023],hist_nat[2024],hist_nat[2025],int(ann26.sum()),int(np.median(natd))]
ax.plot(yrs[:4],central[:4],'o-',color='#1F2A44',lw=2,label='actual / annualised-so-far')
ax.plot(yrs[3:],central[3:],'o--',color='#8C2D04',lw=2,label='projection (median)')
ax.fill_between([2026,2027],[int(ann26.sum()),int(np.percentile(natd,10))],[int(ann26.sum()),int(np.percentile(natd,90))],color='#8C2D04',alpha=.15,label='80% interval (2027)')
ax.fill_between([2026,2027],[int(ann26.sum()),int(np.percentile(natd,2.5))],[int(ann26.sum()),int(np.percentile(natd,97.5))],color='#8C2D04',alpha=.07)
ax.set_xticks(yrs); ax.set_ylabel('National political-violence fatalities'); ax.set_title('National conflict: actuals and 2027 projection (fan)',fontweight='bold',fontsize=11)
ax.annotate('2026 = Jan–Oct annualised',(2026,int(ann26.sum())),fontsize=7,xytext=(0,8),textcoords='offset points',ha='center')
ax.legend(frameon=False,fontsize=8); ax.spines[['top','right']].set_visible(False)
plt.tight_layout(); plt.savefig(f'{BASE}/outputs/fig_national_fan_2027.png',dpi=150); plt.close()
print("\nSaved projection_2027.csv, map10_projection2027.png, fig_national_fan_2027.png, proj27_results.json")
