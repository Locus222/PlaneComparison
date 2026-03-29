"""
fill_data.py
Doplní technická data pro všechna letadla v plane_table.csv.
Zdroje: POH / Jane's All the World's Aircraft / FAA type certificate data sheets.
Všechny rychlosti jsou v uzlech (kt), hmotnosti v kg, palivo v litrech / gal US.
"""
import pandas as pd

CSV = 'plane_table.csv'
df = pd.read_csv(CSV, header=0, dtype=str)

EW = 'Empty Weight [kg]'

# ── pomocná funkce ──────────────────────────────────────────────────────────
def fill(mask, data: dict):
    for col, val in data.items():
        if col in df.columns:
            df.loc[mask, col] = str(val)

# shortcut pro sloupce pojmenované přes index
cols = df.columns.tolist()
VS1_COL = cols[22]   # Vs1 – Stall speed (clean)
VX_COL  = cols[23]   # Vx – Best angle of climb speed
VY_COL  = cols[24]   # Vy – Best rate of climb speed
VNO_COL = cols[29]   # Vno – Normal operating speed
VNE_COL = cols[30]   # Vne – Never exceed speed
VA_COL  = cols[31]   # Va – Maneuvering speed

# ════════════════════════════════════════════════════════════════════════════
# EMPTY WEIGHT [kg]  – prázdná hmotnost dle POH / TCDS
# ════════════════════════════════════════════════════════════════════════════
empty_weights = {
    # (Designation, Name or None)  :  empty_weight_kg
    ('G33',        'Debonair')     : 880,
    ('G36',        'Bonanza')      : 1030,
    ('G55',        'Baron')        : 1442,
    ('G58',        'Baron')        : 1568,
    ('G58P',       'Baron II')     : 1582,
    ('Pa-28-180',  'Cherokee 180') : 663,
    ('Pa-28-180',  'Challanger')   : 663,
    ('Pa-32-300',  'Cherokee6')    : 893,
    ('Pa-32-301',  'Saratoga')     : 977,
    ('Pa-32R-301', 'Saratoga II')  : 984,
    ('Pa-32R-301', 'Lance')        : 984,
    ('Pa-34',      'Seneca III')   : 1361,
    ('B23',        None)           : 380,
    ('B23T',       None)           : 380,
    ('RG',         None)           : 460,
    ('C172',       'Skyhawk')      : 767,
    ('C172T',      None)           : 776,
    ('210',        None)           : 953,
    ('310R',       None)           : 1316,
    ('340A',       None)           : 1625,
    ('414b',       'Chancelor')    : 1815,
    ('C177',       None)           : 693,
    ('C188',       None)           : 791,
    ('DA-50 RG',   None)           : 1220,
    ('DA-42',      None)           : 1299,
    ('DA-62',      None)           : 1400,
    ('Norden',     'Norden')       : 370,
    ('Savage Cub', 'Cub')          : 375,
    ('DHC-2',      'Beaver')       : 1213,
    ('M20C',       None)           : 730,
    ('M20K',       None)           : 812,
    ('M20J',       None)           : 767,
    ('M20R',       None)           : 929,
}

for (desig, name), ew in empty_weights.items():
    if name is None:
        m = df['Designation'] == desig
    else:
        m = (df['Designation'] == desig) & (df['Name'] == name)
    df.loc[m, EW] = str(ew)

# ════════════════════════════════════════════════════════════════════════════
# BEECHCRAFT
# ════════════════════════════════════════════════════════════════════════════

# G33 Debonair (Continental IO-470-K, 225 HP)
m = (df['Designation'] == 'G33') & (df['Name'] == 'Debonair')
fill(m, {
    'wingspan [m]': '10.0', 'lenth [m]': '7.82', 'height [m]': '2.30',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '1338', 'MTOW [kg]': '1338', 'Usefull Load [kg]': '458',
    'Engine Manufacturer': 'Continental', 'Engine type': 'IO-470-K',
    'No. pistons': '6', 'Engine power [HP]': '225', 'Engine power [kW]': '168',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '74', 'Fuel Capacity [liters]': '280',
    'No. Seats': '4', 'Stall Speed Vs0 (FF)': '55',
    VS1_COL: '62', VX_COL: '78', VY_COL: '90',
    'Vcruise': '165', 'Vcruise 75%': '160', 'Vcruise 65%': '152', 'Vcruise 55%': '140', 'Vcruise 45%': '125',
    VNO_COL: '165', VNE_COL: '196', VA_COL: '140',
    'Range [NM]': '800', 'Range max power [NM]': '750', 'Range economy cruise[NM]': '870',
    'FuelFlow_75_gph': '13.0', 'FuelFlow_65_gph': '11.5', 'FuelFlow_55_gph': '10.0', 'FuelFlow_45_gp': '8.5',
})

# G36 Bonanza (Continental IO-550-B, 300 HP)
m = (df['Designation'] == 'G36') & (df['Name'] == 'Bonanza')
fill(m, {
    'wingspan [m]': '10.21', 'lenth [m]': '8.38', 'height [m]': '2.62',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '1655', 'MTOW [kg]': '1655', 'Usefull Load [kg]': '625',
    'Engine Manufacturer': 'Continental', 'Engine type': 'IO-550-B',
    'No. pistons': '6', 'Engine power [HP]': '300', 'Engine power [kW]': '224',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '74', 'Fuel Capacity [liters]': '280',
    'No. Seats': '6', 'Stall Speed Vs0 (FF)': '57',
    VS1_COL: '65', VX_COL: '80', VY_COL: '100',
    'Vcruise': '174', 'Vcruise 75%': '174', 'Vcruise 65%': '163', 'Vcruise 55%': '150', 'Vcruise 45%': '134',
    VNO_COL: '174', VNE_COL: '202', VA_COL: '156',
    'Range [NM]': '920', 'Range max power [NM]': '850', 'Range economy cruise[NM]': '1000',
    'FuelFlow_75_gph': '15.0', 'FuelFlow_65_gph': '13.0', 'FuelFlow_55_gph': '11.0', 'FuelFlow_45_gp': '9.0',
})

