"""Build the Power BI star schema: indicators, gaps and decompositions.

Input:  data/raw/wdi_raw.csv
Output: data/processed/fact_*.csv and dim_*.csv  (gaps > 0 = women at a disadvantage)
"""
from pathlib import Path

import numpy as np
import pandas as pd

from config import INDICATORS  # {WDI code: column name in wdi_raw.csv}

RAW = Path("data/raw/wdi_raw.csv")
OUT = Path("data/processed")
FIRST_YEAR, LAST_YEAR = 1995, 2025

# WDI series (without the sex and unit parts) -> indicator_key used in the model.
# Series not listed here (totals, wage workers, family workers) stay out of the
# dashboard; they were only used for validation.
SERIES_KEYS = {
    "SL.TLF.CACT": "lfp",
    "SL.UEM.TOTL": "unemployment",
    "SL.EMP.TOTL.SP": "epr_wdi",  # published EPR, only used to check our EPR
    "SL.EMP.VULN": "vulnerable",
    "SL.AGR.EMPL": "agriculture",
    "SL.IND.EMPL": "industry",
    "SL.SRV.EMPL": "services",
}
SEX = {"FE": "female", "MA": "male"}
KEYS = ["country_code", "year", "indicator_key", "sex"]
ID = ["country_code", "year"]
SECTORS = ["agriculture", "industry", "services"]
MIN_GAP_FOR_SHARE = 0.5  # pp; below this a share of the gap is not meaningful

# Years from which ILO values are projections. Source: ILO, "ILO modelled estimates:
# Methodological overview", January 2026 (edition used by WDI, accessed Jan 2026):
# labour force participation is projected for 2025-2027 from demographic factors,
# so 2025 is a projection for LFP and everything derived from it (EPR, Q, gaps).
# https://webapps.ilo.org/ilostat-files/Documents/TEM.pdf
FIRST_PROJECTION_YEAR = 2025

PERIODS = [  # (name, first year, last year) - used for trends (A1, C1, C2)
    ("pre_2008", 1995, 2007),
    ("crisis_2008", 2008, 2009),
    ("between", 2010, 2019),
    ("covid", 2020, 2021),
    ("post_covid", 2022, 2025),
]
COMPARISON = {"start": (1995, 1997), "end": (2022, 2024)}  # period averages in the sentences
CRISIS_WINDOWS = {  # K1: crisis -> window -> (first year, last year)
    "2008": {"before": (2005, 2007), "during": (2008, 2009), "after": (2010, 2012)},
    "covid": {"before": (2017, 2019), "during": (2020, 2021), "after": (2022, 2024)},
}


def parse_code(code):
    """'SL.TLF.CACT.FE.ZS' -> ('lfp', 'female'); None if not used in the model."""
    parts = code.split(".")
    if len(parts) < 4 or parts[-2] not in SEX:
        return None  # totals such as SL.UEM.TOTL.ZS have no sex part
    key = SERIES_KEYS.get(".".join(parts[:-2]))
    return (key, SEX[parts[-2]]) if key else None


# ---------------------------------------------------------------- step 1
def load_raw():
    df = pd.read_csv(RAW).rename(columns={"economy": "country_code", "time": "year"})
    df["year"] = df["year"].astype(int)
    df = df[df["year"].between(FIRST_YEAR, LAST_YEAR)]
    print(f"Step 1: {len(df)} country-years, {df['year'].min()}-{df['year'].max()}")
    return df


# ------------------------------------------------------------ steps 2-3
def to_long(df):
    # column name in the raw file -> (indicator_key, sex)
    colmap = {}
    for code, column in INDICATORS.items():
        parsed = parse_code(code)
        if parsed is None:
            continue
        if column not in df.columns:
            print(f"  Warning: {code} ({column}) is in config but not in the raw file")
            continue
        colmap[column] = parsed

    long = df.melt(
        id_vars=["country_code", "year"],
        value_vars=list(colmap),
        var_name="column",
        value_name="value",
    )
    long["indicator_key"] = long["column"].map(lambda c: colmap[c][0])
    long["sex"] = long["column"].map(lambda c: colmap[c][1])
    long = long[KEYS + ["value"]]
    print(f"Steps 2-3: {len(long)} rows, indicators: {sorted(long['indicator_key'].unique())}")
    return long


