# Discussion

*Note.* Bracketed markers such as [ref] indicate where domain citations should
be inserted; they are placeholders, not claims. Reporting follows APA 7th
edition.

## Principal findings

In this ecological spatial disease-mapping study of Nigeria's 37 first-order
administrative units, confirmed Lassa fever burden over 2020–2026 was highly
concentrated—five states accounted for 86% of confirmed cases—and
significantly spatially clustered (global Moran's *I* = .25, *p* = .007), with
a coherent high–high belt spanning Edo, Taraba, Benue, Plateau, Nasarawa, and
Delta. State incidence was structured by a strong north–south gradient and an
urban–rural gradient: incidence fell steeply toward the arid, highly seasonal
north and was lower in more densely populated states. Critically, latitude,
climate (rainfall and its seasonality, temperature seasonality), and
multidimensional poverty were almost perfectly collinear—a single principal
component captured 91% of their joint variance—so these cannot be identified as
separate determinants at the state scale; only population density was
statistically separable from the gradient. A formal Bayesian spatial
disease-mapping model (Besag–York–Mollié) was estimable and localized a
residual high-risk belt after adjustment for climate and density, but the
spatial fraction was modest and imprecisely estimated (*φ* = 0.22, 95% CrI
[0.00, 0.85]) and did not improve out-of-sample prediction over a non-spatial
model. Finally, detected case counts were dominated by surveillance effort:
confirmed cases scaled almost one-to-one with suspected-case volume (*R²* =
.94), and proximity to a diagnostic laboratory independently predicted detected
burden.

## Interpretation

The geographic pattern is consistent with the established ecology of Lassa
fever. The endemic belt identified here coincides with the forest–savanna
mosaic of southern and central Nigeria, the zone of greatest abundance of the
primary reservoir *Mastomys natalensis* and the location of the long-recognised
treatment and research centres at Irrua (Edo) and Owo (Ondo) [ref]. The sharp
decline in incidence toward the arid north mirrors the rainfall and vegetation
gradient that governs reservoir habitat and breeding, and is compatible with
the pronounced dry-season peak of human transmission [ref]. The inverse
association with population density is consistent with Lassa fever as a
primarily rural, peridomestic zoonosis in which exposure occurs through
rodent intrusion into dwellings and food stores rather than through
person-to-person spread in dense urban settings [ref].

A central interpretive point is that the apparent "determinants" of state-level
incidence—climate, poverty, and latitude—are empirically one axis rather than
competing causes. This collinearity resolves the otherwise paradoxical
descriptive pattern in which the highest-burden states (Ondo, Edo) are among
the least poor: once the north–south gradient is accounted for, poverty carries
no risk signal independent of it, and its coefficient is unstable across
specifications. Disentangling the mechanistic contributions of climate,
reservoir ecology, housing, and deprivation therefore requires either finer
spatial resolution, where these variables decouple, or designs that exploit
within-gradient variation.

Equally important, the analysis shows that detected Lassa fever burden is in
large part a measurement of surveillance intensity. States with diagnostic
laboratories and higher suspected-case throughput report more confirmed cases,
and once suspected-case volume is included no ecological covariate remains
significant. This is not evidence that ecology is unimportant; it is evidence
that, at the state scale, true risk and detection capacity are confounded. The
finding underscores the need to interpret NCDC confirmed-case maps as joint
products of transmission and testing access, and it argues for expanding
diagnostic capacity in under-tested states before spatial inequalities in
reported burden can be read as inequalities in risk [ref].

## Methodological contribution

Methodologically, the study illustrates a complete spatial-epidemiological
workflow and its honest limits. Moving from global and local autocorrelation
statistics through spatial-econometric diagnostics to a Bayesian hierarchical
disease-mapping model showed that the spatial clustering evident in the raw
data was almost entirely explained by spatially patterned covariates: residual
autocorrelation was negligible, and the structured random effect, though it
recovered the endemic belt visually, could not be distinguished from an
unstructured effect with 37 areas. Reporting this null spatial result
transparently—rather than over-interpreting a smoothed risk map—is itself a
contribution, and the dimensionality analysis (variance inflation factors and
principal components) provides a template for handling the strong gradient
collinearity that characterises many national ecological analyses.

## Strengths and limitations

Strengths include national coverage across seven transmission seasons, the use
of an incidence model with a population offset and estimated overdispersion,
explicit adjustment for the surveillance confound, formal quantification of
covariate collinearity, and a fully Bayesian spatial model with transparent
uncertainty. Several limitations temper the conclusions.

First, the design is ecological: associations hold at the state level and must
not be read as individual-level effects (the ecological fallacy). Second, and
most consequentially, the spatial unit is coarse. With only 37 areas the
spatial random effect is weakly identified, the modifiable areal unit problem
applies, and the collinear gradient cannot be decomposed; local-government-area
data (*n* = 774) would markedly increase power and allow climate, poverty, and
reservoir ecology to separate. Third, the surveillance data were compiled from
NCDC situation-report tables by automated extraction and, although internally
consistency-checked, have not been validated against primary line lists; blank
cells were treated as zero, which may understate low-reporting states. Fourth,
the outcome was cumulative and cross-sectional, ignoring the pronounced
seasonal and interannual dynamics of Lassa fever; a spatio-temporal extension
is a clear next step. Fifth, reservoir presence was indexed by GBIF occurrence
records, which reflect sampling effort rather than true abundance (the
highest-incidence state had no records) and are an inadequate substitute for a
modelled reservoir-suitability surface. Sixth, climate was represented by
long-term normals rather than period-specific anomalies. Finally, residual and
unmeasured confounding—housing quality, food-storage practices, agricultural
exposure, and health-seeking behaviour—cannot be excluded.

## Implications and future directions

The results have two practical implications. For surveillance, the strong
dependence of detected burden on testing access argues for equitable expansion
of diagnostic capacity so that risk maps reflect transmission rather than
detection. For research, the collapse of climate, poverty, and latitude onto a
single state-level axis makes a clear case for finer-resolution, spatio-temporal
Bayesian models (for example, a local-government-area BYM model with a temporal
component) that incorporate a modelled *Mastomys* suitability surface and a
direct measure of testing capacity. Such models would move the field from
describing where cases are detected toward estimating where spillover risk is
greatest.

## Conclusion

Lassa fever in Nigeria is spatially clustered along a southern–central belt,
but at the state scale its burden is shaped by a single collinear
climate–socioeconomic gradient, by population density, and—substantially—by the
geography of surveillance itself. A formal Bayesian spatial disease-mapping
model is estimable and useful for hypothesis generation, yet a decisive
residual spatial signal is not identifiable at this resolution. Finer,
local-government-area and time-resolved data are needed to separate true
spillover risk from detection and to translate spatial description into
actionable targeting.