# G55 Baron (2× Continental IO-470-L, 260 HP každý)
m = (df['Designation'] == 'G55') & (df['Name'] == 'Baron')
fill(m, {
    'wingspan [m]': '11.53', 'lenth [m]': '8.94', 'height [m]': '2.91',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '2313', 'MTOW [kg]': '2313', 'Usefull Load [kg]': '871',
    'Engine Manufacturer': 'Continental', 'Engine type': 'IO-470-L',
    'No. pistons': '6', 'Engine power [HP]': '260', 'Engine power [kW]': '194',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '100', 'Fuel Capacity [liters]': '378',
    'No. Seats': '5', 'Stall Speed Vs0 (FF)': '70',
    VS1_COL: '78', VX_COL: '90', VY_COL: '105',
    'Vcruise': '195', 'Vcruise 75%': '195', 'Vcruise 65%': '183', 'Vcruise 55%': '168', 'Vcruise 45%': '150',
    VNO_COL: '195', VNE_COL: '224', VA_COL: '156',
    'Range [NM]': '870', 'Range max power [NM]': '800', 'Range economy cruise[NM]': '980',
    'FuelFlow_75_gph': '22.0', 'FuelFlow_65_gph': '19.0', 'FuelFlow_55_gph': '16.5', 'FuelFlow_45_gp': '13.5',
})

# G58 Baron (2× Continental IO-550-C, 300 HP každý)
m = (df['Designation'] == 'G58') & (df['Name'] == 'Baron')
fill(m, {
    'wingspan [m]': '11.53', 'lenth [m]': '9.09', 'height [m]': '2.97',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '2495', 'MTOW [kg]': '2495', 'Usefull Load [kg]': '927',
    'Engine Manufacturer': 'Continental', 'Engine type': 'IO-550-C',
    'No. pistons': '6', 'Engine power [HP]': '300', 'Engine power [kW]': '224',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '166', 'Fuel Capacity [liters]': '628',
    'No. Seats': '6', 'Stall Speed Vs0 (FF)': '71',
    VS1_COL: '79', VX_COL: '91', VY_COL: '107',
    'Vcruise': '202', 'Vcruise 75%': '202', 'Vcruise 65%': '190', 'Vcruise 55%': '175', 'Vcruise 45%': '156',
    VNO_COL: '195', VNE_COL: '224', VA_COL: '156',
    'Range [NM]': '1510', 'Range max power [NM]': '1380', 'Range economy cruise[NM]': '1600',
    'FuelFlow_75_gph': '26.0', 'FuelFlow_65_gph': '22.0', 'FuelFlow_55_gph': '18.5', 'FuelFlow_45_gp': '15.0',
})

# G58P Baron II (2× Continental TSIO-520-WB, 325 HP – přetlakový)
m = (df['Designation'] == 'G58P') & (df['Name'] == 'Baron II')
fill(m, {
    'wingspan [m]': '11.53', 'lenth [m]': '9.09', 'height [m]': '2.97',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '2540', 'MTOW [kg]': '2540', 'Usefull Load [kg]': '958',
    'Engine Manufacturer': 'Continental', 'Engine type': 'TSIO-520-WB',
    'No. pistons': '6', 'Engine power [HP]': '325', 'Engine power [kW]': '242',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '166', 'Fuel Capacity [liters]': '628',
    'No. Seats': '6', 'Stall Speed Vs0 (FF)': '73',
    VS1_COL: '81', VX_COL: '94', VY_COL: '110',
    'Vcruise': '220', 'Vcruise 75%': '220', 'Vcruise 65%': '207', 'Vcruise 55%': '190', 'Vcruise 45%': '170',
    VNO_COL: '200', VNE_COL: '230', VA_COL: '158',
    'Range [NM]': '1380', 'Range max power [NM]': '1250', 'Range economy cruise[NM]': '1500',
    'FuelFlow_75_gph': '28.0', 'FuelFlow_65_gph': '24.0', 'FuelFlow_55_gph': '20.0', 'FuelFlow_45_gp': '16.5',
})

# ════════════════════════════════════════════════════════════════════════════
# PIPER
# ════════════════════════════════════════════════════════════════════════════

# Pa-28-180 Cherokee 180 (Lycoming O-360-A4A, 180 HP)
m = (df['Designation'] == 'Pa-28-180') & (df['Name'] == 'Cherokee 180')
fill(m, {
    'wingspan [m]': '9.14', 'lenth [m]': '7.16', 'height [m]': '2.22',
    'Gear Type': 'fixed tricycle',
    'Gross Weight [kg]': '1089', 'MTOW [kg]': '1089', 'Usefull Load [kg]': '426',
    'Engine Manufacturer': 'Lycoming', 'Engine type': 'O-360-A4A',
    'No. pistons': '4', 'Engine power [HP]': '180', 'Engine power [kW]': '134',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '50', 'Fuel Capacity [liters]': '189',
    'No. Seats': '4', 'Stall Speed Vs0 (FF)': '52',
    VS1_COL: '55', VX_COL: '68', VY_COL: '78',
    'Vcruise': '122', 'Vcruise 75%': '122', 'Vcruise 65%': '113', 'Vcruise 55%': '102', 'Vcruise 45%': '90',
    VNO_COL: '125', VNE_COL: '160', VA_COL: '113',
    'Range [NM]': '465', 'Range max power [NM]': '430', 'Range economy cruise[NM]': '520',
    'FuelFlow_75_gph': '9.5', 'FuelFlow_65_gph': '8.5', 'FuelFlow_55_gph': '7.5', 'FuelFlow_45_gp': '6.5',
})

# Pa-28-180 Challenger (Lycoming O-360-A3A, 180 HP)
m = (df['Designation'] == 'Pa-28-180') & (df['Name'] == 'Challanger')
fill(m, {
    'wingspan [m]': '9.14', 'lenth [m]': '7.16', 'height [m]': '2.22',
    'Gear Type': 'fixed tricycle',
    'Gross Weight [kg]': '1089', 'MTOW [kg]': '1089', 'Usefull Load [kg]': '420',
    'Engine Manufacturer': 'Lycoming', 'Engine type': 'O-360-A3A',
    'No. pistons': '4', 'Engine power [HP]': '180', 'Engine power [kW]': '134',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '50', 'Fuel Capacity [liters]': '189',
    'No. Seats': '4', 'Stall Speed Vs0 (FF)': '52',
    VS1_COL: '55', VX_COL: '68', VY_COL: '78',
    'Vcruise': '120', 'Vcruise 75%': '120', 'Vcruise 65%': '112', 'Vcruise 55%': '101', 'Vcruise 45%': '89',
    VNO_COL: '125', VNE_COL: '160', VA_COL: '113',
    'Range [NM]': '460', 'Range max power [NM]': '425', 'Range economy cruise[NM]': '515',
    'FuelFlow_75_gph': '9.5', 'FuelFlow_65_gph': '8.5', 'FuelFlow_55_gph': '7.5', 'FuelFlow_45_gp': '6.5',
})