# ---------------------------------------------------------------- step 4
def add_epr_q(long):
    # One row per country, year and sex; one column per indicator.
    # pivot (not pivot_table) raises an error if there are duplicates.
    wide = long.pivot(index=["country_code", "year", "sex"], columns="indicator_key", values="value")

    u = wide["unemployment"] / 100
    v = wide["vulnerable"] / 100
    wide["epr"] = wide["lfp"] * (1 - u)   # EPR = LFP x (1 - u)
    wide["q"] = wide["epr"] * (1 - v)     # Q   = EPR x (1 - v)

    # Population funnel (% of population 15+): the four parts add up to 100
    wide["out_of_labor"] = 100 - wide["lfp"]   # not working and not looking
    wide["unemployed"] = wide["lfp"] * u       # looking, without a job
    wide["vulnerable_emp"] = wide["epr"] * v   # employed in vulnerable jobs
    # + q: employed in non-vulnerable jobs

    # Check: our EPR vs the EPR published by the World Bank (modeled separately).
    if "epr_wdi" in wide:
        diff = (wide["epr"] - wide["epr_wdi"]).abs()
        print(f"Step 4: EPR calculated vs published, mean abs diff {diff.mean():.2f} pp, "
              f"max {diff.max():.2f} pp")
        wide = wide.drop(columns="epr_wdi")

    result = (
        wide.reset_index()
        .melt(id_vars=["country_code", "year", "sex"], var_name="indicator_key", value_name="value")
        .dropna(subset=["value"])
    )
    return result[KEYS + ["value"]].sort_values(KEYS).reset_index(drop=True)


# ------------------------------------------------- helpers for steps 5-6
def by_sex(fact):
    """One row per country and year; columns (indicator_key, sex)."""
    w = fact.pivot(index=ID, columns=["indicator_key", "sex"], values="value")
    return (lambda k: w[(k, "female")]), (lambda k: w[(k, "male")])


# ---------------------------------------------------------------- step 5
def build_gaps(fact):
    F, M = by_sex(fact)
    gaps = pd.DataFrame({
        # Convention: positive = women at a disadvantage
        "epr_gap": M("epr") - F("epr"),
        "q_gap": M("q") - F("q"),
        "vulnerable_gap": F("vulnerable") - M("vulnerable"),
        # Duncan index: % of employed women who would have to change sector
        # to match the men's distribution. No sign: it measures difference.
        "duncan_index": 0.5 * sum((F(s) - M(s)).abs() for s in SECTORS),
    })
    out = (
        gaps.reset_index()
        .melt(id_vars=ID, var_name="metric", value_name="value")
        .dropna(subset=["value"])
    )
    out["unit"] = np.where(out["metric"] == "duncan_index", "%", "pp")
    print(f"Step 5: {len(out)} gap rows, metrics: {sorted(out['metric'].unique())}")
    return out.sort_values(ID + ["metric"]).reset_index(drop=True)


