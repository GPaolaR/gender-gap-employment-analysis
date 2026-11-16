import wbgapi as wb
import pandas as pd
from pathlib import Path

from config import INDICATORS, COUNTRIES

# Download: one row per (country, year), one column per indicator
df = wb.data.DataFrame(
    list(INDICATORS),
    COUNTRIES,
    time=range(1995, 2026),
    columns="series",
    numericTimeKeys=True,
)
df = df.rename(columns=INDICATORS).reset_index()
    
# Save raw copy
raw = Path("data/raw")
raw.mkdir(parents=True, exist_ok=True)

# Filtrar el DataFrame para los años 2000, 2010, 2019 y 2022
df_filtrado = df[df['time'].isin([2000, 2010, 2019, 2022])]
df_filtrado.to_csv(raw / "wdi_filtrado.csv", index=False)

df.to_csv(raw / "wdi_raw.csv", index=False)

# Validation 1: % missing by indicator and country
indicators = list(INDICATORS.values())
nulls = (
    df.groupby("economy")[indicators]
    .apply(lambda g: g.isna().mean().mul(100).round(1))
)
print("Percentage of missing values by country and indicator:\n", nulls.T, "\n")

# Validation 2: year range with data by indicator
for col in indicators:
    with_data = df.dropna(subset=[col])
    print(f"{col}: {with_data['time'].min()}–{with_data['time'].max()}")

# Validation 3: data consistency
def errors(cond, *cols):
    ok = df[list(cols)].notna().all(axis=1)
    return int((cond & ok).sum())

for s, suf in [("female", "F"), ("male", "M")]:
    pass  # names vary, see below

sectors_F = ["employment_agriculture_female", "employment_industry_female", "employment_services_female"]
sectors_M = ["employment_agriculture_male", "employment_industry_male", "employment_services_male"]

df["sum_sect_F"] = df[sectors_F].sum(axis=1)
df["sum_sect_M"] = df[sectors_M].sum(axis=1)
df["employers_F"] = 100 - df["wage_workers_female"] - df["vulnerable_employment_female"]
df["employers_M"] = 100 - df["wage_workers_male"] - df["vulnerable_employment_male"]

checks = {
    "sectors F do not total ~100": errors(~df["sum_sect_F"].between(99, 101), *sectors_F),
    "sectors M do not total ~100": errors(~df["sum_sect_M"].between(99, 101), *sectors_M),
    "family_workers F > vulnerable F": errors(df["family_workers_female"] > df["vulnerable_employment_female"], "family_workers_female", "vulnerable_employment_female"),
    "family_workers M > vulnerable M": errors(df["family_workers_male"] > df["vulnerable_employment_male"], "family_workers_male", "vulnerable_employment_male"),
    "employers F < 0": errors(df["employers_F"] < -0.5, "wage_workers_female", "vulnerable_employment_female"),
    "employers M < 0": errors(df["employers_M"] < -0.5, "wage_workers_male", "vulnerable_employment_male"),
    "EPR total outside the F-M range": errors(
        ~df["employment_to_population_total"].between(
            df[["employment_to_population_female", "employment_to_population_male"]].min(axis=1),
            df[["employment_to_population_female", "employment_to_population_male"]].max(axis=1)),
        "employment_to_population_total", "employment_to_population_female", "employment_to_population_male"),
    "unemployment total outside the F-M range": errors(
        ~df["unemployment_total"].between(
            df[["unemployment_female", "unemployment_male"]].min(axis=1),
            df[["unemployment_female", "unemployment_male"]].max(axis=1)),
        "unemployment_total", "unemployment_female", "unemployment_male"),
}
for k, v in checks.items():
    print(f"{k}: {v}")