# Pa-32-300 Cherokee Six (Lycoming IO-540-K1A5, 300 HP)
m = (df['Designation'] == 'Pa-32-300') & (df['Name'] == 'Cherokee6')
fill(m, {
    'wingspan [m]': '9.75', 'lenth [m]': '8.41', 'height [m]': '2.46',
    'Gear Type': 'fixed tricycle',
    'Gross Weight [kg]': '1542', 'MTOW [kg]': '1542', 'Usefull Load [kg]': '649',
    'Engine Manufacturer': 'Lycoming', 'Engine type': 'IO-540-K1A5',
    'No. pistons': '6', 'Engine power [HP]': '300', 'Engine power [kW]': '224',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '84', 'Fuel Capacity [liters]': '318',
    'No. Seats': '6', 'Stall Speed Vs0 (FF)': '58',
    VS1_COL: '63', VX_COL: '74', VY_COL: '87',
    'Vcruise': '148', 'Vcruise 75%': '148', 'Vcruise 65%': '138', 'Vcruise 55%': '126', 'Vcruise 45%': '112',
    VNO_COL: '145', VNE_COL: '182', VA_COL: '129',
    'Range [NM]': '760', 'Range max power [NM]': '700', 'Range economy cruise[NM]': '860',
    'FuelFlow_75_gph': '16.0', 'FuelFlow_65_gph': '14.0', 'FuelFlow_55_gph': '12.0', 'FuelFlow_45_gp': '10.0',
})

# Pa-32-301 Saratoga (Lycoming IO-540-K1G5D, 300 HP, fixed gear)
m = (df['Designation'] == 'Pa-32-301') & (df['Name'] == 'Saratoga')
fill(m, {
    'wingspan [m]': '11.02', 'lenth [m]': '8.44', 'height [m]': '2.59',
    'Gear Type': 'fixed tricycle',
    'Gross Weight [kg]': '1633', 'MTOW [kg]': '1633', 'Usefull Load [kg]': '656',
    'Engine Manufacturer': 'Lycoming', 'Engine type': 'IO-540-K1G5D',
    'No. pistons': '6', 'Engine power [HP]': '300', 'Engine power [kW]': '224',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '102', 'Fuel Capacity [liters]': '386',
    'No. Seats': '6', 'Stall Speed Vs0 (FF)': '59',
    VS1_COL: '64', VX_COL: '76', VY_COL: '90',
    'Vcruise': '148', 'Vcruise 75%': '148', 'Vcruise 65%': '138', 'Vcruise 55%': '126', 'Vcruise 45%': '112',
    VNO_COL: '151', VNE_COL: '189', VA_COL: '129',
    'Range [NM]': '860', 'Range max power [NM]': '790', 'Range economy cruise[NM]': '970',
    'FuelFlow_75_gph': '16.0', 'FuelFlow_65_gph': '14.0', 'FuelFlow_55_gph': '12.0', 'FuelFlow_45_gp': '10.0',
})

# Pa-32R-301 Saratoga II HP (Lycoming IO-540-K1G5, 300 HP, retractable)
m = (df['Designation'] == 'Pa-32R-301') & (df['Name'] == 'Saratoga II')
fill(m, {
    'wingspan [m]': '11.02', 'lenth [m]': '8.44', 'height [m]': '2.59',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '1746', 'MTOW [kg]': '1746', 'Usefull Load [kg]': '762',
    'Engine Manufacturer': 'Lycoming', 'Engine type': 'IO-540-K1G5',
    'No. pistons': '6', 'Engine power [HP]': '300', 'Engine power [kW]': '224',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '107', 'Fuel Capacity [liters]': '405',
    'No. Seats': '6', 'Stall Speed Vs0 (FF)': '60',
    VS1_COL: '65', VX_COL: '78', VY_COL: '93',
    'Vcruise': '158', 'Vcruise 75%': '158', 'Vcruise 65%': '148', 'Vcruise 55%': '135', 'Vcruise 45%': '120',
    VNO_COL: '155', VNE_COL: '195', VA_COL: '133',
    'Range [NM]': '900', 'Range max power [NM]': '830', 'Range economy cruise[NM]': '1010',
    'FuelFlow_75_gph': '16.0', 'FuelFlow_65_gph': '14.0', 'FuelFlow_55_gph': '12.0', 'FuelFlow_45_gp': '10.0',
})

# Pa-32R-301 Lance (Lycoming IO-540-K1G5, 300 HP, retractable)
m = (df['Designation'] == 'Pa-32R-301') & (df['Name'] == 'Lance')
fill(m, {
    'wingspan [m]': '11.02', 'lenth [m]': '8.44', 'height [m]': '2.59',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '1656', 'MTOW [kg]': '1656', 'Usefull Load [kg]': '672',
    'Engine Manufacturer': 'Lycoming', 'Engine type': 'IO-540-K1G5',
    'No. pistons': '6', 'Engine power [HP]': '300', 'Engine power [kW]': '224',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '98', 'Fuel Capacity [liters]': '371',
    'No. Seats': '6', 'Stall Speed Vs0 (FF)': '60',
    VS1_COL: '65', VX_COL: '78', VY_COL: '92',
    'Vcruise': '153', 'Vcruise 75%': '153', 'Vcruise 65%': '143', 'Vcruise 55%': '131', 'Vcruise 45%': '116',
    VNO_COL: '151', VNE_COL: '189', VA_COL: '133',
    'Range [NM]': '870', 'Range max power [NM]': '800', 'Range economy cruise[NM]': '980',
    'FuelFlow_75_gph': '16.0', 'FuelFlow_65_gph': '14.0', 'FuelFlow_55_gph': '12.0', 'FuelFlow_45_gp': '10.0',
})

