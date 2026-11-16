"""Exploration: split vulnerable employment into own-account and family work.

Output: reports/figures/vulnerable_check.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from config import INDICATORS

FACT = Path("data/processed/fact_indicator.csv")
RAW = Path("data/raw/wdi_raw.csv")
FIG = Path("reports/figures/vulnerable_check.png")

COLORS = {"female": "#2a78d6", "male": "#eb6834"}  # validated pair (CVD-safe)
LABELS = {"female": "Mujeres", "male": "Hombres"}
CRISES = [(2008, 2009), (2020, 2021)]
COUNTRIES = ["ARG", "BRA", "CHL", "COL", "URY"]


def load():
    fact = pd.read_csv(FACT)
    vuln = fact[fact["indicator_key"] == "vulnerable"][["country_code", "year", "sex", "value"]]

    # Family workers come from the raw file (validation series, not in fact_indicator)
    raw = pd.read_csv(RAW).rename(columns={"economy": "country_code", "time": "year"})
    fam_cols = {INDICATORS["SL.FAM.WORK.FE.ZS"]: "female", INDICATORS["SL.FAM.WORK.MA.ZS"]: "male"}
    fam = raw.melt(id_vars=["country_code", "year"], value_vars=list(fam_cols),
                   var_name="col", value_name="family")
    fam["sex"] = fam["col"].map(fam_cols)

    df = vuln.rename(columns={"value": "vulnerable"}).merge(
        fam[["country_code", "year", "sex", "family"]], on=["country_code", "year", "sex"])
    df["own_account"] = df["vulnerable"] - df["family"]  # identity: vulnerable = own-account + family
    return df


def plot(df):
    rows = [("vulnerable", "Empleo vulnerable"),
            ("own_account", "Cuenta propia"),
            ("family", "Trabajador familiar")]
    fig, axes = plt.subplots(len(rows), len(COUNTRIES), figsize=(16, 9), sharex=True, sharey="row")
    for r, (col, row_title) in enumerate(rows):
        for c, country in enumerate(COUNTRIES):
            ax = axes[r, c]
            for start, end in CRISES:
                ax.axvspan(start, end + 1, color="#e4e3df", lw=0, zorder=0)
            for sex in ["female", "male"]:
                s = df[(df["country_code"] == country) & (df["sex"] == sex)].sort_values("year")
                ax.plot(s["year"], s[col], color=COLORS[sex], lw=2, label=LABELS[sex])
            ax.grid(axis="y", color="#e4e3df", lw=0.8)
            ax.spines[["top", "right"]].set_visible(False)
            ax.tick_params(labelsize=8, colors="#55544f")
            if r == 0:
                ax.set_title(country, fontsize=11)
            if c == 0:
                ax.set_ylabel(f"{row_title}\n(% del empleo)", fontsize=9)
    axes[0, 0].legend(frameon=False, fontsize=9, loc="upper right")
    fig.suptitle("Empleo vulnerable por sexo y sus dos componentes, 1995-2025 "
                 "(sombreado: crisis 2008-09 y 2020-21)", fontsize=12)
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG, dpi=150)
    print(f"Saved {FIG}")


def summary(df):
    w = df.pivot_table(index=["country_code", "year"], columns="sex",
                       values=["vulnerable", "own_account", "family"])
    gap = pd.DataFrame({
        # same convention as fact_gap: positive = women worse off (more vulnerable)
        "vulnerable": w[("vulnerable", "female")] - w[("vulnerable", "male")],
        "own_account": w[("own_account", "female")] - w[("own_account", "male")],
        "family": w[("family", "female")] - w[("family", "male")],
    }).reset_index()

    years_neg = gap.groupby("country_code")["vulnerable"].agg(
        years_negative=lambda s: int((s < 0).sum()), years_total="count")
    years_neg["first_negative_year"] = gap[gap["vulnerable"] < 0].groupby("country_code")["year"].min()
    print("\nYears with women LESS vulnerable than men (vulnerable gap < 0):")
    print(years_neg.to_string())

    period = {**{y: "1995-97" for y in range(1995, 1998)}, **{y: "2022-24" for y in range(2022, 2025)}}
    gap["period"] = gap["year"].map(period)
    avg = gap.dropna(subset=["period"]).groupby(["country_code", "period"])[
        ["vulnerable", "own_account", "family"]].mean().round(1).unstack()
    print("\nGap women - men (pp), period averages. Negative = women less vulnerable:")
    print(avg.to_string())

    # Big year-to-year jumps can signal a methodology change rather than a real shift
    gap = gap.sort_values(["country_code", "year"])
    gap["jump"] = gap.groupby("country_code")["vulnerable"].diff().abs()
    jumps = gap[gap["jump"] > 2][["country_code", "year", "vulnerable", "jump"]].round(2)
    print("\nYear-to-year changes in the gap above 2 pp (check for breaks):")
    print(jumps.to_string(index=False) if len(jumps) else "none")


if __name__ == "__main__":
    data = load()
    summary(data)
    plot(data)
