import app, math

# Logika mezipristani
print("=== Test logiky ===")
for dist, leg, expected in [(79,80,0),(80,80,0),(120,80,1),(160,80,1),(161,80,2),(180,80,2)]:
    stops = max(0, math.ceil(dist / leg) - 1)
    ok = "OK  " if stops == expected else "FAIL"
    print(f"  {ok} dist={dist}NM leg={leg}NM → {stops} zastávek (očekáváno {expected})")

print("\n=== Test API (120 NM) ===")
results, *_ = app.compute({'distance_nm': 120, 'wind_kt': 0})
for p in results[:3]:
    mp = p['max_power']
    ec = p['econ_cruise']
    print(f"  {p['designation']:15s}  MP: stops={mp['stops']} leg={mp['leg_nm']}NM total={mp['total_time_fmt']}  "
          f"EC: stops={ec['stops']} leg={ec['leg_nm']}NM total={ec['total_time_fmt']}")

print("\n=== Test API (200 NM) ===")
results2, *_ = app.compute({'distance_nm': 200, 'wind_kt': 0})
for p in results2[:3]:
    mp = p['max_power']
    ec = p['econ_cruise']
    print(f"  {p['designation']:15s}  MP: stops={mp['stops']} leg={mp['leg_nm']}NM  EC: stops={ec['stops']} leg={ec['leg_nm']}NM")