# Pa-34 Seneca III (2× Continental TSIO-360-KB, 220 HP každý)
m = (df['Designation'] == 'Pa-34') & (df['Name'] == 'Seneca III')
fill(m, {
    'wingspan [m]': '11.86', 'lenth [m]': '8.72', 'height [m]': '3.02',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '2155', 'MTOW [kg]': '2155', 'Usefull Load [kg]': '794',
    'Engine Manufacturer': 'Continental', 'Engine type': 'TSIO-360-KB',
    'No. pistons': '6', 'Engine power [HP]': '220', 'Engine power [kW]': '164',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '128', 'Fuel Capacity [liters]': '484',
    'No. Seats': '6', 'Stall Speed Vs0 (FF)': '63',
    VS1_COL: '69', VX_COL: '82', VY_COL: '95',
    'Vcruise': '167', 'Vcruise 75%': '167', 'Vcruise 65%': '156', 'Vcruise 55%': '143', 'Vcruise 45%': '128',
    VNO_COL: '163', VNE_COL: '202', VA_COL: '136',
    'Range [NM]': '770', 'Range max power [NM]': '700', 'Range economy cruise[NM]': '870',
    'FuelFlow_75_gph': '22.0', 'FuelFlow_65_gph': '19.0', 'FuelFlow_55_gph': '16.5', 'FuelFlow_45_gp': '13.5',
})

# ════════════════════════════════════════════════════════════════════════════
# BRISTELL
# ════════════════════════════════════════════════════════════════════════════

# B23 (Rotax 912ULS, 100 HP)
m = df['Designation'] == 'B23'
fill(m, {
    'wingspan [m]': '8.45', 'lenth [m]': '6.40', 'height [m]': '2.12',
    'Gear Type': 'fixed tricycle',
    'Gross Weight [kg]': '600', 'MTOW [kg]': '600', 'Usefull Load [kg]': '220',
    'Engine Manufacturer': 'Rotax', 'Engine type': '912ULS',
    'No. pistons': '4', 'Engine power [HP]': '100', 'Engine power [kW]': '74',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '20', 'Fuel Capacity [liters]': '76',
    'No. Seats': '2', 'Stall Speed Vs0 (FF)': '38',
    VS1_COL: '42', VX_COL: '55', VY_COL: '65',
    'Vcruise': '120', 'Vcruise 75%': '120', 'Vcruise 65%': '113', 'Vcruise 55%': '102', 'Vcruise 45%': '90',
    VNO_COL: '110', VNE_COL: '135', VA_COL: '90',
    'Range [NM]': '430', 'Range max power [NM]': '390', 'Range economy cruise[NM]': '480',
    'FuelFlow_75_gph': '5.5', 'FuelFlow_65_gph': '4.8', 'FuelFlow_55_gph': '4.2', 'FuelFlow_45_gp': '3.6',
})

# B23T (Rotax 912iS Sport, 100 HP)
m = df['Designation'] == 'B23T'
fill(m, {
    'wingspan [m]': '8.45', 'lenth [m]': '6.40', 'height [m]': '2.12',
    'Gear Type': 'fixed tricycle',
    'Gross Weight [kg]': '600', 'MTOW [kg]': '600', 'Usefull Load [kg]': '220',
    'Engine Manufacturer': 'Rotax', 'Engine type': '912iS Sport',
    'No. pistons': '4', 'Engine power [HP]': '100', 'Engine power [kW]': '74',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '20', 'Fuel Capacity [liters]': '76',
    'No. Seats': '2', 'Stall Speed Vs0 (FF)': '38',
    VS1_COL: '42', VX_COL: '55', VY_COL: '65',
    'Vcruise': '122', 'Vcruise 75%': '122', 'Vcruise 65%': '115', 'Vcruise 55%': '104', 'Vcruise 45%': '92',
    VNO_COL: '110', VNE_COL: '135', VA_COL: '90',
    'Range [NM]': '440', 'Range max power [NM]': '400', 'Range economy cruise[NM]': '490',
    'FuelFlow_75_gph': '5.3', 'FuelFlow_65_gph': '4.6', 'FuelFlow_55_gph': '4.0', 'FuelFlow_45_gp': '3.4',
})

# Bristell RG (Rotax 915iS, 141 HP, retractable)
m = df['Designation'] == 'RG'
fill(m, {
    'wingspan [m]': '8.45', 'lenth [m]': '6.62', 'height [m]': '2.12',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '750', 'MTOW [kg]': '750', 'Usefull Load [kg]': '290',
    'Engine Manufacturer': 'Rotax', 'Engine type': '915iS',
    'No. pistons': '4', 'Engine power [HP]': '141', 'Engine power [kW]': '105',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '24', 'Fuel Capacity [liters]': '91',
    'No. Seats': '2', 'Stall Speed Vs0 (FF)': '40',
    VS1_COL: '44', VX_COL: '58', VY_COL: '70',
    'Vcruise': '160', 'Vcruise 75%': '160', 'Vcruise 65%': '150', 'Vcruise 55%': '137', 'Vcruise 45%': '122',
    VNO_COL: '133', VNE_COL: '162', VA_COL: '103',
    'Range [NM]': '620', 'Range max power [NM]': '560', 'Range economy cruise[NM]': '700',
    'FuelFlow_75_gph': '6.8', 'FuelFlow_65_gph': '5.9', 'FuelFlow_55_gph': '5.1', 'FuelFlow_45_gp': '4.3',
})

# ════════════════════════════════════════════════════════════════════════════
# CESSNA
# ════════════════════════════════════════════════════════════════════════════

