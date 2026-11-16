# Methodology

Details behind the [README](../README.md): indicators, analytical framework, validation, limitations, data model and key decisions. Formulas and chart specs (in Spanish) are in [formulas.md](formulas.md).

## Indicators

Codes were checked against the API and the metadata extraction returned all 20 series without errors. `FE` = female, `MA` = male.

**Used in the analysis**

| Code | Indicator | Use |
|---|---|---|
| SL.TLF.CACT.FE.ZS / .MA.ZS | Labor force participation rate (% of population 15+) | Access |
| SL.UEM.TOTL.FE.ZS / .MA.ZS | Unemployment (% of labor force) | Access |
| SL.EMP.VULN.FE.ZS / .MA.ZS | Vulnerable employment (% of employment) | Quality |
| SL.AGR.EMPL.FE.ZS / .MA.ZS | Employment in agriculture (% of employment) | Sector segregation |
| SL.IND.EMPL.FE.ZS / .MA.ZS | Employment in industry (% of employment) | Sector segregation |
| SL.SRV.EMPL.FE.ZS / .MA.ZS | Employment in services (% of employment) | Sector segregation |

**Downloaded for validation and exploration**

| Code | Indicator | Use |
|---|---|---|
| SL.EMP.TOTL.SP.FE.ZS / .MA.ZS | Employment to population ratio, 15+ | Check of the calculated EPR |
| SL.EMP.WORK.FE.ZS / .MA.ZS | Wage and salaried workers | Consistency checks |
| SL.FAM.WORK.FE.ZS / .MA.ZS | Contributing family workers | Split of vulnerable employment (exploration) |
| SL.EMP.TOTL.SP.ZS | Employment to population ratio, total | Consistency checks |
| SL.UEM.TOTL.ZS | Unemployment, total | Consistency checks |

Indicators with a female/male pair were selected because the gap cannot be computed without both. Fertility, health, education and other gender indicators from the World Bank gender topic were left out because they do not answer the guiding question.

## Analytical framework

All rates are in %; in the formulas, unemployment `u` and vulnerable employment `v` are used as fractions. Gaps are computed year by year and averaged by period (1995–97 vs 2022–24). Full formulas, sentence templates and chart specs: [formulas.md](formulas.md).

**Sign convention:** every gap is positive when women are at a disadvantage (employment and non-vulnerable employment: men − women; vulnerable employment: women − men). The Duncan index has no sign.

**The funnel.** The access indicators are linked by an identity, and adding vulnerable employment extends it one step:

```
EPR = LFP × (1 − u)                       share of the population 15+ with a job
Q   = EPR × (1 − v) = LFP × (1 − u) × (1 − v)   share of the population 15+ with non-vulnerable employment
```

Both EPR and Q are calculated from LFP, u and v rather than taken from the published EPR.

**Metrics**

| Metric | Formula | Question |
|---|---|---|
| Employment gap | EPR_M − EPR_F | A1, K1 |
| Vulnerable employment gap | v_F − v_M | C1 |
| Duncan segregation index | ½ × Σ \|share_F − share_M\| over 3 sectors | C2 |
| Non-vulnerable employment gap | Q_M − Q_F | S1 |

**Decompositions (sequential, men as reference).** Starting from the men's values, one factor at a time is switched to the women's value; the drop at each step is attributed to that factor. The order follows the funnel (participation → unemployment → quality). The components add up exactly to the gap.

```
A2: EPR gap = (LFP_M − LFP_F)(1 − u_M)          participation
            + LFP_F (u_F − u_M)                 unemployment

S1: Q gap   = (EPR_M − EPR_F)(1 − v_M)          access
            + EPR_F (v_F − v_M)                 quality
```

A three-part version of S1 (participation, unemployment, quality) is also computed.

## Data validation

**1. Availability.** Participation, unemployment, employment-to-population, vulnerable employment and sector series have no missing values in the five countries for 1995–2025. Female share in managerial positions was tested and discarded as a core indicator: 30–72% missing depending on the country.

**2. Internal consistency (all passed, 0 failures).**

- Sector shares (agriculture + industry + services) sum to about 100% for both sexes.
- Contributing family workers never exceed vulnerable employment.
- Employers, derived as `100 - wage workers - vulnerable employment`, are never negative.
- Total employment-to-population and total unemployment fall between the female and male values.

**3. Cross-check with national sources (done).** Internal consistency does not prove the values match reality, since these are modeled estimates. Female and male unemployment and labor force participation were compared with the national statistics offices for 2010, 2019 and 2022 (`src/03_compare_national.py`). 2000 was dropped: national series by sex were missing or not comparable (Brazil, Colombia, Argentina, Uruguay) or available only for one quarter (Chile).