# ---------------------------------------------------------------- step 6
def build_decompositions(fact):
    """Sequential ('staircase') decomposition, men as reference.
    Order follows the funnel: participation -> unemployment -> quality."""
    F, M = by_sex(fact)
    lfp_f, lfp_m = F("lfp"), M("lfp")
    u_f, u_m = F("unemployment") / 100, M("unemployment") / 100
    v_f, v_m = F("vulnerable") / 100, M("vulnerable") / 100
    epr_f, epr_m = F("epr"), M("epr")

    parts = {
        # A2: EPR gap = participation + unemployment
        "epr_2parts": {
            "participation": (lfp_m - lfp_f) * (1 - u_m),
            "unemployment": lfp_f * (u_f - u_m),
        },
        # S1: Q gap = access + quality
        "q_2parts": {
            "access": (epr_m - epr_f) * (1 - v_m),
            "quality": epr_f * (v_f - v_m),
        },
        # S1 (detail): Q gap = participation + unemployment + quality
        "q_3parts": {
            "participation": (lfp_m - lfp_f) * (1 - u_m) * (1 - v_m),
            "unemployment": lfp_f * (u_f - u_m) * (1 - v_m),
            "quality": lfp_f * (1 - u_f) * (v_f - v_m),
        },
    }
    frames = []
    for decomposition, components in parts.items():
        for component, values in components.items():
            frames.append(pd.DataFrame({
                "decomposition": decomposition,
                "component": component,
                "value_pp": values,
            }).reset_index())
    out = pd.concat(frames, ignore_index=True).dropna(subset=["value_pp"])

    # share_pct: % of the gap explained by each component (components sum to 100)
    total = out.groupby(ID + ["decomposition"])["value_pp"].transform("sum")
    out["share_pct"] = np.where(total.abs() >= MIN_GAP_FOR_SHARE, out["value_pp"] / total * 100, np.nan)
    print(f"Step 6: {len(out)} component rows, decompositions: {sorted(out['decomposition'].unique())}")
    return out[ID + ["decomposition", "component", "value_pp", "share_pct"]].sort_values(
        ID + ["decomposition", "component"]).reset_index(drop=True)


def check_decompositions(decomp, gaps):
    """The components must add up exactly to the gap they decompose."""
    target = {"epr_2parts": "epr_gap", "q_2parts": "q_gap", "q_3parts": "q_gap"}
    sums = decomp.groupby(ID + ["decomposition"])["value_pp"].sum().reset_index()
    sums["metric"] = sums["decomposition"].map(target)
    merged = sums.merge(gaps, on=ID + ["metric"])
    residual = (merged["value_pp"] - merged["value"]).abs()
    print(f"\nDecomposition check: max |components - gap| = {residual.max():.2e} pp")
    negative = decomp[(decomp["component"] == "quality") & (decomp["value_pp"] < 0)]
    if len(negative):
        print(f"  Note: quality is negative in {len(negative)} rows "
              f"(employed women less vulnerable than men): valid, but changes the wording")
    return residual.max() < 1e-6


def preview(gaps, decomp):
    """Quick look at the numbers behind A1 and S1 (start vs end period)."""
    period = {**{y: "1995-97" for y in range(1995, 1998)}, **{y: "2022-24" for y in range(2022, 2025)}}
    g = gaps[gaps["metric"] == "epr_gap"].assign(period=lambda d: d["year"].map(period)).dropna(subset=["period"])
    d = decomp[(decomp["decomposition"] == "q_2parts") & (decomp["component"] == "access")]
    d = d.assign(period=lambda x: x["year"].map(period)).dropna(subset=["period"])
    table = pd.concat({
        "epr_gap_pp": g.pivot_table(index="country_code", columns="period", values="value"),
        "access_share_pct": d.pivot_table(index="country_code", columns="period", values="share_pct"),
    }, axis=1).round(1)
    print("\nPreview (period averages):")
    print(table.to_string())


