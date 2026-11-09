import json, numpy as np, pandas as pd
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
SC='/tmp/claude-0/-home-user-data/9733eecb-671a-58d6-bbe9-c7d4a40590cd/scratchpad'
R=json.load(open(f'{SC}/final_results.json'))
ED=pd.read_csv('/home/user/data/geography_of_armed_conflict/outputs/flow_edges.csv')
OUT='/home/user/data/geography_of_armed_conflict/Prediction_and_Diffusion_Method_Results_APA7.docx'
doc=Document(); s=doc.styles['Normal']; s.font.name='Times New Roman'; s.font.size=Pt(12)
s.paragraph_format.line_spacing_rule=WD_LINE_SPACING.DOUBLE; s.paragraph_format.space_after=Pt(0)
NAVY=RGBColor(0x1F,0x2A,0x44)
def fp(p):
    p=float(p); return "< .001" if p<.001 else "= "+("%.3f"%p).lstrip("0") if p<1 else "= %.2f"%p
def nz(x,d=2):
    t=f"%.{d}f"%float(x); return t.replace("0.",".",1) if (t[:2]=="0." or t[:3]=="-0.") else t
def H(t,size=12,bold=True,italic=False,align='left',before=8,after=4):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(before); p.paragraph_format.space_after=Pt(after)
    p.alignment={'left':WD_ALIGN_PARAGRAPH.LEFT,'center':WD_ALIGN_PARAGRAPH.CENTER}[align]
    r=p.add_run(t); r.bold=bold; r.italic=italic; r.font.size=Pt(size)
    if bold: r.font.color.rgb=NAVY
    return p
def body(t):
    p=doc.add_paragraph(); p.paragraph_format.first_line_indent=Inches(0.5); p.add_run(t); return p
def setc(c,t,italic=False,align='left',size=10.5):
    c.text=''; pr=c.paragraphs[0]; pr.alignment={'left':WD_ALIGN_PARAGRAPH.LEFT,'center':WD_ALIGN_PARAGRAPH.CENTER}[align]
    pr.paragraph_format.line_spacing_rule=WD_LINE_SPACING.SINGLE; pr.paragraph_format.space_after=Pt(1); pr.paragraph_format.space_before=Pt(1)
    r=pr.add_run(t); r.italic=italic; r.font.size=Pt(size); r.font.name='Times New Roman'
def bdr(cell,edges):
    tcPr=cell._tc.get_or_add_tcPr(); tb=OxmlElement('w:tcBorders')
    for e in ['top','bottom']:
        el=OxmlElement('w:'+e)
        if e in edges: el.set(qn('w:val'),'single'); el.set(qn('w:sz'),'6'); el.set(qn('w:color'),'000000')
        else: el.set(qn('w:val'),'nil')
        tb.append(el)
    tcPr.append(tb)
def figure(num,title,path,note=None,width=6.0):
    from PIL import Image as PImage
    H(f"Figure {num}",before=8,after=0); H(title,bold=False,italic=True,after=4)
    iw,ih=PImage.open(path).size
    doc.add_picture(path,width=Inches(width))
    doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
    if note:
        p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(2)
        a=p.add_run("Note. "); a.italic=True; a.font.size=Pt(10); a.font.name='Times New Roman'
        b=p.add_run(note); b.font.size=Pt(10); b.font.name='Times New Roman'
    doc.add_paragraph()
