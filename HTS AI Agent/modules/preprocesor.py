import pandas as pd
import re
from word2number import w2n
from tariff_cal import *
import os

#csv_folder = "tariff_agent_data"
#parsed_files = [f for f in os.listdir(csv_folder) if f.startswith("htsdata") and f.endswith(".csv")]


#s1_df = pd.concat(
#    [pd.read_csv(os.path.join(csv_folder, f)) for f in parsed_files],
#    ignore_index=True
#)

# Optional: Save merged result
#s1_df.to_csv(os.path.join(csv_folder, "merged_hts_duties.csv"), index=False)


csv_path = os.path.join(os.path.dirname(__file__), 'tariff_agent_data\\all_htsdata.csv')

df = pd.read_csv(csv_path)
for col in ["General Rate of Duty", "Special Rate of Duty", "Column 2 Rate of Duty"]:
        df[col] = df[col].apply(lambda x: parse_duty_advanced(x))


df["HTS Number"] = df["HTS Number"].astype(str).str.strip()
df = df[df["HTS Number"] != ""]
df.to_csv("tariff_agent_data\\all_sections_hts_data.csv", index=False)
