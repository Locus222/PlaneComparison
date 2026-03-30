"""Rychlý test API pro M20J data."""
import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

body = json.dumps({
    "distance_nm": 200, "wind_kt": 0, "cruise_altitude_ft": 8000,
    "pax1_weight": 95, "pax1_baggage": 5, "pax2_weight": 65, "pax2_baggage": 5,
    "pax3_weight": 0, "pax3_baggage": 0, "pax4_weight": 0, "pax4_baggage": 0,
    "pax5_weight": 0, "pax5_baggage": 0, "pax6_weight": 0, "pax6_baggage": 0,
    "avgas_price": 75, "jet_a1_price": 45, "avgas_density": 0.72,
    "jet_a1_density": 0.81, "fuel_reserve_min": 30, "person_weight_kg": 95,
    "baggage_per_seat_kg": 5, "annual_hours": 80, "currency": "CZK",
    "weight_unit": "kg", "volume_unit": "l"
}).encode()

req = urllib.request.Request(
    "http://127.0.0.1:5000/api/compute",
    data=body, headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())

print("ok =", data.get("ok"))
if not data.get("ok"):
    print("ERROR:", data.get("error"))
    print(data.get("trace", ""))
    sys.exit(1)

m20j = next((p for p in data["planes"] if p["designation"] == "M20J"), None)
if not m20j:
    print("M20J NOT FOUND in response")
    sys.exit(1)

print(f"cruise_climb_kt  = {m20j.get('cruise_climb_kt')}")
print(f"cruise_climb_kmh = {m20j.get('cruise_climb_kmh')}")
print(f"climb_data count = {len(m20j.get('climb_data', []))}")
print(f"desc_data  count = {len(m20j.get('desc_data',  []))}")
print(f"cruise_poh count = {len(m20j.get('cruise_poh', []))}")
print()
print("=== climb_data ===")
for row in m20j.get("climb_data", []):
    print(f"  {row}")
print()
print("=== desc_data ===")
for row in m20j.get("desc_data", []):
    print(f"  {row}")
print()
print("=== cruise_poh ===")
for row in m20j.get("cruise_poh", []):
    print(f"  {row}")
print()
print("=== max_power ===")
mp = m20j.get("max_power", {})
print(f"  v_kt={mp.get('v_kt')}  ff_lph={mp.get('ff_lph')}  fob_l={mp.get('fob_l')}")
print("=== econ_cruise ===")
ec = m20j.get("econ_cruise", {})
print(f"  v_kt={ec.get('v_kt')}  ff_lph={ec.get('ff_lph')}  fob_l={ec.get('fob_l')}")

