import json, numpy as np
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
SC='/tmp/claude-0/-home-user-data/9733eecb-671a-58d6-bbe9-c7d4a40590cd/scratchpad'
R=json.load(open(f'{SC}/pub_results.json'))
OUT='/home/user/data/geography_of_armed_conflict/Armed_Conflict_Spatial_Analysis_APA7.docx'

doc=Document()
st=doc.styles['Normal']; st.font.name='Times New Roman'; st.font.size=Pt(12)
st.paragraph_format.line_spacing_rule=WD_LINE_SPACING.DOUBLE
st.paragraph_format.space_after=Pt(0)

def fp(p):  # APA p-value
    p=float(p)
    return "< .001" if p<.001 else "= "+("%.3f"%p).lstrip("0").replace("0.",".") if p<1 else "= %.2f"%p
def nz(x,d=2):  # strip leading zero for |x|<1
    s=f"%.{d}f"%x
    return s.replace("0.",".") if (s.startswith("0.") or s.startswith("-0.")) else s
def star(p):
    p=float(p); return "***" if p<.001 else "**" if p<.01 else "*" if p<.05 else "†" if p<.10 else ""

def H(txt,size=12,bold=True,italic=False,align='left',after=6,before=6):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(before); p.paragraph_format.space_after=Pt(after)
    p.alignment={'left':WD_ALIGN_PARAGRAPH.LEFT,'center':WD_ALIGN_PARAGRAPH.CENTER}[align]
    r=p.add_run(txt); r.bold=bold; r.italic=italic; r.font.size=Pt(size); return p
def body(txt,indent=True):
    p=doc.add_paragraph();
    if indent: p.paragraph_format.first_line_indent=Inches(0.5)
    p.add_run(txt); return p

def set_cell(cell,text,bold=False,italic=False,align='left',size=11):
    cell.text=''; pr=cell.paragraphs[0]; pr.alignment={'left':WD_ALIGN_PARAGRAPH.LEFT,'center':WD_ALIGN_PARAGRAPH.CENTER,'right':WD_ALIGN_PARAGRAPH.RIGHT}[align]
    pr.paragraph_format.line_spacing_rule=WD_LINE_SPACING.SINGLE; pr.paragraph_format.space_after=Pt(2); pr.paragraph_format.space_before=Pt(2)
    run=pr.add_run(text); run.bold=bold; run.italic=italic; run.font.size=Pt(size); run.font.name='Times New Roman'
def _border(cell,edges):
    tcPr=cell._tc.get_or_add_tcPr(); tb=OxmlElement('w:tcBorders')
    for e in ['top','bottom']:
        el=OxmlElement('w:'+e)
        if e in edges: el.set(qn('w:val'),'single'); el.set(qn('w:sz'),'6'); el.set(qn('w:color'),'000000')
        else: el.set(qn('w:val'),'nil')
        tb.append(el)
    tcPr.append(tb)
