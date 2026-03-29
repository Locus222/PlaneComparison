import pandas as pd
import numpy as np
import config
import setup

EW = 'Empty Weight [kg]'   # název sloupce prázdné hmotnosti v CSV

def calculate_derived_data(df):
    """
    Calculates derived performance and cost data for the aircraft table.

    Args:
        df (pd.DataFrame): DataFrame with aircraft data.

    Returns:
        pd.DataFrame: DataFrame with new calculated columns.
    """
    # --- Basic Conversions and Preparations ---

    # FuelFlow_*_usgalph = GPH zaokrouhleno na 1 des. místo (USGal/h = GPH)
    # Interní _lph proměnné pro výpočty endurance
    for power_setting in ['75', '65', '55', '45']:
        gph_col     = f'FuelFlow_{power_setting}_gph'
        usgalph_col = f'FuelFlow_{power_setting}_usgalph'
        if gph_col in df.columns:
            df[gph_col]     = pd.to_numeric(df[gph_col], errors='coerce')
            df[usgalph_col] = df[gph_col].round(1)   # GPH = USGal/h

    # Interní LPH pro výpočty výdrže (nezobrazuje se v CSV)
    ff75_lph = df['FuelFlow_75_gph'] * setup.GAL_TO_LITERS if 'FuelFlow_75_gph' in df.columns else pd.Series(dtype=float)
    ff55_lph = df['FuelFlow_55_gph'] * setup.GAL_TO_LITERS if 'FuelFlow_55_gph' in df.columns else pd.Series(dtype=float)

    # --- Payload and Fuel Calculations ---

    df[EW]                          = pd.to_numeric(df[EW],                          errors='coerce').round(0).astype('Int64')
    df['MTOW [kg]']                 = pd.to_numeric(df['MTOW [kg]'],                 errors='coerce').round(0).astype('Int64')
    df['Fuel Capacity [liters]']    = pd.to_numeric(df['Fuel Capacity [liters]'],    errors='coerce').round(0).astype('Int64')
    df['Usefull Load [kg]']         = pd.to_numeric(df['Usefull Load [kg]'],         errors='coerce')
    df['No. Seats']                 = pd.to_numeric(df['No. Seats'],                 errors='coerce').round(0).astype('Int64')

    # Hustota paliva podle typu (AVGAS nebo JET A1)
    fuel_density = np.where(
        df['Fuel type'] == 'JET A1',
        setup.JET_A1_DENSITY_KPL,
        setup.AVGAS_DENSITY_KPL
    )

    # Payload with full Fuel [kg] = Useful Load - hmotnost plného paliva
    # (kolik nákladu lze vzít při plně naplněných nádržích)
    df['Payload with full Fuel [kg]'] = (
        df['Usefull Load [kg]'] - (df['Fuel Capacity [liters]'] * fuel_density)
    ).round(0).astype('Int64')

    # Fuel with max Payload [USGal.] = kolik paliva zbyde při plné obsazenosti
    # max_payload = No. Seats * (76 kg osoba + 5 kg zavazadlo) = No. Seats * 81 kg
    # zbývající hmotnostní rezerva na palivo = Useful Load - max_payload
    fuel_with_max_payload_kg     = df['Usefull Load [kg]'] - (df['No. Seats'] * config.SEAT_WEIGHT_KG)
    fuel_with_max_payload_liters = fuel_with_max_payload_kg / fuel_density
    # Omezit na kapacitu nádrží (nelze vzít více paliva než se vejde)
    fuel_with_max_payload_liters = fuel_with_max_payload_liters.clip(upper=df['Fuel Capacity [liters]'])
    # Převod na US galony
    df['Fuel with max Payload [USGal.]'] = (fuel_with_max_payload_liters * setup.LITERS_TO_GAL).round(1)
    # --- Výpočet paliva a výdrže pro konkrétní posádku (pilot + PAX vepředu) ---
    # FuelWithPilotPax_kg = Useful Load - hmotnost posádky
    df['Fuel with pilot+pax [kg]']      = df['Usefull Load [kg]'] - config.FRONT_CREW_WEIGHT_KG
    df['Fuel with pilot+pax [liters]']  = (df['Fuel with pilot+pax [kg]'] / fuel_density).round(1)

    # The usable fuel is the minimum of what fits in the tank and what the weight limit allows
    df['Usable fuel pilot+pax [liters]'] = df[
        ['Fuel with pilot+pax [liters]', 'Fuel Capacity [liters]']
    ].min(axis=1).round(1)

    # --- Endurance and Range with pilot+pax ---

    vcruise_max_perf_kt    = pd.to_numeric(df['Vcruise 75%'], errors='coerce')
    vcruise_econ_kt        = pd.to_numeric(df['Vcruise 55%'], errors='coerce')
    fuel_flow_max_perf_lph = pd.to_numeric(ff75_lph,          errors='coerce')
    fuel_flow_econ_lph     = pd.to_numeric(ff55_lph,          errors='coerce')

    # Palivová rezerva 30 minut letu při ekonomickém cruise [litry]
    fuel_reserve_lph = fuel_flow_econ_lph * (config.FUEL_RESERVE_MINUTES / 60.0)

    # Použitelné palivo po odečtení rezervy (min 0)
    usable_with_reserve_lph = (df['Usable fuel pilot+pax [liters]'] - fuel_reserve_lph).clip(lower=0)

    # Endurance (h) = (Usable Fuel - Reserve) / Fuel Flow
    # Pro max perf: rezerva odpovídá 30 min při FF_econ (konzervativnější přístup)
    endurance_max_perf_h = usable_with_reserve_lph / fuel_flow_max_perf_lph
    endurance_econ_h     = usable_with_reserve_lph / fuel_flow_econ_lph

    # Convert endurance to h-min format
    df['Endurance pilot+PAX front [h-min]'] = endurance_econ_h.apply(
        lambda h: f"{int(h)}h {int((h * 60) % 60):02d}m" if pd.notna(h) and h > 0 else None
    )
    df['Range max perf pilot+PAX front [NM]']    = (endurance_max_perf_h * vcruise_max_perf_kt).round(1)
    df['Range econ cruise pilot+PAX front [NM]'] = (endurance_econ_h     * vcruise_econ_kt).round(1)

    # --- Endurance with full fuel (economy cruise, žádný payload limit) ---
    endurance_full_fuel_h = df['Fuel Capacity [liters]'] / fuel_flow_econ_lph
    df['Endurance with full fuel[h-min]'] = endurance_full_fuel_h.apply(
        lambda h: f"{int(h)}h {int((h * 60) % 60):02d}m" if pd.notna(h) and h > 0 else None
    )

    # --- Endurance with max payload (economy cruise, palivo = Fuel with max Payload) ---
    endurance_max_payload_h = fuel_with_max_payload_liters / fuel_flow_econ_lph
    df['Endurance with Max payload[h-min]'] = endurance_max_payload_h.apply(
        lambda h: f"{int(h)}h {int((h * 60) % 60):02d}m" if pd.notna(h) and h > 0 else None
    )

    # --- Range with max Payload [NM] (economy cruise, palivo = Fuel with max Payload) ---
    df['Range with max Payload [NM]'] = (endurance_max_payload_h * vcruise_econ_kt).round(1)

    return df