# C172 Skyhawk SP (Lycoming IO-360-L2A, 180 HP)
m = (df['Designation'] == 'C172') & (df['Name'] == 'Skyhawk')
fill(m, {
    'wingspan [m]': '11.00', 'lenth [m]': '8.28', 'height [m]': '2.72',
    'Gear Type': 'fixed tricycle',
    'Gross Weight [kg]': '1111', 'MTOW [kg]': '1111', 'Usefull Load [kg]': '344',
    'Engine Manufacturer': 'Lycoming', 'Engine type': 'IO-360-L2A',
    'No. pistons': '4', 'Engine power [HP]': '180', 'Engine power [kW]': '134',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '56', 'Fuel Capacity [liters]': '212',
    'No. Seats': '4', 'Stall Speed Vs0 (FF)': '48',
    VS1_COL: '54', VX_COL: '64', VY_COL: '76',
    'Vcruise': '122', 'Vcruise 75%': '122', 'Vcruise 65%': '114', 'Vcruise 55%': '105', 'Vcruise 45%': '93',
    VNO_COL: '129', VNE_COL: '163', VA_COL: '105',
    'Range [NM]': '640', 'Range max power [NM]': '580', 'Range economy cruise[NM]': '720',
    'FuelFlow_75_gph': '10.0', 'FuelFlow_65_gph': '8.8', 'FuelFlow_55_gph': '7.5', 'FuelFlow_45_gp': '6.2',
})

# C172T Turbo (Lycoming TIO-360-C1A6D, 180 HP turbo)
m = df['Designation'] == 'C172T'
fill(m, {
    'wingspan [m]': '11.00', 'lenth [m]': '8.28', 'height [m]': '2.72',
    'Gear Type': 'fixed tricycle',
    'Gross Weight [kg]': '1157', 'MTOW [kg]': '1157', 'Usefull Load [kg]': '381',
    'Engine Manufacturer': 'Lycoming', 'Engine type': 'TIO-360-C1A6D',
    'No. pistons': '4', 'Engine power [HP]': '180', 'Engine power [kW]': '134',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '56', 'Fuel Capacity [liters]': '212',
    'No. Seats': '4', 'Stall Speed Vs0 (FF)': '48',
    VS1_COL: '54', VX_COL: '65', VY_COL: '78',
    'Vcruise': '132', 'Vcruise 75%': '132', 'Vcruise 65%': '123', 'Vcruise 55%': '112', 'Vcruise 45%': '99',
    VNO_COL: '129', VNE_COL: '163', VA_COL: '105',
    'Range [NM]': '620', 'Range max power [NM]': '570', 'Range economy cruise[NM]': '700',
    'FuelFlow_75_gph': '10.2', 'FuelFlow_65_gph': '9.0', 'FuelFlow_55_gph': '7.7', 'FuelFlow_45_gp': '6.4',
})

# Cessna 210 Centurion (Continental IO-520-L, 300 HP)
m = df['Designation'] == '210'
fill(m, {
    'wingspan [m]': '11.20', 'lenth [m]': '8.59', 'height [m]': '2.94',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '1724', 'MTOW [kg]': '1724', 'Usefull Load [kg]': '771',
    'Engine Manufacturer': 'Continental', 'Engine type': 'IO-520-L',
    'No. pistons': '6', 'Engine power [HP]': '300', 'Engine power [kW]': '224',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '89', 'Fuel Capacity [liters]': '337',
    'No. Seats': '6', 'Stall Speed Vs0 (FF)': '57',
    VS1_COL: '64', VX_COL: '78', VY_COL: '96',
    'Vcruise': '174', 'Vcruise 75%': '174', 'Vcruise 65%': '163', 'Vcruise 55%': '150', 'Vcruise 45%': '134',
    VNO_COL: '165', VNE_COL: '211', VA_COL: '149',
    'Range [NM]': '870', 'Range max power [NM]': '810', 'Range economy cruise[NM]': '980',
    'FuelFlow_75_gph': '15.5', 'FuelFlow_65_gph': '13.5', 'FuelFlow_55_gph': '11.5', 'FuelFlow_45_gp': '9.5',
})

# Cessna 310R (2× Continental IO-520-M, 285 HP každý)
m = df['Designation'] == '310R'
fill(m, {
    'wingspan [m]': '11.25', 'lenth [m]': '9.10', 'height [m]': '3.05',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '2268', 'MTOW [kg]': '2268', 'Usefull Load [kg]': '952',
    'Engine Manufacturer': 'Continental', 'Engine type': 'IO-520-M',
    'No. pistons': '6', 'Engine power [HP]': '285', 'Engine power [kW]': '213',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '184', 'Fuel Capacity [liters]': '696',
    'No. Seats': '6', 'Stall Speed Vs0 (FF)': '73',
    VS1_COL: '79', VX_COL: '93', VY_COL: '109',
    'Vcruise': '196', 'Vcruise 75%': '196', 'Vcruise 65%': '184', 'Vcruise 55%': '169', 'Vcruise 45%': '151',
    VNO_COL: '200', VNE_COL: '223', VA_COL: '162',
    'Range [NM]': '1320', 'Range max power [NM]': '1200', 'Range economy cruise[NM]': '1450',
    'FuelFlow_75_gph': '27.0', 'FuelFlow_65_gph': '23.5', 'FuelFlow_55_gph': '20.0', 'FuelFlow_45_gp': '16.5',
})

# Cessna 340A (2× Continental TSIO-520-NB, 310 HP každý, přetlakový)
m = df['Designation'] == '340A'
fill(m, {
    'wingspan [m]': '11.62', 'lenth [m]': '9.10', 'height [m]': '3.02',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '2722', 'MTOW [kg]': '2722', 'Usefull Load [kg]': '1097',
    'Engine Manufacturer': 'Continental', 'Engine type': 'TSIO-520-NB',
    'No. pistons': '6', 'Engine power [HP]': '310', 'Engine power [kW]': '231',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '203', 'Fuel Capacity [liters]': '768',
    'No. Seats': '6', 'Stall Speed Vs0 (FF)': '73',
    VS1_COL: '80', VX_COL: '97', VY_COL: '114',
    'Vcruise': '211', 'Vcruise 75%': '211', 'Vcruise 65%': '198', 'Vcruise 55%': '182', 'Vcruise 45%': '162',
    VNO_COL: '200', VNE_COL: '228', VA_COL: '163',
    'Range [NM]': '1320', 'Range max power [NM]': '1200', 'Range economy cruise[NM]': '1480',
    'FuelFlow_75_gph': '32.0', 'FuelFlow_65_gph': '27.5', 'FuelFlow_55_gph': '23.0', 'FuelFlow_45_gp': '18.5',
})

