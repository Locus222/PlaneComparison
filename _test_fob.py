"""Rychlý test FOB logiky."""
import sys
sys.path.insert(0, '.')
from app import compute

r, *_ = compute({'distance_nm': 200, 'wind_kt': 0, 'avgas_price': 75, 'fuel_reserve_min': 30})
p = r[0]
mp = p['max_power']
ec = p['econ_cruise']

print(f"Letadlo: {p['designation']} {p['name']}")
print(f"  MP  trip_fuel = {mp.get('fuel_l')} l,  FOB = {mp.get('fob_l')} l")
print(f"  EC  trip_fuel = {ec.get('fuel_l')} l,  FOB = {ec.get('fob_l')} l")

# Ověření: FOB > trip_fuel (rezerva > 0)
assert mp['fob_l'] > mp['fuel_l'], "MP: FOB musí být větší než trip fuel"
assert ec['fob_l'] > ec['fuel_l'], "EC: FOB musí být větší než trip fuel"
print("OK – FOB > trip fuel pro oba režimy")

