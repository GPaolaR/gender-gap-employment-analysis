COUNTRIES = ["ARG", "BRA", "CHL", "COL", "URY"]

CORE = {
    "SL.TLF.CACT.FE.ZS": "labor_force_participation_female",
    "SL.TLF.CACT.MA.ZS": "labor_force_participation_male",
    "SL.UEM.TOTL.FE.ZS": "unemployment_female",
    "SL.UEM.TOTL.MA.ZS": "unemployment_male",
    "SL.EMP.VULN.FE.ZS": "vulnerable_employment_female",
    "SL.EMP.VULN.MA.ZS": "vulnerable_employment_male",
    "SL.EMP.TOTL.SP.FE.ZS": "employment_to_population_female",
    "SL.EMP.TOTL.SP.MA.ZS": "employment_to_population_male",
    "SL.EMP.WORK.FE.ZS": "wage_workers_female",
    "SL.EMP.WORK.MA.ZS": "wage_workers_male",
    "SL.AGR.EMPL.FE.ZS": "employment_agriculture_female",
    "SL.AGR.EMPL.MA.ZS": "employment_agriculture_male",
    "SL.IND.EMPL.FE.ZS": "employment_industry_female",
    "SL.IND.EMPL.MA.ZS": "employment_industry_male",
    "SL.SRV.EMPL.FE.ZS": "employment_services_female",
    "SL.SRV.EMPL.MA.ZS": "employment_services_male",
}

VALIDATION = {
    # Series totales
    "SL.EMP.TOTL.SP.ZS": "employment_to_population_total",
    "SL.UEM.TOTL.ZS": "unemployment_total",
    # Componente del empleo vulnerable
    "SL.FAM.WORK.FE.ZS": "family_workers_female",
    "SL.FAM.WORK.MA.ZS": "family_workers_male",
}

INDICATORS = {**CORE, **VALIDATION}