import wbgapi as wb
import pandas as pd
from pathlib import Path

from config import INDICATORS

rows = []
for code, name in INDICATORS.items():
    row = {"code": code, "alias": name}
    try:
        row["oficial_name"] = wb.series.get(code)["value"]
        meta = wb.series.metadata.get(code).metadata
        row.update(meta)  # Add each field as a column
    except Exception as e:
        row["error"] = str(e)
    rows.append(row)

df_meta = pd.DataFrame(rows)

out = Path("data/raw")
out.mkdir(parents=True, exist_ok=True)
df_meta.to_csv(out / "indicator_metadata.csv", index=False)

# Key columns to review manually
print(df_meta.columns.tolist())