def main():
    try:
        df = pd.read_csv('plane_table.csv', header=0, dtype=str)
    except FileNotFoundError:
        print("Error: 'plane_table.csv' not found.")
        return

    # Oprava překlepů v názvech sloupců
    df.rename(columns={
        'lenth [m]':          'length [m]',
        'toal cost per hour': 'total cost per hour',
    }, inplace=True)

    # Výpočty
    df_calc = calculate_derived_data(df)

    # Sloupce, které se zapíší zpět do plane_table.csv
    computed_cols = [
        'Empty Weight [kg]',
        'MTOW [kg]',
        'Fuel Capacity [liters]',
        'No. Seats',
        'Payload with full Fuel [kg]',
        'Fuel with max Payload [USGal.]',
        'Endurance with full fuel[h-min]',
        'Endurance with Max payload[h-min]',
        'Range with max Payload [NM]',
        'Endurance pilot+PAX front [h-min]',
        'Range max perf pilot+PAX front [NM]',
        'Range econ cruise pilot+PAX front [NM]',
        # pomocné mezisloupce (pro ladění)
        'Fuel with pilot+pax [liters]',
        'Usable fuel pilot+pax [liters]',
        'FuelFlow_75_usgalph', 'FuelFlow_65_usgalph', 'FuelFlow_55_usgalph', 'FuelFlow_45_usgalph',
    ]

    # Zapsat vypočtené hodnoty zpět do plane_table.csv
    for col in computed_cols:
        if col in df_calc.columns:
            df[col] = df_calc[col]

    df.to_csv('plane_table.csv', index=False)
    print("OK - Vysledky zapsany do plane_table.csv")

    # Uložit i kompletní výstup
    df_calc.to_csv('plane_table_calculated.csv', index=False, float_format='%.2f')
    print("OK - Kompletni vystup ulozen do plane_table_calculated.csv")

    # Výpis
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 220)
    cols_show = [
        'Manufacturer', 'Designation', 'Name',
        'No. Seats', 'Usefull Load [kg]',
        'Payload with full Fuel [kg]',
        'Fuel with max Payload [USGal.]',
        'Endurance with full fuel[h-min]',
        'Endurance with Max payload[h-min]',
        'Range with max Payload [NM]',
        'Endurance pilot+PAX front [h-min]',
        'Range max perf pilot+PAX front [NM]',
        'Range econ cruise pilot+PAX front [NM]',
    ]
    print()
    print(df_calc[cols_show].to_string(index=False))


if __name__ == '__main__':
    main()