def table(num,title,headers,rows,note=None,colw=None,fs=10.5):
    H(f"Table {num}",before=8,after=0); H(title,bold=False,italic=True,after=4)
    t=doc.add_table(rows=1+len(rows),cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.LEFT
    for j,h in enumerate(headers): setc(t.rows[0].cells[j],h,italic=True,align='center' if j else 'left',size=fs)
    for i,row in enumerate(rows,1):
        for j,v in enumerate(row): setc(t.rows[i].cells[j],str(v),align='center' if j else 'left',size=fs)
    for j in range(len(headers)): bdr(t.rows[0].cells[j],['top','bottom']); bdr(t.rows[-1].cells[j],['bottom'])
    if colw:
        for j,w in enumerate(colw):
            for rr in t.rows: rr.cells[j].width=Inches(w)
    if note:
        p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(2)
        a=p.add_run("Note. "); a.italic=True; a.font.size=Pt(10); a.font.name='Times New Roman'
        b=p.add_run(note); b.font.size=Pt(10); b.font.name='Times New Roman'
    doc.add_paragraph()

pr=R['pred']; pn=R['panel']; fl=R['flow']
# ===== TITLE =====
H("Method and Results",size=15,align='center',before=0,after=4)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("Out-of-Sample Prediction, Forecast Mismatch, and Spatial Diffusion of Armed Conflict Across Nigerian States"); r.italic=True

# ================= METHOD =================
H("Method",size=13)
H("Predicting the Most Recent Year and Quantifying Forecast Mismatch",italic=True)
body("To assess how far current conflict can be anticipated from prior information, and where it departs "
 "from expectation, we predicted each state's 2025 political-violence fatalities (log-transformed; N = 37 "
 "states) using only pre-2025 predictors. Four nested linear models were compared: (M1) a persistence "
 "model using the prior year's (2024) fatalities; (M2) adding a spatial spillover term, the row-standardised "
 "queen-contiguity spatial lag of neighbours' 2024 fatalities; (M3) replacing the single lag with a "
 "three-year (2022–2024) violence history plus the spillover term; and (M4) adding static structural "
 "covariates (multidimensional poverty, population, and a northern-region indicator). Predictive skill was "
 "evaluated by exact leave-one-out cross-validation (LOOCV) using the PRESS statistic, which yields "
 "genuine out-of-sample R² rather than in-sample fit. The forecast mismatch for each state was defined "
 "as its standardised residual from the full model (observed minus predicted log fatalities): positive "
 "residuals denote states with more 2025 violence than their trajectory and neighbourhood implied "
 "(emergent hotspots), and negative residuals denote states that de-escalated below expectation. "
 "Residuals on very low base counts were interpreted as noise.")
H("Characterising the Direction of Diffusion",italic=True)
body("Two methods described the spatial flow of conflict over 2010–2025. First, the fatality-weighted "
 "mean centre of violence—the fatality-weighted average of state centroids—was computed for each "
 "year and connected to trace the movement of the conflict's centre of gravity, summarised by the net "
 "displacement and bearing between the first and last years. Second, a directed neighbour lead–lag "
 "network was estimated: for every pair of contiguous states A and B, we regressed B's log fatalities in "
 "year t on B's own value in year t − 1 and A's value in year t − 1 (a space–time Granger-type "
 "test), retaining A → B as a directed diffusion edge where the coefficient on A's lag was positive and "
 "significant at p < .10 net of B's own persistence. Because this involves many pairwise tests on annual "
 "data, the network is interpreted as exploratory. Analyses used Python 3.13.")

# ================= RESULTS =================
H("Results",size=13)
H("Out-of-Sample Prediction of 2025 Conflict",italic=True)
body(f"Conflict in 2025 was substantially predictable from pre-2025 information. The prior year's "
 f"fatalities alone correlated r = {nz(pr['r_persist'],2)} with 2025 fatalities and explained a majority "
 f"of out-of-sample variance (Table 1). Predictive skill increased as spatial spillover and a longer "
 f"violence history were added, peaking for the model combining three-year history with neighbours' prior "
 f"violence, LOOCV R² = {nz(pr['models'][2][2],3)}. Adding static structural covariates did not improve "
 f"out-of-sample performance (LOOCV R² = {nz(pr['models'][3][2],3)}), indicating that predictability "
 "derived from the dynamics of conflict—its persistence and spatial diffusion—rather than from "
 "stable structural conditions.")
table(1,"Out-of-Sample Predictive Performance for 2025 Conflict (Leave-One-Out Cross-Validation)",
 ["Model","In-sample R²","LOOCV R²"],
 [[m[0],nz(m[1],3),nz(m[2],3)] for m in pr['models']],
 note="N = 37 states. Outcome = log(1 + 2025 fatalities). LOOCV computed via the PRESS statistic; negative values indicate no out-of-sample skill.",
 colw=[3.4,1.3,1.3],fs=10)

H("Forecast Mismatch: Emergent Hotspots and De-escalations",italic=True)
pos=pr['pos']; neg=pr['neg']
body(f"The forecast residuals isolated states whose 2025 outcomes broke from trajectory (Table 2). The "
 f"largest positive residual was Kwara, which recorded {pos[0][2]} fatalities against a predicted "
 f"≈ {pos[0][3]} (residual = {nz(pos[0][4])}), a previously quiet North-Central state in which "
 f"banditry broke out—an emergent hotspot invisible to its own history. Sokoto and Zamfara similarly "
 f"escalated beyond expectation. Conversely, the largest negative residual was Kaduna, a major theatre "
 f"that fell to {neg[0][2]} fatalities against a predicted ≈ {neg[0][3]} (residual = {nz(neg[0][4])}), "
 "marking a sharp de-escalation. Substantively, positive residuals flag where the conflict system "
 "advanced into new territory faster than contagion alone predicts, whereas negative residuals flag "
 "interruptions of persistence (e.g., operations, displacement, or local accommodation); both locate the "
 "discrete shocks that structural and historical data cannot encode. Residuals on small base counts "
 "(e.g., Ekiti) were treated as statistical noise.")
rows=[["Under-predicted (emergent hotspots)","","","",""]]+[[r[0],r[1],r[2],r[3],nz(r[4])] for r in pos[:3]]+\
     [["Over-predicted (de-escalating)","","","",""]]+[[r[0],r[1],r[2],r[3],nz(r[4])] for r in neg[:3]]
table(2,"States With the Largest Forecast Residuals for 2025",
 ["State / group","2024","2025","Predicted","Residual (log)"],rows,
 note="Residuals from the full model (three-year history + spatial spillover + structural covariates). Predicted values rounded.",
 colw=[2.7,0.8,0.8,1.0,1.2],fs=10)

H("Direction of Spatial Diffusion",italic=True)
kb=[e for e in fl['key'] if e[0]=='Kebbi'][0]; kd=[e for e in fl['key'] if e[0]=='Kaduna'][0]
body(f"The fatality-weighted mean centre of violence migrated approximately {fl['drift_km']} km over "
 "2010–2025, tracing an arc rather than a straight path: it moved north-east toward the North-East "
 "theatre during the 2014–2015 Boko Haram peak, then reversed and migrated west and south-west into "
 "the North-West–North-Central banditry belt, settling near the Niger–Kwara–Kaduna frontier by "
 f"2024–2025. The directed lead–lag network returned {fl['n_edges']} diffusion edges at p < .10. "
 "The substantively meaningful edges fed into the North-Central corridor—Kebbi → Niger "
 f"(b = {nz(kb[2])}, p {fp(kb[3])}) and Kaduna → Niger (b = {nz(kd[2])}, p {fp(kd[3])})—consistent "
 "with the Kwara breakout identified in the forecast residuals; a separate cluster of edges in the "
 "South-West and South-East reflected co-moving communal and separatist violence (Table 3). These "
 "directional findings are exploratory: lead–lag co-movement may reflect common shocks or unobserved "
 "armed-actor mobility; edges on low base counts are volatile; and the annual, state-level resolution "
 "cannot capture sub-state routes. Event-level (point-coordinate) data would permit a confirmatory "
 "space–time point-process model.")
figure(1,"Spatial Flow of Armed Conflict in Nigeria, 2010–2025",
 '/home/user/data/geography_of_armed_conflict/outputs/map8_conflict_flow.png',
 note="The navy path traces the fatality-weighted mean centre of violence by year (open circle = 2010; star = 2025). Red arrows are directed year-on-year diffusion edges between neighbouring states (p < .10); arrow width is proportional to the lead–lag coefficient. Directional results are exploratory.",
 width=6.1)
top=ED.sort_values('coef',ascending=False).head(8)
table(3,"Strongest Directed Diffusion Edges Between Neighbouring States",
 ["From → To","b","p"],
 [[f"{r['from']} → {r['to']}",nz(r['coef']),nz(r['p'],3)] for _,r in top.iterrows()],
 note="Edge A → B: coefficient on A's prior-year log fatalities predicting B's current log fatalities, controlling for B's own lag. Exploratory; see text.",
 colw=[2.6,1.0,1.0],fs=10)

H("Summary",italic=True)
body(f"Armed conflict in 2025 was largely predictable from prior violence and neighbouring violence "
 f"(LOOCV R² = {nz(pr['models'][2][2],3)}), with static structure adding nothing out-of-sample. The "
 "forecast mismatch nonetheless pinpointed genuine regime changes—Kwara's emergence and Kaduna's "
 "de-escalation—that lie in the residuals. Directionally, the violence centre has shifted from the "
 "North-East to the North-West–North-Central, and diffusion into the North-Central corridor "
 "foreshadowed the new hotspot. Together these results support a conflict-trap and contagion account of "
 "Nigerian insecurity.")
doc.save(OUT); print("WROTE",OUT)