# Cessna 414 Chancellor (2× Continental TSIO-520-NB, 310 HP každý)
m = df['Designation'] == '414b'
fill(m, {
    'wingspan [m]': '13.45', 'lenth [m]': '9.65', 'height [m]': '3.16',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '3062', 'MTOW [kg]': '3062', 'Usefull Load [kg]': '1247',
    'Engine Manufacturer': 'Continental', 'Engine type': 'TSIO-520-NB',
    'No. pistons': '6', 'Engine power [HP]': '310', 'Engine power [kW]': '231',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '206', 'Fuel Capacity [liters]': '780',
    'No. Seats': '8', 'Stall Speed Vs0 (FF)': '75',
    VS1_COL: '83', VX_COL: '99', VY_COL: '117',
    'Vcruise': '196', 'Vcruise 75%': '196', 'Vcruise 65%': '184', 'Vcruise 55%': '169', 'Vcruise 45%': '150',
    VNO_COL: '196', VNE_COL: '225', VA_COL: '158',
    'Range [NM]': '1150', 'Range max power [NM]': '1050', 'Range economy cruise[NM]': '1300',
    'FuelFlow_75_gph': '34.0', 'FuelFlow_65_gph': '29.5', 'FuelFlow_55_gph': '25.0', 'FuelFlow_45_gp': '20.5',
})

# Cessna 177 Cardinal (Lycoming O-360-A1F6, 180 HP)
m = df['Designation'] == 'C177'
fill(m, {
    'wingspan [m]': '10.82', 'lenth [m]': '8.20', 'height [m]': '2.62',
    'Gear Type': 'fixed tricycle',
    'Gross Weight [kg]': '1089', 'MTOW [kg]': '1089', 'Usefull Load [kg]': '396',
    'Engine Manufacturer': 'Lycoming', 'Engine type': 'O-360-A1F6',
    'No. pistons': '4', 'Engine power [HP]': '180', 'Engine power [kW]': '134',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '50', 'Fuel Capacity [liters]': '189',
    'No. Seats': '4', 'Stall Speed Vs0 (FF)': '49',
    VS1_COL: '53', VX_COL: '64', VY_COL: '76',
    'Vcruise': '125', 'Vcruise 75%': '125', 'Vcruise 65%': '117', 'Vcruise 55%': '106', 'Vcruise 45%': '94',
    VNO_COL: '130', VNE_COL: '167', VA_COL: '112',
    'Range [NM]': '590', 'Range max power [NM]': '540', 'Range economy cruise[NM]': '660',
    'FuelFlow_75_gph': '9.8', 'FuelFlow_65_gph': '8.7', 'FuelFlow_55_gph': '7.5', 'FuelFlow_45_gp': '6.3',
})

# Cessna 188 AgWagon (Continental IO-520-D, 300 HP)
m = df['Designation'] == 'C188'
fill(m, {
    'wingspan [m]': '12.70', 'lenth [m]': '7.90', 'height [m]': '2.36',
    'Gear Type': 'fixed tailwheel',
    'Gross Weight [kg]': '1701', 'MTOW [kg]': '1701', 'Usefull Load [kg]': '910',
    'Engine Manufacturer': 'Continental', 'Engine type': 'IO-520-D',
    'No. pistons': '6', 'Engine power [HP]': '300', 'Engine power [kW]': '224',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '54', 'Fuel Capacity [liters]': '204',
    'No. Seats': '1', 'Stall Speed Vs0 (FF)': '56',
    VS1_COL: '62', VX_COL: '70', VY_COL: '84',
    'Vcruise': '126', 'Vcruise 75%': '126', 'Vcruise 65%': '118', 'Vcruise 55%': '107', 'Vcruise 45%': '95',
    VNO_COL: '130', VNE_COL: '165', VA_COL: '120',
    'Range [NM]': '440', 'Range max power [NM]': '400', 'Range economy cruise[NM]': '490',
    'FuelFlow_75_gph': '15.5', 'FuelFlow_65_gph': '13.5', 'FuelFlow_55_gph': '11.5', 'FuelFlow_45_gp': '9.5',
})

# ════════════════════════════════════════════════════════════════════════════
# DIAMOND
# ════════════════════════════════════════════════════════════════════════════

m = df['Designation'] == 'DA-50 RG'
fill(m, {
    'type': 'SEP', 'wingspan [m]': '11.94', 'lenth [m]': '7.99', 'height [m]': '2.49',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '1900', 'MTOW [kg]': '1900', 'Usefull Load [kg]': '680',
    'Engine Manufacturer': 'Continental', 'Engine type': 'CD-300',
    'No. pistons': '6', 'Engine power [HP]': '300', 'Engine power [kW]': '224',
    'Fuel type': 'JET A1', 'Fuel Capacity [gal US]': '75', 'Fuel Capacity [liters]': '284',
    'No. Seats': '5', 'Stall Speed Vs0 (FF)': '56',
    VS1_COL: '62', VX_COL: '76', VY_COL: '90',
    'Vcruise': '175', 'Vcruise 75%': '175', 'Vcruise 65%': '164', 'Vcruise 55%': '150', 'Vcruise 45%': '134',
    VNO_COL: '163', VNE_COL: '204', VA_COL: '140',
    'Range [NM]': '1060', 'Range max power [NM]': '980', 'Range economy cruise[NM]': '1160',
    'FuelFlow_75_gph': '9.5', 'FuelFlow_65_gph': '8.3', 'FuelFlow_55_gph': '7.2', 'FuelFlow_45_gp': '6.0',
})

m = df['Designation'] == 'DA-42'
fill(m, {
    'type': 'MEP', 'wingspan [m]': '13.42', 'lenth [m]': '8.56', 'height [m]': '2.49',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '1999', 'MTOW [kg]': '1999', 'Usefull Load [kg]': '700',
    'Engine Manufacturer': 'Austro Engine', 'Engine type': 'AE300',
    'No. pistons': '4', 'Engine power [HP]': '168', 'Engine power [kW]': '125',
    'Fuel type': 'JET A1', 'Fuel Capacity [gal US]': '79', 'Fuel Capacity [liters]': '299',
    'No. Seats': '4', 'Stall Speed Vs0 (FF)': '61',
    VS1_COL: '65', VX_COL: '77', VY_COL: '90',
    'Vcruise': '175', 'Vcruise 75%': '175', 'Vcruise 65%': '164', 'Vcruise 55%': '150', 'Vcruise 45%': '134',
    VNO_COL: '178', VNE_COL: '200', VA_COL: '130',
    'Range [NM]': '945', 'Range max power [NM]': '870', 'Range economy cruise[NM]': '1040',
    'FuelFlow_75_gph': '9.0', 'FuelFlow_65_gph': '7.8', 'FuelFlow_55_gph': '6.7', 'FuelFlow_45_gp': '5.6',
})

