import pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')
df = pd.read_csv('plane_table.csv', dtype=str)
print("COLUMNS:", list(df.columns))
m20j = df[df['Designation']=='M20J']
print("M20J rows:", len(m20j))
if len(m20j):
    row = m20j.iloc[0].to_dict()
    for k,v in row.items():
        if v and str(v).strip():
            print(f"  {k}: {v}")

