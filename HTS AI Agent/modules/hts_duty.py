import pandas as pd
import re 
from word2number import w2n
import os
from tabulate import tabulate
import warnings
warnings.filterwarnings('ignore')


csv_path = os.path.join(os.path.dirname(__file__), 'tariff_agent_data\\all_sections_hts_data.csv')
df = pd.read_csv(csv_path)
df["HTS Number"] = df["HTS Number"].astype(str).str.strip()


def parse_duty(duty_str, unit_weight, quantity, cif_value):
    if isinstance(duty_str, float) and not pd.isna(duty_str):
        return duty_str
    duty_str = str(duty_str).strip().lower()
    if duty_str == "" or "free" in duty_str:
        return 0.0

    if match := re.search(r"([\d.]+)\s*%", duty_str):
        return float(match.group(1)) / 100
    if match := re.search(r"([\d.]+)\s*¢/kg", duty_str):
        return (float(match.group(1)) * unit_weight) / (100 * cif_value) if unit_weight else 0.0
    if match := re.search(r"\$([\d.]+)/unit", duty_str):
        return (float(match.group(1)) * quantity) / cif_value if quantity else 0.0

    return 0.0

def convert_words_to_numbers(text):
    text = re.sub(r'(\d+(?:\.\d+)?)([kmbKMB])', lambda m: str(float(m.group(1)) * {
        'k': 1_000, 'm': 1_000_000, 'b': 1_000_000_000
    }[m.group(2).lower()]), text)

    text = re.sub(r'(\d+)\s+(thousand|million|billion)', lambda m: str(int(m.group(1)) * {
        'thousand': 1_000,
        'million': 1_000_000,
        'billion': 1_000_000_000
    }[m.group(2).lower()]), text, flags=re.IGNORECASE)

    def repl(match):
        try:
            return str(w2n.word_to_num(match.group(0)))
        except:
            return match.group(0)

    return re.sub(r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|"
                  r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
                  r"eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|"
                  r"eighty|ninety|hundred|thousand|million|billion|point|and|[-\s]+)+\b",
                  repl, text, flags=re.IGNORECASE)


def calculate_duty(info: str) -> str:
    info = info.lower().replace("usd", "$").replace("dollars", "$")
    info = convert_words_to_numbers(info)

    hts = re.search(r"hts(?: code)? (\d{4}\.\d{2}\.\d{2}\.\d{2})", info)
    cost = re.search(r"(?:cost|fob).*?[\$]?([\d,\.]+)", info)
    freight = re.search(r"freight.*?[\$]?([\d,\.]+)", info)
    insurance = re.search(r"insurance.*?[\$]?([\d,\.]+)", info)
    weight = re.search(r"([\d,\.]+)\s*(?:kg|kilograms|kilos)", info)
    units = re.search(r"(\d+)\s*units", info)

    if not hts or not cost:
        return "Missing HTS code or product cost."

    hts_code = hts.group(1)
    cost = float(cost.group(1).replace(",", ""))
    freight_val = float(freight.group(1).replace(",", "")) if freight else 0.0
    insurance_val = float(insurance.group(1).replace(",", "")) if insurance else 0.0
    unit_weight = float(weight.group(1).replace(",", "")) if weight else 0.0
    quantity = int(units.group(1)) if units else 1

    cif = cost + freight_val + insurance_val

    row = df[df["HTS Number"] == hts_code]
    if row.empty:
        return f"HTS code {hts_code} not found."

    row = row.iloc[0]
    duty_table = []
    total_duties = 0.0

    for col in ["General Rate of Duty", "Special Rate of Duty", "Column 2 Rate of Duty"]:
        rate = parse_duty(row[col], unit_weight, quantity, cif)
        amount = round(rate * cif, 2)
        if amount > 0:
            duty_table.append([col, f"{rate*100:.2f}%", f"${amount:.2f}"])
            total_duties += amount

    if not duty_table:
        return f"HTS: {hts_code} | CIF: ${cif:,.2f} — No duties applicable."

    duty_table.append(["Total Duties", "", f"${total_duties:.2f}"])
    output = [
        f"HTS: {hts_code}",
        f"CIF: ${cif:,.2f}",
        f"Qty: {quantity}",
        f"Wt: {unit_weight} kg",
        "\nDuties Breakdown:",
        tabulate(duty_table, headers=["HTS Duty Type", "Rate", "Amount"], tablefmt="github")
    ]

    return "\n".join(output)