# ---------------------------------------------------------------- step 7
def build_dimensions():
    dim_country = pd.DataFrame([
        ("ARG", "Argentina", "Argentina"),
        ("BRA", "Brasil", "Brazil"),
        ("CHL", "Chile", "Chile"),
        ("COL", "Colombia", "Colombia"),
        ("URY", "Uruguay", "Uruguay"),
    ], columns=["country_code", "country_name_es", "country_name_en"])

    rows = []
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        row = {"year": year,
               "period": next(p for p, a, b in PERIODS if a <= year <= b),
               "comparison_period": next((k for k, (a, b) in COMPARISON.items() if a <= year <= b), None),
               "crisis": None, "window": None,
               "is_projection": year >= FIRST_PROJECTION_YEAR}
        for crisis, windows in CRISIS_WINDOWS.items():  # windows do not overlap
            for window, (a, b) in windows.items():
                if a <= year <= b:
                    row["crisis"], row["window"] = crisis, window
        rows.append(row)
    dim_year = pd.DataFrame(rows)
    # Readable label for the comparison periods (axis of the C2 chart)
    dim_year["comparison_label"] = dim_year["comparison_period"].map(
        {k: f"{a}–{str(b)[-2:]}" for k, (a, b) in COMPARISON.items()})
    # Spanish label and order for the crisis windows (K1 bar charts)
    dim_year["window_es"] = dim_year["window"].map({"before": "Antes", "during": "Durante", "after": "Después"})
    dim_year["window_order"] = dim_year["window"].map({"before": 1, "during": 2, "after": 3}).astype("Int64")

    dim_sex = pd.DataFrame([
        ("female", "Mujeres", 1),
        ("male", "Hombres", 2),
    ], columns=["sex", "name_es", "sort_order"])

    dim_indicator = pd.DataFrame([
        # key, name_es (unique), block, base, wdi female, wdi male, source, sort_order
        # Funnel parts (block "embudo") are sorted bottom -> top of the stacked bar.
        ("q", "Empleo no vulnerable", "embudo", "población 15+", None, None, "calculado: EPR × (1 − v)", 1),
        ("vulnerable_emp", "Empleo vulnerable", "embudo", "población 15+", None, None, "calculado: EPR × v", 2),
        ("unemployed", "Desempleo", "embudo", "población 15+", None, None, "calculado: LFP × u", 3),
        ("out_of_labor", "Fuera del mercado laboral", "embudo", "población 15+", None, None, "calculado: 100 − LFP", 4),
        ("lfp", "Tasa de participación", "acceso", "población 15+", "SL.TLF.CACT.FE.ZS", "SL.TLF.CACT.MA.ZS", "wdi", 5),
        ("unemployment", "Tasa de desempleo", "acceso", "fuerza laboral", "SL.UEM.TOTL.FE.ZS", "SL.UEM.TOTL.MA.ZS", "wdi", 6),
        ("epr", "Tasa de empleo (empleo/población)", "acceso", "población 15+", None, None, "calculado: LFP × (1 − u)", 7),
        ("vulnerable", "Empleo vulnerable (% de ocupados)", "calidad", "ocupados", "SL.EMP.VULN.FE.ZS", "SL.EMP.VULN.MA.ZS", "wdi", 8),
        ("agriculture", "Empleo en agricultura", "sector", "ocupados", "SL.AGR.EMPL.FE.ZS", "SL.AGR.EMPL.MA.ZS", "wdi", 9),
        ("industry", "Empleo en industria", "sector", "ocupados", "SL.IND.EMPL.FE.ZS", "SL.IND.EMPL.MA.ZS", "wdi", 10),
        ("services", "Empleo en servicios", "sector", "ocupados", "SL.SRV.EMPL.FE.ZS", "SL.SRV.EMPL.MA.ZS", "wdi", 11),
    ], columns=["indicator_key", "name_es", "block", "base", "wdi_code_female", "wdi_code_male", "source",
                "sort_order"])
    dim_indicator["unit"] = "%"

    dim_metric = pd.DataFrame([
        ("epr_gap", "Brecha de empleo", "pp", "H − M; positivo = desventaja de las mujeres"),
        ("q_gap", "Brecha de empleo no vulnerable", "pp", "H − M; positivo = desventaja de las mujeres"),
        ("vulnerable_gap", "Brecha de empleo vulnerable", "pp", "M − H; positivo = desventaja de las mujeres"),
        ("duncan_index", "Índice de segregación (Duncan)", "%", "sin signo: mide diferencia, no desventaja"),
    ], columns=["metric", "name_es", "unit", "sign_convention"])

    # sort_order fixes the stacking order in the bar charts (funnel order)
    dim_component = pd.DataFrame([
        ("participation", "Participación", 1),
        ("unemployment", "Desempleo", 2),
        ("access", "Acceso", 3),
        ("quality", "Calidad", 4),
    ], columns=["component", "name_es", "sort_order"])

    print(f"\nStep 7: dim_year {len(dim_year)} years, "
          f"{int(dim_year['is_projection'].sum())} flagged as projection (from {FIRST_PROJECTION_YEAR})")
    return {"dim_country": dim_country, "dim_year": dim_year, "dim_indicator": dim_indicator,
            "dim_sex": dim_sex, "dim_metric": dim_metric, "dim_component": dim_component}


