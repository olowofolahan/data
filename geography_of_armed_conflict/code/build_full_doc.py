import json, numpy as np
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
SC='/tmp/claude-0/-home-user-data/9733eecb-671a-58d6-bbe9-c7d4a40590cd/scratchpad'
R=json.load(open(f'{SC}/final_results.json'))
OUT='/home/user/data/geography_of_armed_conflict/Method_and_Results_APA7.docx'
doc=Document()
s=doc.styles['Normal']; s.font.name='Times New Roman'; s.font.size=Pt(12)
s.paragraph_format.line_spacing_rule=WD_LINE_SPACING.DOUBLE; s.paragraph_format.space_after=Pt(0)
from docx.shared import RGBColor
NAVY=RGBColor(0x1F,0x2A,0x44)
def fp(p):
    p=float(p);
    return "< .001" if p<.001 else "= "+("%.3f"%p).lstrip("0") if p<1 else "= %.2f"%p
def nz(x,d=2):
    s=f"%.{d}f"%float(x);
    return s.replace("0.",".",1) if (s[:2]=="0." or s[:3]=="-0.") else s
def star(p):
    p=float(p); return "***" if p<.001 else "**" if p<.01 else "*" if p<.05 else "†" if p<.10 else ""
def H(t,size=12,bold=True,italic=False,align='left',before=8,after=4):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(before); p.paragraph_format.space_after=Pt(after)
    p.alignment={'left':WD_ALIGN_PARAGRAPH.LEFT,'center':WD_ALIGN_PARAGRAPH.CENTER}[align]
    r=p.add_run(t); r.bold=bold; r.italic=italic; r.font.size=Pt(size); r.font.color.rgb=NAVY if bold else None; return p
def body(t):
    p=doc.add_paragraph(); p.paragraph_format.first_line_indent=Inches(0.5); p.add_run(t); return p
def setc(c,t,bold=False,italic=False,align='left',size=10.5):
    c.text=''; pr=c.paragraphs[0]; pr.alignment={'left':WD_ALIGN_PARAGRAPH.LEFT,'center':WD_ALIGN_PARAGRAPH.CENTER,'right':WD_ALIGN_PARAGRAPH.RIGHT}[align]
    pr.paragraph_format.line_spacing_rule=WD_LINE_SPACING.SINGLE; pr.paragraph_format.space_after=Pt(1); pr.paragraph_format.space_before=Pt(1)
    r=pr.add_run(t); r.bold=bold; r.italic=italic; r.font.size=Pt(size); r.font.name='Times New Roman'
def bd(cell,edges):
    tcPr=cell._tc.get_or_add_tcPr(); tb=OxmlElement('w:tcBorders')
    for e in ['top','bottom']:
        el=OxmlElement('w:'+e)
        if e in edges: el.set(qn('w:val'),'single'); el.set(qn('w:sz'),'6'); el.set(qn('w:color'),'000000')
        else: el.set(qn('w:val'),'nil')
        tb.append(el)
    tcPr.append(tb)