National values, sources and links are in `data/validation/national_values.csv`. Each row records the period (annual, average of 4 quarters, or single quarter), age base, coverage, a status and a note.

| Country | Source | Survey | Age base | Notes |
|---|---|---|---|---|
| Argentina | INDEC | EPH (31 urban agglomerates) | 14+ | 2019 and 2022 = average of 4 quarters; 2010 = Q4 only (no sex breakdown published for Q1-Q3) |
| Brazil | IBGE | PNAD Continua | 15+ (LFP), 14+ (unemployment) | No comparable survey in 2010 (PNADC starts 2012; no PNAD in census years) |
| Chile | INE | ENE | 15+ | 2010 and 2019 from the series before the 2020 re-benchmarking; 2022 from the current series |
| Colombia | DANE | GEIH | 12+ urban / 10+ rural before 2022; 15+ from 2022 | 2010 = average of 4 quarters; 2019 and 2022 annual |
| Uruguay | INE | ECH (series ECH0103) | 14+ | Methodology change in July 2021 |

Results (World Bank minus national, percentage points, 14 country-years):

| Measure | Mean abs. difference | Max abs. difference |
|---|---|---|
| Unemployment, female | 0.39 | 1.20 (COL 2010) |
| Unemployment, male | 0.20 | 0.48 |
| Participation, female | 1.19 | 3.35 (CHL 2019) |
| Participation, male | 1.82 | 6.12 (COL 2010) |
| **Participation gap (male − female)** | **0.87** | 3.56 (COL 2019) |
| **Unemployment gap (female − male)** | **0.25** | 1.08 (COL 2010) |

Findings:

- **Unemployment matches almost exactly** (Argentina 2019 and 2022 differ by 0.0), which suggests the ILO model uses the national survey values directly when they exist.
- **Participation is systematically higher in the World Bank data** (about +0.5 to +1.6 pp for both sexes in Argentina, Brazil, Chile and Uruguay). The most likely reasons are the age base (ILO uses 15+, INDEC and INE Uruguay use 14+) and urban-only coverage in Argentina. Because the bias affects both sexes, it largely cancels out in the gap.
- **Chile 2019** (+3.4 / +3.9 pp) reflects the 2020 ENE re-benchmarking: the World Bank value matches the re-benchmarked series (female participation about 52.5), not the originally published one (49.3). The gap differs by only 0.6 pp.
- **Colombia before 2022** is the only real outlier (participation gap off by about 3.5 pp). DANE counted the working-age population from age 12 (urban) and 10 (rural) until the 2022 redesign, when it moved to 15+; in 2022 the difference almost disappears. Why the effect is larger for men has not been verified.
- **Conclusion:** the World Bank series reproduce the national *gaps* with a mean error below 1 pp, while *levels* of participation differ because of definitions, coverage and series vintages. This supports analyzing gaps and within-country trends rather than country levels.

**4. Pipeline checks (`src/04_build_tables.py`, all passed).**

- No duplicated rows; all values between 0 and 100; 62 rows per country and indicator (31 years × 2 sexes).
- **Calculated EPR = published EPR** (mean and max difference 0.00 pp): the ILO derives EPR from participation and unemployment, so the decompositions close exactly.
- Funnel holds for every row: Q ≤ EPR ≤ LFP.
- Decomposition components add up to their gap (max residual 1.6e-14 pp, i.e. floating-point error).
- Every key in the fact tables exists in its dimension (no orphan rows in Power BI).

## Limitations