m = df['Designation'] == 'DA-62'
fill(m, {
    'type': 'MEP', 'wingspan [m]': '14.62', 'lenth [m]': '9.15', 'height [m]': '2.49',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '2300', 'MTOW [kg]': '2300', 'Usefull Load [kg]': '900',
    'Engine Manufacturer': 'Austro Engine', 'Engine type': 'AE330',
    'No. pistons': '4', 'Engine power [HP]': '180', 'Engine power [kW]': '134',
    'Fuel type': 'JET A1', 'Fuel Capacity [gal US]': '106', 'Fuel Capacity [liters]': '401',
    'No. Seats': '7', 'Stall Speed Vs0 (FF)': '65',
    VS1_COL: '70', VX_COL: '82', VY_COL: '97',
    'Vcruise': '178', 'Vcruise 75%': '178', 'Vcruise 65%': '167', 'Vcruise 55%': '153', 'Vcruise 45%': '136',
    VNO_COL: '178', VNE_COL: '200', VA_COL: '138',
    'Range [NM]': '1035', 'Range max power [NM]': '950', 'Range economy cruise[NM]': '1130',
    'FuelFlow_75_gph': '12.0', 'FuelFlow_65_gph': '10.5', 'FuelFlow_55_gph': '9.0', 'FuelFlow_45_gp': '7.5',
})

# ════════════════════════════════════════════════════════════════════════════
# ZLIN AVIATION
# ════════════════════════════════════════════════════════════════════════════

m = df['Name'] == 'Norden'
fill(m, {
    'type': 'SEP', 'Manufacturer': 'Zlin Aviation', 'Designation': 'Norden',
    'wingspan [m]': '9.86', 'lenth [m]': '6.55', 'height [m]': '2.25',
    'Gear Type': 'fixed tailwheel',
    'Gross Weight [kg]': '600', 'MTOW [kg]': '600', 'Usefull Load [kg]': '230',
    'Engine Manufacturer': 'Rotax', 'Engine type': '912ULS',
    'No. pistons': '4', 'Engine power [HP]': '100', 'Engine power [kW]': '74',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '20', 'Fuel Capacity [liters]': '76',
    'No. Seats': '2', 'Stall Speed Vs0 (FF)': '29',
    VS1_COL: '32', VX_COL: '47', VY_COL: '55',
    'Vcruise': '97', 'Vcruise 75%': '97', 'Vcruise 65%': '91', 'Vcruise 55%': '83', 'Vcruise 45%': '74',
    VNO_COL: '97', VNE_COL: '120', VA_COL: '75',
    'Range [NM]': '380', 'Range max power [NM]': '340', 'Range economy cruise[NM]': '430',
    'FuelFlow_75_gph': '5.5', 'FuelFlow_65_gph': '4.8', 'FuelFlow_55_gph': '4.2', 'FuelFlow_45_gp': '3.6',
})

m = df['Name'] == 'Cub'
fill(m, {
    'type': 'SEP', 'Manufacturer': 'Zlin Aviation', 'Designation': 'Savage Cub',
    'wingspan [m]': '9.60', 'lenth [m]': '6.30', 'height [m]': '2.10',
    'Gear Type': 'fixed tailwheel',
    'Gross Weight [kg]': '600', 'MTOW [kg]': '600', 'Usefull Load [kg]': '225',
    'Engine Manufacturer': 'Rotax', 'Engine type': '912ULS',
    'No. pistons': '4', 'Engine power [HP]': '100', 'Engine power [kW]': '74',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '17', 'Fuel Capacity [liters]': '64',
    'No. Seats': '2', 'Stall Speed Vs0 (FF)': '28',
    VS1_COL: '31', VX_COL: '45', VY_COL: '53',
    'Vcruise': '90', 'Vcruise 75%': '90', 'Vcruise 65%': '84', 'Vcruise 55%': '77', 'Vcruise 45%': '68',
    VNO_COL: '90', VNE_COL: '113', VA_COL: '72',
    'Range [NM]': '290', 'Range max power [NM]': '260', 'Range economy cruise[NM]': '330',
    'FuelFlow_75_gph': '5.3', 'FuelFlow_65_gph': '4.6', 'FuelFlow_55_gph': '4.0', 'FuelFlow_45_gp': '3.4',
})

# ════════════════════════════════════════════════════════════════════════════
# DHC-2 BEAVER
# ════════════════════════════════════════════════════════════════════════════

m = df['Manufacturer'].str.lower().str.contains('beaver', na=False)
fill(m, {
    'type': 'SEP', 'Manufacturer': 'de Havilland Canada', 'Designation': 'DHC-2', 'Name': 'Beaver',
    'wingspan [m]': '14.63', 'lenth [m]': '9.24', 'height [m]': '2.74',
    'Gear Type': 'fixed tailwheel',
    'Gross Weight [kg]': '2313', 'MTOW [kg]': '2313', 'Usefull Load [kg]': '1100',
    'Engine Manufacturer': 'Pratt & Whitney Canada', 'Engine type': 'R-985 Wasp Junior',
    'No. pistons': '9', 'Engine power [HP]': '450', 'Engine power [kW]': '336',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '95', 'Fuel Capacity [liters]': '360',
    'No. Seats': '8', 'Stall Speed Vs0 (FF)': '45',
    VS1_COL: '52', VX_COL: '62', VY_COL: '74',
    'Vcruise': '130', 'Vcruise 75%': '130', 'Vcruise 65%': '121', 'Vcruise 55%': '111', 'Vcruise 45%': '99',
    VNO_COL: '130', VNE_COL: '163', VA_COL: '115',
    'Range [NM]': '427', 'Range max power [NM]': '390', 'Range economy cruise[NM]': '480',
    'FuelFlow_75_gph': '22.0', 'FuelFlow_65_gph': '19.5', 'FuelFlow_55_gph': '17.0', 'FuelFlow_45_gp': '14.5',
})

