"""Compare World Bank values with national statistics (2010, 2019, 2022).

Input:  data/raw/wdi_raw.csv, data/validation/national_values.csv
Output: data/validation/comparison.csv  (differences = World Bank - national)
"""
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/wdi_raw.csv")
NATIONAL = Path("data/validation/national_values.csv")
OUT = Path("data/validation/comparison.csv")

INDICATORS = ["unemployment", "labor_force_participation"]
SEXES = ["female", "male"]

wb = pd.read_csv(RAW)
nat = pd.read_csv(NATIONAL)

merged = nat.merge(
    wb,
    left_on=["economy", "year"],
    right_on=["economy", "time"],
    suffixes=("_nat", "_wb"),
)

unmatched = len(nat) - len(merged)
if unmatched:
    print(f"Warning: {unmatched} national rows had no World Bank match.")

# Level differences
for ind in INDICATORS:
    for sex in SEXES:
        merged[f"{ind}_{sex}_diff"] = (
            merged[f"{ind}_{sex}_wb"] - merged[f"{ind}_{sex}_nat"]
        )

# Gaps in each source, and the difference between them
for src in ["wb", "nat"]:
    merged[f"lfp_gap_{src}"] = (
        merged[f"labor_force_participation_male_{src}"]
        - merged[f"labor_force_participation_female_{src}"]
    )
    merged[f"unemp_gap_{src}"] = (
        merged[f"unemployment_female_{src}"] - merged[f"unemployment_male_{src}"]
    )
merged["lfp_gap_diff"] = merged["lfp_gap_wb"] - merged["lfp_gap_nat"]
merged["unemp_gap_diff"] = merged["unemp_gap_wb"] - merged["unemp_gap_nat"]

level_cols = [f"{i}_{s}_diff" for i in INDICATORS for s in SEXES]
gap_cols = ["lfp_gap_diff", "unemp_gap_diff"]

result = merged[["economy", "year"] + level_cols + gap_cols].sort_values(
    ["economy", "year"]
)
OUT.parent.mkdir(parents=True, exist_ok=True)
result.round(2).to_csv(OUT, index=False)

print(result.round(1).to_string(index=False))
print("\nMean absolute difference (percentage points):")
print("Levels:\n", result[level_cols].abs().mean().round(2).to_string())
print("Gaps:\n", result[gap_cols].abs().mean().round(2).to_string())
print("\nMax absolute difference:")
print(result[level_cols + gap_cols].abs().max().round(2).to_string())