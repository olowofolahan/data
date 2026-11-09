# Tracking the spatial flow/direction of conflict (2010–2025)

Two complementary methods recover *direction* from the state–year panel. Outputs:
`outputs/map8_conflict_flow.png`, `outputs/flow_edges.csv`.

## Method 1 — Mean-centre of violence (where the epicentre physically moved)
Each year, the fatality-weighted mean of state centroids gives the "centre of gravity" of violence;
connecting them traces its drift.

**Finding — the epicentre traces an arc, not a straight line.** From a central starting point (2010,
near the Plateau/FCT belt) it migrated **north-east to Borno by 2014–2015** (the Boko Haram peak),
then **reversed and migrated west/south-west into the North-West–North-Central banditry belt**, settling
near the **Niger/Kwara/Kaduna frontier by 2024–2025**. Net 2010→2025 displacement ≈ 208 km. The net
vector understates the story; the *path* is the finding — the engine of violence handed off from
North-East jihadism to North-West/North-Central banditry.

## Method 2 — Directed lead–lag diffusion network (which neighbour follows which)
For every pair of **adjacent** states A, B we fit B&#8339; = α + β&#8321;B&#8339;&#8331;&#8321; + β&#8322;A&#8339;&#8331;&#8321;,
i.e. does neighbour A's violence *last* year predict B's *this* year, **controlling for B's own
persistence**? A positive, significant β&#8322; is a directed diffusion edge A→B (a space-time
Granger-type test). 41 edges reached p < .10.

**Substantively meaningful (banditry corridor) edges:** **Kebbi → Niger** (β = 0.74, p = .02),
**Kaduna → Niger** (β = 0.77, p = .05), **Benue → Taraba / Benue → Kogi** — i.e. violence feeding
*into* Niger and the North-Central, consistent with the Niger→**Kwara** breakout the 2025 forecast
flagged. A second dense cluster of edges sits in the **South-West/South-East** (Ondo→Osun/Kogi/Ogun,
Rivers→Abia/Delta/Akwa Ibom), reflecting co-moving communal/separatist/cult violence rather than the
banditry spread.

## What this does and does not establish
- **Does:** describe the *observed geography of spread* — the epicentre's physical migration and
  statistically leading→following neighbour relationships. This operationalises the diffusion the
  dynamic spatial panel detected (ρ = 0.48).
- **Does not:** prove causal transmission. Lead–lag co-movement can arise from **common shocks**
  (a drought, a national policy) hitting neighbours together, or from **actor mobility** the data
  can't see. Southern edges on **low base counts are volatile** and some are likely spurious. With
  41 edges and no multiple-comparison correction, treat the network as **exploratory**; the
  high-base North-West/North-Central edges are the trustworthy ones.
- **Resolution:** annual, state-level — sub-state routes (e.g. forest corridors, highways) are
  invisible. ACLED event coordinates would allow a true point-level space–time diffusion model
  (e.g. space–time K-function, or an epidemic-type Hawkes model) — the rigorous next step.

Source: ACLED via HDX; boundaries OCHA/HDX; population NBS/NPC.