def check_keys(facts, dims):
    """Every key used in a fact table must exist in its dimension (no orphan rows)."""
    links = [
        ("country_code", "dim_country"), ("year", "dim_year"),
        ("indicator_key", "dim_indicator"), ("sex", "dim_sex"),
        ("metric", "dim_metric"), ("component", "dim_component"),
    ]
    problems = []
    for name, fact in facts.items():
        for col, dim in links:
            if col in fact:
                missing = set(fact[col]) - set(dims[dim][col])
                if missing:
                    problems.append(f"{name}.{col} not in {dim}: {sorted(missing)}")
    print("Key check:", "all fact keys found in their dimensions" if not problems else "; ".join(problems))
    return not problems


# ---------------------------------------------------------------- checks
def check(fact):
    problems = []
    if fact.duplicated(KEYS).any():
        problems.append("duplicated rows")
    if not fact["value"].between(0, 100).all():
        problems.append("values outside 0-100")

    sectors = fact[fact["indicator_key"].isin(["agriculture", "industry", "services"])]
    total = sectors.groupby(["country_code", "year", "sex"])["value"].sum()
    if not total.between(99, 101).all():
        problems.append("sector shares do not sum to ~100")

    w = fact.pivot(index=["country_code", "year", "sex"], columns="indicator_key", values="value")
    funnel = w[["lfp", "epr", "q"]].dropna()  # missing values are reported below, not here
    if not ((funnel["q"] <= funnel["epr"]) & (funnel["epr"] <= funnel["lfp"])).all():
        problems.append("funnel broken: expected Q <= EPR <= LFP")

    parts = w[["out_of_labor", "unemployed", "vulnerable_emp", "q"]].dropna()
    if not (parts.sum(axis=1) - 100).abs().max() < 1e-6:
        problems.append("population funnel does not add up to 100")

    missing = fact.groupby(["country_code", "indicator_key"]).size().unstack()
    expected = LAST_YEAR - FIRST_YEAR + 1
    print(f"\nRows per country and indicator (expected {expected} per sex, {2 * expected} total):")
    print(missing.to_string())

    print("\nChecks:", "all passed" if not problems else "FAILED -> " + "; ".join(problems))
    return not problems


def main():
    raw = load_raw()
    long = to_long(raw)
    fact = add_epr_q(long)
    ok = check(fact)

    print()
    gaps = build_gaps(fact)
    decomp = build_decompositions(fact)
    ok = check_decompositions(decomp, gaps) and ok
    preview(gaps, decomp)

    facts = {"fact_indicator": fact, "fact_gap": gaps, "fact_decomposition": decomp}
    dims = build_dimensions()
    ok = check_keys(facts, dims) and ok

    OUT.mkdir(parents=True, exist_ok=True)
    print()
    for name, table in {**facts, **dims}.items():
        table.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8-sig")  # utf-8-sig: accents OK in Excel/Power BI
        print(f"Saved {len(table):>5} rows to {OUT / (name + '.csv')}")
    if not ok:
        print("Review the failed checks before using the files.")


if __name__ == "__main__":
    main()
