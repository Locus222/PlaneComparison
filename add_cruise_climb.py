"""
add_cruise_climb.py
Přidá sloupec 'Cruise climb [km/h]' do plane_table.csv.
Hodnota pro M20J: 102 kt × 1.852 = 188.9 → zaokrouhleno na 189 km/h
Sloupec se zařadí za skupinu Climb (za posledni Climb_Time_12000ft).
"""
import pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')

KT_TO_KMH = 1.852
CSV = 'plane_table.csv'

df = pd.read_csv(CSV, dtype=str)

COL = 'Cruise climb [km/h]'

if COL not in df.columns:
    df[COL] = ''

# M20J: 102 kt
value = str(round(102 * KT_TO_KMH))
df.loc[df['Designation'] == 'M20J', COL] = value

df.to_csv(CSV, index=False)

print('OK: sloupec', COL, 'pridan, M20J =', value, 'km/h (102 kt)')
print('Celkem sloupcu:', len(df.columns))
idx = list(df.columns).index(COL)
print('Pozice:', idx, '| pred:', df.columns[idx-1])