def table(num,title,headers,rows,note=None,colw=None,fs=10.5):
    H(f"Table {num}",before=8,after=0); H(title,bold=False,italic=True,after=4)
    t=doc.add_table(rows=1+len(rows),cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.LEFT
    for j,h in enumerate(headers): setc(t.rows[0].cells[j],h,italic=True,align='center' if j else 'left',size=fs)
    for i,row in enumerate(rows,1):
        for j,v in enumerate(row): setc(t.rows[i].cells[j],str(v),align='center' if j else 'left',size=fs)
    for j in range(len(headers)): bd(t.rows[0].cells[j],['top','bottom']); bd(t.rows[-1].cells[j],['bottom'])
    if colw:
        for j,w in enumerate(colw):
            for rr in t.rows: rr.cells[j].width=Inches(w)
    if note:
        p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(2)
        a=p.add_run("Note. "); a.italic=True; a.font.size=Pt(10); a.font.name='Times New Roman'
        b=p.add_run(note); b.font.size=Pt(10); b.font.name='Times New Roman'
    doc.add_paragraph()

# ===== TITLE =====
H("Method and Results",size=15,align='center',before=0,after=4)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("The Spatial Structure, Determinants, Predictability, and Diffusion of Armed Conflict Across Nigerian States, 2010–2025"); r.italic=True

# ===================== METHOD =====================
H("Method",size=13)
H("Study Design and Units of Analysis",italic=True)
body("We conducted a subnational, spatially explicit analysis of armed conflict across Nigeria's 37 "
 "first-order administrative units (36 states and the Federal Capital Territory, FCT). The design "
 "combined (a) a cross-sectional analysis of the 2020–2025 period, (b) an annual state panel "
 "spanning 2010–2025, and (c) an out-of-sample prediction of the most recent year (2025). All "
 "analyses were ecological (state-level); no individual-level data were used.")

H("Data Sources and Measures",italic=True)
body("Armed conflict. The dependent variable was the intensity of political violence, drawn from the "
 "Armed Conflict Location & Event Data Project (ACLED), which geolocates conflict events from a triangulated "
 "review of local and international sources. Following ACLED's taxonomy, political violence comprised "
 "battles, violence against civilians, explosions/remote violence, and mob violence. State-year fatality "
 "counts were aggregated and expressed as deaths per 100,000 population; the measure was positively "
 "skewed and was log-transformed for modelling.")
body("Structural covariates. Guided by the conflict literature, five theoretically motivated predictors "
 "were assembled at the state level: population density (persons/km²; log-transformed), international-border "
 "location (dummy; cross-border exposure to Niger, Chad, Cameroon, and Benin), mean annual temperature "
 "(°C) and terrain ruggedness (within-state standard deviation of elevation), both derived by zonal "
 "statistics from the WorldClim 2.1 digital elevation and climate surfaces, and economic resources "
 "(2023 internally generated revenue per capita; National Bureau of Statistics). Supplementary measures "
 "(multidimensional poverty, rainfall, displacement, and OpenStreetMap-derived police stations) were also "
 "compiled. Continuous predictors were standardised (z scores) for the regression models, which held "
 "multicollinearity to acceptable levels (maximum variance inflation factor = "+str(R['max_vif'])+").")
body("Spatial weights. Spatial relationships were encoded with a row-standardised, first-order "
 "queen-contiguity weights matrix. Robustness was assessed using k-nearest-neighbour (k = 5) and "
 "inverse-distance weights.")

H("Analytic Strategy",italic=True)
body("First, spatial dependence in conflict intensity was assessed with the global Moran's I statistic "
 "(999 permutations) and local indicators of spatial association. Second, structural determinants were "
 "estimated by ordinary least squares (OLS) with Anselin's Lagrange multiplier (LM) diagnostics, followed "
 "by maximum-likelihood spatial lag (SAR), spatial error (SEM), and spatial Durbin (SDM) models; SAR "
 "effects were decomposed into direct, indirect, and total impacts. Third, to exploit the space–time "
 "structure, a state-fixed-effects dynamic spatial-lag panel (2012–2025) was estimated, including both "
 "a spatial lag of the outcome and a one-year temporal lag. Fourth, the predictability of 2025 conflict "
 "was evaluated by regressing 2025 fatalities on pre-2025 information only, with model skill assessed by "
 "exact leave-one-out cross-validation (LOOCV, via the PRESS statistic); forecast residuals identified "
 "states whose 2025 outcomes departed from their predicted trajectory. Fifth, the direction of conflict "
 "diffusion was characterised by (a) the fatality-weighted mean centre of violence tracked annually and "
 "(b) a directed neighbour lead–lag network estimating whether a state's prior-year violence predicted "
 "its neighbour's current violence, net of the neighbour's own persistence. Analyses used Python 3.13 "
 "(spreg 1.9, libpysal, esda).")

# ===================== RESULTS =====================
H("Results",size=13)

H("Descriptive Statistics and Bivariate Associations",italic=True)
body("Table 1 summarises the study variables. Conflict was highly concentrated, ranging from near zero "
 "to 270 deaths per 100,000. Zero-order correlations (Table 2) indicated that conflict intensity was "
 "negatively associated with population density and positively associated with border location and "
 "temperature.")
table(1,"Descriptive Statistics for Study Variables (N = 37 States)",["Variable","M","SD","Min","Max"],
 [[r[0], (nz(r[1]) if abs(r[1])<1 else f"{r[1]:,.2f}"), f"{r[2]:,.2f}", f"{r[3]:,.2f}", f"{r[4]:,.2f}"] for r in R['descriptives']],
 note="IGR = internally generated revenue; MPI = Multidimensional Poverty Index. Conflict measures cover 2020–2025.",
 colw=[2.5,0.95,0.95,0.95,0.95],fs=10)
cl=R['corr_labels']; cm=R['corr']
rows=[[cl[i]]+[(nz(cm[i][j]) if j<=i else "") for j in range(len(cl))] for i in range(len(cl))]
table(2,"Zero-Order Correlations Among Key Variables",["Variable"]+[str(i+1) for i in range(len(cl))],rows,
 note="Conflict rate log-transformed; continuous predictors standardised. |r| ≥ .33 is significant at p < .05 (two-tailed).",
 colw=[1.8]+[0.6]*len(cl),fs=9)

H("Spatial Clustering of Conflict",italic=True)
m=R['moran']
body(f"Conflict intensity was significantly spatially clustered, Moran's I = {nz(m['I'],3)}, "
 f"z = {m['z']:.2f}, p {fp(m['p'])}, with a contiguous high-intensity belt across the North-West and "
 "North-Central zones and a low-intensity southern bloc. Plain OLS was therefore potentially mis-specified, "
 "motivating the spatial models below.")

H("Structural Determinants: OLS and Spatial Regression",italic=True)
o=R['ols']; _lo=o['beta'][1]-1.96*o['se'][1]; _hi=o['beta'][1]+1.96*o['se'][1]
body(f"The OLS model explained a modest share of variance, R² = {nz(o['r2'],3)}, adjusted R² = "
 f"{nz(o['ar2'],3)}, F(5, 31) = {o['f'][0]:.2f}, p {fp(o['f'][1])}. No predictor attained conventional "
 f"statistical significance in the multivariable model; population density was the strongest correlate but "
 f"fell short of the .05 threshold, b = {nz(o['beta'][1],2)}, 95% CI [{nz(_lo,2)}, {nz(_hi,2)}], "
 f"p {fp(o['t'][1][1])}. Its zero-order association was, however, significant (r = −.48, p = .002), "
 "indicating attenuation under multicollinearity among the spatially patterned covariates. Anselin's LM "
 f"tests were non-significant for both a spatial lag (LM = {o['lm_lag'][0]:.2f}, p {fp(o['lm_lag'][1])}) and "
 f"a spatial error (LM = {o['lm_error'][0]:.2f}, p {fp(o['lm_error'][1])}) process, and no residual spatial "
 f"autocorrelation remained (Moran's I = {nz(o['moran_res'][0],3)}, p {fp(o['moran_res'][1])}). Consistent "
 f"with this, the autoregressive parameters in the spatial models were non-significant (SAR ρ = "
 f"{nz(R['sar']['spatial'],2)}, p {fp(R['sar']['spatial_p'])}; SEM λ = {nz(R['sem']['spatial'],2)}, "
 f"p {fp(R['sem']['spatial_p'])}), with comparable fit (Table 3). Impact decomposition confirmed negligible "
 "cross-sectional spillovers (indirect effects near zero).")
pred=['Population density (ln, z)','Border state','Temperature (z)','Terrain ruggedness (z)','Economic resources (ln IGR, z)']
rows=[]
for i,lbl in enumerate(pred):
    k=i+1
    rows.append([lbl,
      f"{nz(o['beta'][k])}{star(o['t'][k][1])} ({nz(o['se'][k])})",
      f"{nz(R['sar']['beta'][k])}{star(R['sar']['zp'][k][1])} ({nz(R['sar']['se'][k])})",
      f"{nz(R['sem']['beta'][k])}{star(R['sem']['zp'][k][1])} ({nz(R['sem']['se'][k])})"])
rows.append(["Spatial parameter (ρ / λ)","—",f"{nz(R['sar']['spatial'])}",f"{nz(R['sem']['spatial'])}"])
rows.append(["R² / Pseudo-R²",nz(o['r2']),nz(R['sar']['pr2']),nz(R['sem']['pr2'])])
rows.append(["AIC",f"{o['aic']:.1f}",f"{R['sar']['aic']:.1f}",f"{R['sem']['aic']:.1f}"])
table(3,"OLS and Maximum-Likelihood Spatial Regression Models Predicting Log Conflict Intensity",
 ["Predictor","OLS b (SE)","SAR b (SE)","SEM b (SE)"],rows,
 note="N = 37. Row-standardised queen-contiguity weights. ρ = spatial lag parameter; λ = spatial error parameter. †p < .10. *p < .05. **p < .01. ***p < .001.",
 colw=[2.4,1.45,1.45,1.45],fs=9.5)
table(4,"Robustness of Spatial Parameters Across Weight Matrices",
 ["Weights","SAR ρ","p","SEM λ","p","Moran's I","p"],
 [[r[0],nz(r[1]),nz(r[2]),nz(r[3]),nz(r[4]),nz(r[5]),nz(r[6],3)] for r in R['robust']],
 note="Moran's I computed on the dependent variable (999 permutations).",colw=[1.7,0.8,0.7,0.8,0.7,0.9,0.7],fs=10)

H("Space–Time Dynamics: Dynamic Spatial Panel",italic=True)
pn=R['panel']
body(f"The weak cross-sectional autoregression reflected two features: the spatially patterned covariates "
 f"absorbed between-state clustering, and N = 37 underpowered maximum-likelihood estimation of ρ. "
 f"Exploiting the annual panel resolved both. In a state-fixed-effects dynamic spatial-lag model "
 f"(N = {pn['N']} × T = {pn['T']}), spatial diffusion was strong and highly significant, ρ = "
 f"{nz(pn['rho'],3)}, p {fp(pn['rho_p'])}, as was temporal persistence, b = {nz(pn['beta_tlag'],3)}, "
 f"p {fp(pn['beta_tlag_p'])} (within-R² = {nz(pn['pr2'],3)}). A state's conflict in a given year rose "
 "with both its own prior-year violence and the contemporaneous violence of its neighbours, net of stable "
 "state characteristics.")

H("Out-of-Sample Prediction of 2025 Conflict",italic=True)
pr=R['pred']
body(f"Conflict in 2025 was highly predictable from pre-2025 information. Prior-year violence alone "
 f"correlated r = {nz(pr['r_persist'],2)} with 2025 fatalities. Cross-validated performance improved as "
 "diffusion and history were added (Table 5), with a model combining three-year violence history and "
 f"neighbours' prior violence achieving LOOCV R² = {nz(pr['models'][2][2],3)}; adding static structural "
 f"covariates did not improve out-of-sample skill (LOOCV R² = {nz(pr['models'][3][2],3)}). Thus "
 "predictability derived from conflict dynamics rather than structure.")
table(5,"Out-of-Sample Predictive Performance for 2025 Conflict (Leave-One-Out Cross-Validation)",
 ["Model","In-sample R²","LOOCV R²"],
 [[r[0],nz(r[1],3),nz(r[2],3)] for r in pr['models']],
 note="N = 37. Outcome = log(1 + 2025 fatalities). LOOCV via the PRESS statistic.",colw=[3.3,1.3,1.3],fs=10)
body("Forecast residuals isolated departures from trajectory (Table 6). The largest positive residual, "
 f"Kwara (actual = {pr['pos'][0][2]} deaths vs. predicted ≈ {pr['pos'][0][3]}), signalled an emergent "
 "hotspot as banditry breached a previously quiet state; the largest negative residual, Kaduna "
 f"(actual = {pr['neg'][0][2]} vs. predicted ≈ {pr['neg'][0][3]}), marked a sharp de-escalation. "
 "Residuals on small base counts were treated as noise.")
table(6,"States With the Largest Forecast Residuals for 2025",
 ["State","2024","2025","Predicted","Residual (log)"],
 [["Under-predicted (emergent)","","","",""]]+[[r[0],r[1],r[2],r[3],nz(r[4])] for r in pr['pos'][:3]]+
 [["Over-predicted (de-escalating)","","","",""]]+[[r[0],r[1],r[2],r[3],nz(r[4])] for r in pr['neg'][:3]],
 note="Residuals from the full model (history + spillover + structural covariates).",colw=[2.6,0.8,0.8,1.1,1.2],fs=10)

H("Spatial Diffusion and Direction of Flow",italic=True)
fl=R['flow']
body(f"Two analyses characterised the direction of spread. The fatality-weighted mean centre of violence "
 f"migrated approximately {fl['drift_km']} km over 2010–2025, tracing an arc: north-east toward the "
 "North-East theatre during the 2014–2015 Boko Haram peak, then reversing west and south-west into the "
 "North-West–North-Central banditry belt by 2024–2025. The directed neighbour lead–lag network "
 f"yielded {fl['n_edges']} diffusion edges at p < .10; substantively, violence propagated into the "
 "North-Central corridor (e.g., Kebbi → Niger, b = "
 f"{[e[2] for e in fl['key'] if e[0]=='Kebbi'][0]}, p = {[e[3] for e in fl['key'] if e[0]=='Kebbi'][0]:.3f}; "
 f"Kaduna → Niger, b = {[e[2] for e in fl['key'] if e[0]=='Kaduna'][0]}, p = {[e[3] for e in fl['key'] if e[0]=='Kaduna'][0]:.3f}), "
 "consistent with the Kwara breakout identified in the forecast residuals. These directional results are "
 "exploratory: lead–lag co-movement may reflect common shocks or unobserved actor mobility, low-base "
 "edges are volatile, and annual state-level resolution cannot capture sub-state routes.")

H("Summary of Findings",italic=True)
body("Conflict intensity is spatially clustered but poorly explained by static structural conditions; its "
 "clustering is generated by temporal persistence and spatial diffusion, as shown by the dynamic spatial "
 "panel and the cross-validated prediction. The centre of violence has shifted from the North-East to the "
 "North-West–North-Central, and directed diffusion into the North-Central corridor foreshadowed the "
 "emergence of new hotspots. The findings support a conflict-trap and contagion account of Nigerian "
 "insecurity and argue for space–time rather than purely cross-sectional designs.")

doc.save(OUT)
from pypdf import PdfReader
print("WROTE",OUT)