def apa_table(num,title,headers,rows,note=None,colw=None,fs=11):
    H(f"Table {num}",after=0); H(title,bold=False,italic=True,after=4)
    t=doc.add_table(rows=1+len(rows),cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.LEFT
    t.autofit=True
    for j,h in enumerate(headers): set_cell(t.rows[0].cells[j],h,bold=False,italic=True,align='center' if j else 'left',size=fs)
    for i,row in enumerate(rows,1):
        for j,v in enumerate(row): set_cell(t.rows[i].cells[j],str(v),align='center' if j else 'left',size=fs)
    # APA borders: top & bottom of table, under header
    for j in range(len(headers)):
        _border(t.rows[0].cells[j],['top','bottom'])
        _border(t.rows[-1].cells[j],['bottom'])
    if colw:
        for j,wv in enumerate(colw):
            for r_ in t.rows: r_.cells[j].width=Inches(wv)
    if note:
        p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(2)
        rr=p.add_run("Note. "); rr.italic=True; rr.font.size=Pt(10); rr.font.name='Times New Roman'
        r2=p.add_run(note); r2.font.size=Pt(10); r2.font.name='Times New Roman'
    doc.add_paragraph()

# ===== TITLE =====
H("The Spatial Structure of Armed Conflict Across Nigerian States: A Spatial-Econometric Analysis, 2020–2025",size=14,align='center',after=10)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run("Results and Method (APA 7th edition reporting)").italic=True

# ===== METHOD =====
H("Method")
H("Data and Measures",size=12,italic=True,bold=True,after=2)
body(f"The units of analysis were Nigeria's 37 first-order administrative units (36 states and the "
 f"Federal Capital Territory; N = {R['N']}). The dependent variable was the state-level intensity of "
 "armed conflict, operationalised as political-violence fatalities per 100,000 population over 2020–2025 "
 "(battles, violence against civilians, explosions/remote violence, and mob violence; Armed Conflict "
 "Location & Event Data Project [ACLED]), and analysed on the natural-log scale to correct positive skew. "
 "Structural predictors were population density (persons/km²; log-transformed), international-border "
 "location (dummy), mean annual temperature (°C) and terrain ruggedness (within-state standard deviation "
 "of elevation; WorldClim 2.1), and economic resources (2023 internally generated revenue per capita; "
 "National Bureau of Statistics, log-transformed). Continuous predictors were standardised (z scores).")
H("Analytic Strategy",size=12,italic=True,bold=True,after=2)
body("Spatial dependence in the outcome was first tested with the global Moran's I statistic using a "
 "row-standardised queen-contiguity spatial weights matrix (999 permutations). Ordinary least squares "
 "(OLS) regression was then estimated with Anselin's Lagrange multiplier (LM) diagnostics to adjudicate "
 "between spatial-lag and spatial-error specifications. Maximum-likelihood spatial lag (SAR), spatial "
 "error (SEM), and spatial Durbin (SDM) models were fitted, and SAR effects were decomposed into direct, "
 "indirect, and total impacts. Robustness was assessed under k-nearest-neighbour (k = 5) and "
 "inverse-distance weights. Finally, because conflict is a space–time process, a fixed-effects dynamic "
 "spatial-lag panel model (state fixed effects; annual observations 2012–2025, T = 14) was estimated to "
 "recover the spatial-diffusion and temporal-persistence parameters. Analyses used Python 3.13 with "
 "spreg 1.9 and libpysal/esda.")

# ===== RESULTS =====
H("Results")
H("Descriptive Statistics and Bivariate Associations",size=12,italic=True,bold=True,after=2)
body("Table 1 reports descriptive statistics. Conflict intensity was highly right-skewed, ranging from "
 "near zero to 270 deaths per 100,000. Table 2 reports the correlation matrix; conflict intensity was "
 "negatively associated with population density and positively associated with border location and "
 "temperature.")
apa_table(1,"Descriptive Statistics for Study Variables (N = 37 States)",
 ["Variable","M","SD","Min","Max"],
 [[r[0],nz(r[1]) if abs(r[1])<1 else f"{r[1]:,.2f}",f"{r[2]:,.2f}",f"{r[3]:,.2f}",f"{r[4]:,.2f}"] for r in R['descriptives']],
 note="IGR = internally generated revenue; MPI = Multidimensional Poverty Index. Conflict death rate and deaths cover 2020–2025.",
 colw=[2.6,0.9,0.9,0.9,0.9],fs=10)

cl=R['corr_labels']; cm=R['corr']
rows=[]
for i,lbl in enumerate(cl):
    cells=[lbl]+[(nz(cm[i][j]) if j<=i else "") for j in range(len(cl))]
    rows.append(cells)
apa_table(2,"Zero-Order Correlations Among Key Variables",
 ["Variable"]+[str(i+1) for i in range(len(cl))], rows,
 note="Conflict rate is log-transformed; continuous predictors standardised. Correlations |r| ≥ .33 are significant at p < .05 (two-tailed, N = 37).",
 colw=[1.9]+[0.6]*len(cl),fs=9)

H("Spatial Autocorrelation",size=12,italic=True,bold=True,after=2)
m=R['moran']
body(f"Conflict intensity was significantly spatially clustered, Moran's I = {nz(m['I'],3)}, "
 f"E(I) = {nz(m['EI'],3)}, z = {m['z']:.2f}, p {fp(m['p'])}, indicating that high-conflict states "
 "neighboured other high-conflict states (a contiguous North-West/North-Central belt) rather than being "
 "randomly distributed. Plain OLS was therefore potentially mis-specified.")

H("Determinants: OLS and Spatial Regression Models",size=12,italic=True,bold=True,after=2)
o=R['ols']
body(f"The OLS model explained a modest share of variance, R² = {nz(o['r2'],3)}, "
 f"adjusted R² = {nz(o['ar2'],3)}, F(5, 31) = {o['f'][0]:.2f}, p {fp(o['f'][1])}; multicollinearity "
 f"was negligible (max VIF = {R['max_vif']}). Only population density reached significance "
 f"(b = {nz(o['beta'][1],3)}, p {fp(o['t'][1][1])}). Critically, Anselin's LM diagnostics were "
 f"non-significant for both a spatial lag (LM = {o['lm_lag'][0]:.2f}, p {fp(o['lm_lag'][1])}) and a "
 f"spatial error (LM = {o['lm_error'][0]:.2f}, p {fp(o['lm_error'][1])}) process, and residual spatial "
 f"autocorrelation was absent (Moran's I = {nz(o['moran_res'][0],3)}, p {fp(o['moran_res'][1])}). "
 "Table 3 presents OLS alongside the ML spatial lag and spatial error models; the autoregressive "
 f"parameters were non-significant (SAR ρ = {nz(R['sar']['spatial'],3)}, p {fp(R['sar']['spatial_p'])}; "
 f"SEM λ = {nz(R['sem']['spatial'],3)}, p {fp(R['sem']['spatial_p'])}), and model fit was comparable "
 f"(AIC: OLS = {o['aic']:.1f}, SEM = {R['sem']['aic']:.1f}, SAR = {R['sar']['aic']:.1f}). Thus, once the "
 "spatially patterned covariates were included, no residual spatial dependence remained in the cross-section.")

def coef_cell(beta,se,p):
    return f"{nz(beta,2)}{star(p)}\n({nz(se,2)})"
pred=['Population density (ln, z)','Border state','Temperature (z)','Terrain ruggedness (z)','Economic resources (ln IGR, z)']
rows=[]
for i,lbl in enumerate(pred):
    k=i+1
    rows.append([lbl,
        f"{nz(o['beta'][k],2)}{star(o['t'][k][1])} ({nz(o['se'][k],2)})",
        f"{nz(R['sar']['beta'][k],2)}{star(R['sar']['zp'][k][1])} ({nz(R['sar']['se'][k],2)})",
        f"{nz(R['sem']['beta'][k],2)}{star(R['sem']['zp'][k][1])} ({nz(R['sem']['se'][k],2)})"])
rows.append(["Spatial parameter (ρ / λ)","—",
    f"{nz(R['sar']['spatial'],2)} ({nz(R['sar']['spatial_p'],2) if R['sar']['spatial_p']>=.001 else '<.001'})",
    f"{nz(R['sem']['spatial'],2)} ({nz(R['sem']['spatial_p'],2)})"])
rows.append(["R² / Pseudo-R²",nz(o['r2'],2),nz(R['sar']['pr2'],2),nz(R['sem']['pr2'],2)])
rows.append(["AIC",f"{o['aic']:.1f}",f"{R['sar']['aic']:.1f}",f"{R['sem']['aic']:.1f}"])
apa_table(3,"OLS and Maximum-Likelihood Spatial Regression Models Predicting Log Conflict Intensity",
 ["Predictor","OLS b (SE)","SAR b (SE)","SEM b (SE)"],rows,
 note="N = 37. Row-standardised queen-contiguity weights. ρ = spatial autoregressive (lag) parameter; λ = spatial error parameter. †p < .10. *p < .05. **p < .01. ***p < .001.",
 colw=[2.5,1.4,1.4,1.4],fs=9)

H("Spatial Impact Decomposition",size=12,italic=True,bold=True,after=2)
body("Because the spatial lag parameter was small and non-significant, direct effects approximated total "
 "effects and spatial spillovers (indirect effects) were negligible in the cross-section (Table 4).")
apa_table(4,"Direct, Indirect, and Total Impacts From the Spatial Lag (SAR) Model",
 ["Predictor","Direct","Indirect","Total"],
 [[r[0],nz(r[1],3),nz(r[2],3),nz(r[3],3)] for r in R['impacts']],
 note="Impacts derived from the SAR model under queen-contiguity weights.",colw=[2.8,1.1,1.1,1.1],fs=10)

H("Robustness to Alternative Spatial Weights",size=12,italic=True,bold=True,after=2)
body("The substantive conclusions were invariant to the specification of the weights matrix (Table 5). "
 "Global clustering of the outcome remained significant under all three schemes, while the regression "
 "autoregressive parameters remained non-significant throughout.")
apa_table(5,"Robustness of Spatial Parameters Across Weight Matrices",
 ["Weights","SAR ρ","p","SEM λ","p","Moran's I","p"],
 [[r[0],nz(r[1],2),nz(r[2],2),nz(r[3],2),nz(r[4],2),nz(r[5],2),nz(r[6],3)] for r in R['robust']],
 note="Moran's I computed on the dependent variable under each weights scheme (999 permutations).",colw=[1.7,0.8,0.7,0.8,0.7,0.9,0.7],fs=10)

H("Spatial Diffusion: Dynamic Spatial Panel Model",size=12,italic=True,bold=True,after=2)
pn=R['panel']
if pn.get('ok'):
    body(f"The weak cross-sectional autoregression reflects two features: the spatially patterned "
     f"covariates absorb between-state clustering, and N = 37 underpowers maximum-likelihood estimation "
     f"of ρ. Exploiting the space–time structure resolves both. A fixed-effects dynamic spatial-lag "
     f"panel (N = {pn['N']} states × T = {pn['T']} years, 2012–2025) revealed strong and highly "
     f"significant spatial diffusion, ρ = {nz(pn['rho'],3)}, p {fp(pn['rho_p'])}, alongside substantial "
     f"temporal persistence, bₗₐ₉ = {nz(pn['beta_tlag'],3)}, p {fp(pn['beta_tlag_p'])} "
     f"(within-R² = {nz(pn['pr2'],3)}). That is, a state's conflict intensity in a given year rose "
     "with both its own prior-year violence and the contemporaneous violence of its neighbours, net of "
     "stable state characteristics. Armed conflict in Nigeria is thus better characterised as a "
     "self-reinforcing, spatially diffusing process than as a function of static structural conditions.")

H("Brief Discussion")
body("Three findings cohere. First, conflict intensity is spatially clustered (Moran's I significant "
 "across weight matrices). Second, static structural covariates explain this clustering weakly; only "
 "rurality (low population density) is a robust cross-sectional correlate, and border location and "
 "temperature are secondary. Third, and decisively, the dynamic spatial panel shows that the clustering "
 "is generated by temporal persistence and spatial diffusion rather than by fixed state attributes. "
 "Substantively, this supports a conflict-trap/contagion account of Nigerian insecurity over a purely "
 "grievance- or resource-based one, and methodologically it argues for space–time rather than "
 "cross-sectional designs in subnational conflict research.")

H("References")
refs=[
 "Anselin, L., & Rey, S. J. (2014). Modern spatial econometrics in practice: A guide to GeoDa, GeoDaSpace and PySAL. GeoDa Press.",
 "Armed Conflict Location & Event Data Project. (2026). ACLED conflict event data for Nigeria [Data set]. https://acleddata.com",
 "Fick, S. E., & Hijmans, R. J. (2017). WorldClim 2: New 1-km spatial resolution climate surfaces for global land areas. International Journal of Climatology, 37(12), 4302–4315.",
 "International Organization for Migration. (2025). Displacement Tracking Matrix: Nigeria [Data set]. Humanitarian Data Exchange. https://data.humdata.org",
 "National Bureau of Statistics. (2024). Internally generated revenue at state level, 2023. https://nigerianstat.gov.ng",
 "Office for the Coordination of Humanitarian Affairs. (2024). Nigeria subnational administrative boundaries [Data set]. Humanitarian Data Exchange.",
 "Oxford Poverty and Human Development Initiative. (2023). Nigeria Multidimensional Poverty Index [Data set]. https://ophi.org.uk",
]
for r in refs:
    p=doc.add_paragraph(); p.paragraph_format.left_indent=Inches(0.5); p.paragraph_format.first_line_indent=Inches(-0.5)
    p.add_run(r)

doc.save(OUT)
print("WROTE",OUT)
