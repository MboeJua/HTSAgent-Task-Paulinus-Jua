import pandas as pd
import re # Load HTS data CSV


def set_inputs_values():
    global product_cost, freight, insurance, unit_weight, quantity,cif_value
    product_cost = 10000.0
    freight = 500.0
    insurance = 100.0
    unit_weight = 1000
    quantity = 10
    cif_value = product_cost + freight + insurance


# Duty parser
def parse_duty_advanced(duty_str, unit_weight=None, quantity=None):
    set_inputs_values()
    # Compute CIF
    cif_value = product_cost + freight + insurance
    """
    Parses and returns a duty rate as a decimal fraction (e.g., 0.05 for 5%),
    or a calculated specific duty based on unit_weight or quantity.
    """
    if pd.isna(duty_str) or duty_str.strip() == "":
        return 0.0
    duty_str = duty_str.strip().lower()
    if "free" in duty_str:
        return 0.0
   # Percentage duty (e.g., '5%')
    match = re.search(r"([\d.]+)\s*%", duty_str)
    if match:
        return float(match.group(1)) / 100
    # Weight-based duty (e.g., '2.5¢/kg')
    match = re.search(r"([\d.]+)\s*¢/kg", duty_str)
    if match and unit_weight is not None:
        cents_per_kg = float(match.group(1))
        return (cents_per_kg * unit_weight) / (100 * cif_value) # convert to % of CIF
    # Unit-based duty (e.g., '$1.00/unit')
    match = re.search(r"\$([\d.]+)/unit", duty_str)
    if match and quantity is not None:
        dollars_per_unit = float(match.group(1))
        return (dollars_per_unit * quantity) / cif_value
    return 0.0

# Create working DataFrame
def create_working_df(df, product_cost, freight, insurance, unit_weight, quantity, filename="filename"): 
    #set_inputs_values()
    #cif_value = 10600
    duty_df = df[["HTS Number", "Description", "General Rate of Duty",
                  "Special Rate of Duty", "Column 2 Rate of Duty"]].copy()
    # Apply CIF and input data
    duty_df["CIF Value"] = cif_value
    duty_df["Product Cost"] = product_cost
    duty_df["Freight"] = freight
    duty_df["Insurance"] = insurance
    # Apply duty calculations
    for col in ["General Rate of Duty", "Special Rate of Duty", "Column 2 Rate of Duty"]:
        parsed_col = f"{col} Parsed (%)"
        #amount_col = f"{col} Duty Amount"
        duty_df[parsed_col] = duty_df[col].apply(lambda x: parse_duty_advanced(x, unit_weight,
                                                                               quantity))
        #duty_df[amount_col] = duty_df[parsed_col] * cif_value

# Filter results with any applicable duty
#duty_df_filtered = duty_df[
#    (duty_df["General Rate of Duty Duty Amount"] > 0) |
#    (duty_df["Special Rate of Duty Duty Amount"] > 0) |
#    (duty_df["Column 2 Rate of Duty Duty Amount"] > 0)
#] 
#Save results
    
    duty_df_filtered.to_csv(f"{filename}.csv", index=False)