- **Modeled and imputed data.** The metadata states that the series include imputed observations that are not based on national data, carry high uncertainty and "should not be used for country comparisons or rankings". For this reason the analysis focuses on within-country gaps and trends, and country levels are not ranked.
- **Projection years: 2025.** According to the ILO methodological overview of the modelled estimates (January 2026, the edition used by the WDI download), labour force participation is *projected* for 2025–2027 from demographic factors, trends and GDP; unemployment for 2025 is an *estimate* from quarterly models for countries with quarterly data, and projected from 2026. Since EPR, Q and every gap depend on participation, **2025 is flagged as a projection** (`dim_year.is_projection`), shown as provisional in the dashboard and excluded from the period averages. 2024, the latest year with reported data, may be revised in the next edition. ([ILO, 2026](https://webapps.ilo.org/ilostat-files/Documents/TEM.pdf))
- **Women's employment is harder to measure.** The metadata notes that estimates of women in employment are not strictly comparable across countries, because social and cultural norms influence which activities are counted as economic.
- **Unemployment understates the access gap.** Women are more likely to be excluded from the unemployment count (discouragement, care responsibilities, barriers to job search), so unemployment is read together with participation and employment-to-population.
- **Vulnerable employment is a narrow measure of quality.** It is own-account workers plus contributing family workers, and in practice it mostly reflects own-account work. It does not capture informality among wage workers, pay or hours. **Paid domestic work**, a large share of female employment in the region, counts as wage employment (non-vulnerable) even when it is informal, so the measure probably overstates the quality of women's jobs. The finding "the gap is in access, not quality" holds for this measure only; it does not rule out a quality gap in informality or wages.
- **Selection.** Vulnerable employment is measured among the employed. As more women enter the labor market, the profile of employed women changes, which can move the indicator without any change in job quality.
- **Decomposition order.** The sequential decomposition depends on the order of the factors; the funnel order is used and stated. Results with other orders would differ slightly, not in total.
- **Probable series breaks in the ILO estimates.** Vulnerable employment jumps by about 6 pp for both sexes in Colombia in 2008 (consistent with DANE's change from ECH to GEIH) and moves sharply in Uruguay in 2006 (the ECH extended to the whole country, including rural areas). The *gap* barely changes in those years, so gap analysis is not affected, but level changes in those years are not interpreted.
- **Employment by sector** uses three broad ISIC groups, so the Duncan index understates segregation within sectors (e.g. domestic work and banking are both "services").
- **Breaks in national series.** Chile re-benchmarked the ENE in 2020, Uruguay changed the ECH methodology in July 2021 and Colombia changed the working-age definition in 2022. These affect the national comparison, not the World Bank series.
- **Colombia's participation gap before 2022** could not be validated against DANE because of the different age definition.

## Data model (Power BI)

Star schema built by `src/04_build_tables.py` in `data/processed/` (CSV, UTF-8). Each fact table has a single grain.

| Table | One row is… | Columns | Used by |
|---|---|---|---|
| `fact_indicator` | one indicator, one sex, one country, one year | country_code, year, indicator_key, sex, value | A1, C1, C2, K1 |
| `fact_gap` | one gap, one country, one year | country_code, year, metric, value, unit | C2, K1, titles |
| `fact_decomposition` | one component of a gap, one country, one year | country_code, year, decomposition, component, value_pp, share_pct | A2, S1 |
| `dim_country` | a country | country_code, names (es, en) | all |
| `dim_year` | a year | year, period, comparison_period, crisis, window, is_projection | all |
| `dim_indicator` | an indicator | key, name, block, base, WDI codes, source | fact_indicator |
| `dim_metric` | a gap metric | metric, name, unit, sign convention | fact_gap |
| `dim_component` | a decomposition component | component, name, sort order (stacking order) | fact_decomposition |

Period averages and crisis windows are computed as DAX measures from `dim_year`.

## Key decisions

- Hybrid approach (Python for ETL and metrics, Power BI for visualization) over Power BI alone or manual CSV downloads.
- Five countries instead of the 12 in South America.
- Within-country gaps and trends instead of cross-country rankings, because of the modeled nature of the data.
- Female/male pairs only: no pair, no gap.
- Raw API snapshot saved to `data/raw` so the project is reproducible.
- National cross-check uses 2010, 2019 and 2022; 2000 was dropped for lack of comparable national data by sex.
- Every national value keeps its source link, period and status, so each comparison can be audited.
- Period comparison uses 3-year averages (1995–97 vs 2022–24) instead of single years; 2025 is excluded because it is an ILO projection.
- Gaps and decompositions are in percentage points with one sign convention (positive = women at a disadvantage), because only pp components add up to the gap. For communication, the dashboard also shows parity (women / men ratio) and levels as "out of every 100", calculated as DAX measures.
- Python computes what defines the data or must be validated (gaps, decompositions, dimensions); Power BI computes what depends on the chart context (period averages, ratios). No metric is calculated in both places.
- EPR and Q are calculated from their components so that the decompositions close exactly.
- Quality is measured by vulnerable employment only; sector segregation is context, not part of the access vs. quality comparison, because a different sector is not necessarily a worse job.
- S1 is presented in percentage points rather than shares, because quality is negative in most years and shares above 100% are hard to read.
- The 2001–02 crises in Argentina and Uruguay are reported as a finding; the crisis windows stay at 2008 and the pandemic for all countries.