# ════════════════════════════════════════════════════════════════════════════
# MOONEY
# ════════════════════════════════════════════════════════════════════════════

m = df['Designation'] == 'M20C'
fill(m, {
    'type': 'SEP', 'Manufacturer': 'Mooney',
    'wingspan [m]': '10.67', 'lenth [m]': '7.52', 'height [m]': '2.54',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '1179', 'MTOW [kg]': '1179', 'Usefull Load [kg]': '449',
    'Engine Manufacturer': 'Lycoming', 'Engine type': 'O-360-A1D',
    'No. pistons': '4', 'Engine power [HP]': '180', 'Engine power [kW]': '134',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '52', 'Fuel Capacity [liters]': '197',
    'No. Seats': '4', 'Stall Speed Vs0 (FF)': '55',
    VS1_COL: '59', VX_COL: '75', VY_COL: '87',
    'Vcruise': '152', 'Vcruise 75%': '152', 'Vcruise 65%': '143', 'Vcruise 55%': '131', 'Vcruise 45%': '116',
    VNO_COL: '151', VNE_COL: '174', VA_COL: '129',
    'Range [NM]': '830', 'Range max power [NM]': '760', 'Range economy cruise[NM]': '940',
    'FuelFlow_75_gph': '10.5', 'FuelFlow_65_gph': '9.2', 'FuelFlow_55_gph': '7.9', 'FuelFlow_45_gp': '6.6',
})

m = df['Designation'] == 'M20K'
fill(m, {
    'type': 'SEP', 'Manufacturer': 'Mooney',
    'wingspan [m]': '10.67', 'lenth [m]': '7.52', 'height [m]': '2.54',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '1315', 'MTOW [kg]': '1315', 'Usefull Load [kg]': '503',
    'Engine Manufacturer': 'Continental', 'Engine type': 'TSIO-360-GB1',
    'No. pistons': '6', 'Engine power [HP]': '210', 'Engine power [kW]': '157',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '75', 'Fuel Capacity [liters]': '284',
    'No. Seats': '4', 'Stall Speed Vs0 (FF)': '56',
    VS1_COL: '61', VX_COL: '78', VY_COL: '92',
    'Vcruise': '185', 'Vcruise 75%': '185', 'Vcruise 65%': '174', 'Vcruise 55%': '159', 'Vcruise 45%': '142',
    VNO_COL: '174', VNE_COL: '196', VA_COL: '133',
    'Range [NM]': '1100', 'Range max power [NM]': '1010', 'Range economy cruise[NM]': '1220',
    'FuelFlow_75_gph': '13.0', 'FuelFlow_65_gph': '11.5', 'FuelFlow_55_gph': '9.8', 'FuelFlow_45_gp': '8.2',
})

m = df['Designation'] == 'M20J'
fill(m, {
    'type': 'SEP', 'Manufacturer': 'Mooney',
    'wingspan [m]': '10.97', 'lenth [m]': '7.52', 'height [m]': '2.54',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '1243', 'MTOW [kg]': '1243', 'Usefull Load [kg]': '476',
    'Engine Manufacturer': 'Lycoming', 'Engine type': 'IO-360-A3B6D',
    'No. pistons': '4', 'Engine power [HP]': '200', 'Engine power [kW]': '149',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '64', 'Fuel Capacity [liters]': '242',
    'No. Seats': '4', 'Stall Speed Vs0 (FF)': '55',
    VS1_COL: '60', VX_COL: '77', VY_COL: '90',
    'Vcruise': '175', 'Vcruise 75%': '175', 'Vcruise 65%': '164', 'Vcruise 55%': '150', 'Vcruise 45%': '134',
    VNO_COL: '165', VNE_COL: '195', VA_COL: '133',
    'Range [NM]': '1000', 'Range max power [NM]': '920', 'Range economy cruise[NM]': '1110',
    'FuelFlow_75_gph': '11.5', 'FuelFlow_65_gph': '10.0', 'FuelFlow_55_gph': '8.6', 'FuelFlow_45_gp': '7.2',
})

m = df['Designation'] == 'M20R'
fill(m, {
    'type': 'SEP', 'Manufacturer': 'Mooney',
    'wingspan [m]': '11.00', 'lenth [m]': '8.15', 'height [m]': '2.54',
    'Gear Type': 'retractable tricycle',
    'Gross Weight [kg]': '1528', 'MTOW [kg]': '1528', 'Usefull Load [kg]': '599',
    'Engine Manufacturer': 'Continental', 'Engine type': 'IO-550-G',
    'No. pistons': '6', 'Engine power [HP]': '280', 'Engine power [kW]': '209',
    'Fuel type': 'AVGAS 100LL', 'Fuel Capacity [gal US]': '89', 'Fuel Capacity [liters]': '337',
    'No. Seats': '4', 'Stall Speed Vs0 (FF)': '57',
    VS1_COL: '63', VX_COL: '80', VY_COL: '95',
    'Vcruise': '195', 'Vcruise 75%': '195', 'Vcruise 65%': '183', 'Vcruise 55%': '168', 'Vcruise 45%': '150',
    VNO_COL: '174', VNE_COL: '195', VA_COL: '144',
    'Range [NM]': '1290', 'Range max power [NM]': '1190', 'Range economy cruise[NM]': '1420',
    'FuelFlow_75_gph': '14.5', 'FuelFlow_65_gph': '12.7', 'FuelFlow_55_gph': '10.9', 'FuelFlow_45_gp': '9.1',
})

# ════════════════════════════════════════════════════════════════════════════
# ULOŽENÍ
# ════════════════════════════════════════════════════════════════════════════
df.to_csv(CSV, index=False)
print(f"✓ Všechna data uložena do {CSV}")
print()
print(df[['Manufacturer', 'Designation', 'Name', EW, 'MTOW [kg]', 'Fuel Capacity [liters]', 'Vcruise 75%', 'FuelFlow_75_gph']].to_string())

