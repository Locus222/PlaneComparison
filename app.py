"""
app.py – Flask webová aplikace PlaneComparison
Spustit: python app.py
Otevřít: http://127.0.0.1:5000
"""
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import math
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'plane_table.csv')

# ---------------------------------------------------------------------------
# Pomocné funkce
# ---------------------------------------------------------------------------

def load_planes() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, header=0, dtype=str)
    numeric_cols = [
        'Empty Weight [kg]', 'MTOW [kg]', 'Useful Load [kg]', 'No. Seats',
        'Fuel Capacity [l]',
        'Vcruise_75 [km/h]', 'Vcruise_65 [km/h]', 'Vcruise_55 [km/h]', 'Vcruise_45 [km/h]',
        'FF_75 [l/h]', 'FF_65 [l/h]', 'FF_55 [l/h]', 'FF_45 [l/h]',
        'Fixed cost [CZK/yr]', 'Variable cost [CZK/yr]',
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    return df


def fmt_hm(h: float) -> str:
    """Převede hodiny (float) na řetězec h:mm."""
    if h is None or (isinstance(h, float) and np.isnan(h)) or h <= 0:
        return '–'
    hh = int(h)
    mm = int(round((h - hh) * 60))
    return f'{hh}h {mm:02d}m'


GAL_TO_L  = 3.78541
NM_TO_KM  = 1.852
KT_TO_KPH = 1.852

# Výchozí kurzy: kolik CZK za 1 jednotku cizí měny
DEFAULT_FOREIGN_TO_CZK = {
    'EUR': 24.545,
    'USD': 21.315,
    'GBP': 28.299,
}

CURRENCY_SYMBOLS = {
    'CZK': 'Kč',
    'EUR': '€',
    'USD': '$',
    'GBP': '£',
}


def compute(params: dict) -> list:
    """
    Parametry (dict):
      general: avgas_price, jet_a1_price, avgas_density, jet_a1_density,
               fuel_reserve_min, person_weight_kg, baggage_per_seat_kg,
               currency, czk_to_eur, czk_to_usd, czk_to_gbp
      plan:    distance_nm, wind_kt
      crew:    pax1..6 weight + baggage
    Vrátí seznam dicts – jeden na letadlo.
    Ceny paliva jsou vždy zadávány v CZK; výsledné náklady jsou převedeny
    do zvolené měny pomocí kurzu.
    """
    # --- obecné ---
    avgas_price      = float(params.get('avgas_price',      75.0))
    jet_a1_price     = float(params.get('jet_a1_price',     45.0))
    avgas_density    = float(params.get('avgas_density',    0.72))
    jet_a1_density   = float(params.get('jet_a1_density',   0.81))
    fuel_reserve_min = float(params.get('fuel_reserve_min', 30))
    person_weight    = float(params.get('person_weight_kg', 76))
    baggage_per_seat = float(params.get('baggage_per_seat_kg', 5))
    seat_weight      = person_weight + baggage_per_seat
    annual_hours     = max(float(params.get('annual_hours', 80)), 1.0)  # min 1 h/rok

    # --- měna ---
    currency = str(params.get('currency', 'CZK')).upper()
    if currency not in CURRENCY_SYMBOLS:
        currency = 'CZK'
    # Kurzy: uživatel zadává "1 cizí = X CZK" → fx_rate = 1 / X
    key_map = {'EUR': 'eur_to_czk', 'USD': 'usd_to_czk', 'GBP': 'gbp_to_czk'}
    if currency == 'CZK':
        fx_rate = 1.0
    else:
        default_foreign_to_czk = DEFAULT_FOREIGN_TO_CZK[currency]
        foreign_to_czk = float(params.get(key_map[currency], default_foreign_to_czk))
        if foreign_to_czk <= 0:
            foreign_to_czk = default_foreign_to_czk
        fx_rate = 1.0 / foreign_to_czk

    # --- jednotky ---
    weight_unit = str(params.get('weight_unit', 'kg')).lower()
    volume_unit = str(params.get('volume_unit', 'l')).lower()
    LB_TO_KG = 0.453592

    # --- plán ---
    distance_nm = float(params.get('distance_nm', 200))
    wind_kt     = float(params.get('wind_kt',     0))

    # --- obsazení ---
    pax_weights   = []
    pax_baggages  = []
    for i in range(1, 7):
        w = float(params.get(f'pax{i}_weight',  0))
        b = float(params.get(f'pax{i}_baggage', 0))
        # Pokud uživatel zadával v lb, převedeme na kg pro výpočet
        if weight_unit == 'lb':
            w *= LB_TO_KG
            b *= LB_TO_KG
        pax_weights.append(w)
        pax_baggages.append(b)

    total_pax_kg   = sum(pax_weights) + sum(pax_baggages)
    occupied_seats = sum(1 for w in pax_weights if w > 0)

    df = load_planes()
    results = []

    for _, row in df.iterrows():
        r = {
            'type':         row.get('type', ''),
            'manufacturer': row.get('Manufacturer', ''),
            'designation':  row.get('Designation', ''),
            'name':         row.get('Name', ''),
            'no_seats':     int(row['No. Seats']) if pd.notna(row.get('No. Seats')) else 0,
            'empty_weight': row.get('Empty Weight [kg]', ''),
            'mtow':         row.get('MTOW [kg]', ''),
            'useful_load':  row.get('Useful Load [kg]', ''),
            'fuel_type':    row.get('Fuel type', 'AVGAS 100LL'),
        }

        useful_load = pd.to_numeric(row.get('Useful Load [kg]'),   errors='coerce')
        mtow        = pd.to_numeric(row.get('MTOW [kg]'),          errors='coerce')
        empty_wt    = pd.to_numeric(row.get('Empty Weight [kg]'),  errors='coerce')
        no_seats    = pd.to_numeric(row.get('No. Seats'),          errors='coerce')
        fuel_cap_l  = pd.to_numeric(row.get('Fuel Capacity [l]'),  errors='coerce')

        r['fuel_cap_l'] = float(fuel_cap_l) if pd.notna(fuel_cap_l) else None

        # CSV ukládá rychlosti v km/h, spotřebu v l/h → převedeme zpět na kt/GPH pro interní výpočty
        KMH_TO_KT  = 1.0 / KT_TO_KPH
        LPH_TO_GPH = 1.0 / GAL_TO_L

        v75_kmh     = pd.to_numeric(row.get('Vcruise_75 [km/h]'), errors='coerce')
        v55_kmh     = pd.to_numeric(row.get('Vcruise_55 [km/h]'), errors='coerce')
        ff75_lph    = pd.to_numeric(row.get('FF_75 [l/h]'),       errors='coerce')
        ff55_lph    = pd.to_numeric(row.get('FF_55 [l/h]'),       errors='coerce')

        # Interní výpočty pracují v kt a GPH (historicky), převedeme
        v75      = v75_kmh  * KMH_TO_KT  if pd.notna(v75_kmh)  else float('nan')
        v55      = v55_kmh  * KMH_TO_KT  if pd.notna(v55_kmh)  else float('nan')
        ff75_gph = ff75_lph * LPH_TO_GPH if pd.notna(ff75_lph) else float('nan')
        ff55_gph = ff55_lph * LPH_TO_GPH if pd.notna(ff55_lph) else float('nan')

        fuel_type   = str(row.get('Fuel type', 'AVGAS 100LL'))

        # ── Náklady letadla: fixní + variabilní / nalétané hodiny ────────
        fixed_cost_czk    = pd.to_numeric(row.get('Fixed cost [CZK/yr]'),    errors='coerce')
        variable_cost_czk = pd.to_numeric(row.get('Variable cost [CZK/yr]'), errors='coerce')
        # cost_ph = roční náklady (bez paliva) přepočítané na 1 h dle zadaného annual_hours
        if pd.notna(fixed_cost_czk) and pd.notna(variable_cost_czk):
            cost_ph = (float(fixed_cost_czk) + float(variable_cost_czk)) / annual_hours
        elif pd.notna(fixed_cost_czk):
            cost_ph = float(fixed_cost_czk) / annual_hours
        elif pd.notna(variable_cost_czk):
            cost_ph = float(variable_cost_czk) / annual_hours
        else:
            cost_ph = float('nan')

        r['fixed_cost_czk']    = float(fixed_cost_czk)    if pd.notna(fixed_cost_czk)    else None
        r['variable_cost_czk'] = float(variable_cost_czk) if pd.notna(variable_cost_czk) else None

        density      = jet_a1_density if 'JET' in fuel_type.upper() else avgas_density
        fuel_price   = jet_a1_price   if 'JET' in fuel_type.upper() else avgas_price

        def calc_mode(v_kt, ff_gph, label):
            """
            Výpočet pro jeden výkonnostní režim.

            Definice (weight_balance_rules.md):
              payload    = součet osádky + zavazadla  (total_pax_kg – pevná hodnota)
              trip_fuel  = palivo na let A→B
              reserve    = palivo na fuel_reserve_min minut (při daném FF)
              FOB        = trip_fuel + reserve
              trip_load  = FOB [kg] + payload [kg]
              podmínka   : useful_load >= trip_load
            """
            out = {}
            if any(pd.isna(x) for x in [v_kt, ff_gph, distance_nm]):
                for k in ['v_kt', 'v_kmh', 'ff_gph', 'ff_lph', 'flight_time_h',
                          'flight_time_fmt', 'trip_fuel_l', 'fob_l',
                          'fuel_cost', 'plane_cost', 'total_cost',
                          'stops', 'leg_nm', 'total_time_h', 'total_time_fmt',
                          'trip_load_kg', 'load_reserve_kg', 'range_warning', 'needed_fuel_l']:
                    out[k] = None
                return out

            gs_kt         = max(v_kt + wind_kt, 1.0)
            ff_lph        = ff_gph * GAL_TO_L
            flight_time_h = distance_nm / gs_kt

            # ── Trip fuel & FOB ───────────────────────────────────────────
            trip_fuel_l = ff_lph * flight_time_h          # palivo na let A→B [l]
            reserve_l   = ff_lph * (fuel_reserve_min / 60.0)  # rezerva [l]
            fob_l       = round(trip_fuel_l + reserve_l, 1)   # Fuel On Board [l]

            # ── Trip Load = FOB [kg] + Payload [kg] ──────────────────────
            fob_kg        = fob_l * density
            trip_load_kg  = round(fob_kg + total_pax_kg, 1)

            # ── Load Reserve = Useful Load − Trip Load ────────────────────
            load_reserve_kg = round(float(useful_load) - trip_load_kg, 1) if pd.notna(useful_load) else None

            # ── Náklady ───────────────────────────────────────────────────
            fuel_cost_czk  = trip_fuel_l * fuel_price
            plane_cost_czk = (cost_ph * flight_time_h) if pd.notna(cost_ph) else None
            total_cost_czk = (fuel_cost_czk + plane_cost_czk) if plane_cost_czk is not None else None

            fuel_cost  = round(fuel_cost_czk  * fx_rate, 2)
            plane_cost = round(plane_cost_czk * fx_rate, 2) if plane_cost_czk is not None else None
            total_cost = round(total_cost_czk * fx_rate, 2) if total_cost_czk is not None else None

            # ── Range warning: FOB > kapacita nádrže ─────────────────────
            range_warning = bool(pd.notna(fuel_cap_l) and fob_l > fuel_cap_l)

            # ── Mezipřistání ──────────────────────────────────────────────
            stops  = 0
            leg_nm = None
            if pd.notna(fuel_cap_l):
                usable_l = fuel_cap_l - reserve_l
                if usable_l > 0 and ff_lph > 0:
                    max_range_nm = (usable_l / ff_lph) * gs_kt
                    leg_nm_calc  = max_range_nm * 0.8
                    if leg_nm_calc > 0:
                        leg_nm = round(leg_nm_calc, 1)
                        stops  = max(0, math.ceil(distance_nm / leg_nm_calc) - 1)

            total_time_h = flight_time_h + stops * (45 / 60.0)

            out.update({
                'v_kt':            round(v_kt, 0),
                'v_kmh':           round(v_kt * KT_TO_KPH, 0),
                'ff_gph':          round(ff_gph, 1),
                'ff_lph':          round(ff_lph, 1),
                'flight_time_h':   round(flight_time_h, 3),
                'flight_time_fmt': fmt_hm(flight_time_h),
                'trip_fuel_l':     round(trip_fuel_l, 1),
                'fob_l':           fob_l,
                'trip_load_kg':    trip_load_kg,
                'load_reserve_kg': load_reserve_kg,
                'fuel_cost':       fuel_cost,
                'plane_cost':      plane_cost,
                'total_cost':      total_cost,
                'range_warning':   range_warning,
                'needed_fuel_l':   round(fob_l, 1),   # alias – kolik FOB je potřeba
                'stops':           stops,
                'leg_nm':          leg_nm,
                'total_time_h':    round(total_time_h, 3),
                'total_time_fmt':  fmt_hm(total_time_h),
            })
            return out

        r['max_power']   = calc_mode(v75, ff75_gph, '75%')
        r['econ_cruise'] = calc_mode(v55, ff55_gph, '55%')

        # ── PAYLOAD = součet osádky + zavazadla (definice, pevná hodnota) ──
        r['payload_kg'] = round(total_pax_kg, 1)

        # ── FOB pro každý režim (z calc_mode) ────────────────────────────
        r['mp_fob_l'] = r['max_power'].get('fob_l')
        r['ec_fob_l'] = r['econ_cruise'].get('fob_l')

        # ── Vhodnost: useful_load >= trip_load (pro každý regime) ────────
        # Používáme EC jako konzervativnější (vyšší FF → vyšší FOB)
        reason = []

        # Kontrola sedadel
        fail_seats = False
        if pd.notna(no_seats) and occupied_seats > int(no_seats):
            reason.append(f'obsazeno {occupied_seats} sedadel, kapacita {int(no_seats)}')
            fail_seats = True

        # Hlavní podmínka: useful_load >= trip_load – vyhodnotit pro každý profil zvlášť
        fail_load    = False   # celkový flag (True pokud selhává alespoň jeden profil)
        fail_load_mp = False
        fail_load_ec = False
        if pd.notna(useful_load):
            ul = float(useful_load)
            mp_tl = r['max_power'].get('trip_load_kg')
            ec_tl = r['econ_cruise'].get('trip_load_kg')
            if mp_tl is not None and mp_tl > ul:
                fail_load_mp = True
            if ec_tl is not None and ec_tl > ul:
                fail_load_ec = True
            # Konzervativní celkový fail = selhání alespoň jednoho profilu
            fail_load = fail_load_mp or fail_load_ec
            if fail_load:
                # Zpráva: použijeme ten profil s vyšším přetížením
                worst_tl = max(
                    (mp_tl or 0) if fail_load_mp else 0,
                    (ec_tl or 0) if fail_load_ec else 0,
                )
                reason.append(
                    f'trip load ({int(worst_tl)} kg) > užit. zátěž ({int(ul)} kg)'
                )

        r['suitable']          = len(reason) == 0
        r['unsuitable_reason'] = '; '.join(reason) if reason else ''
        r['fail_seats']        = fail_seats
        r['fail_load']         = fail_load
        r['fail_load_mp']      = fail_load_mp
        r['fail_load_ec']      = fail_load_ec

        # Hour Rates – náklady za hodinu letu (nezávislé na vzdálenosti)
        def calc_hour_rates(ff75_gph, ff55_gph, cost_ph, fuel_price, density, fx_rate):
            out = {}
            ff75_lph = (ff75_gph * GAL_TO_L) if pd.notna(ff75_gph) else None
            ff55_lph = (ff55_gph * GAL_TO_L) if pd.notna(ff55_gph) else None
            out['mp_ff_lph']       = round(ff75_lph, 1)                               if ff75_lph is not None else None
            out['mp_fuel_cost_ph'] = round(ff75_lph * fuel_price * fx_rate, 2)        if ff75_lph is not None else None
            out['ec_ff_lph']       = round(ff55_lph, 1)                               if ff55_lph is not None else None
            out['ec_fuel_cost_ph'] = round(ff55_lph * fuel_price * fx_rate, 2)        if ff55_lph is not None else None
            plane_cost_ph_native   = round(cost_ph * fx_rate, 2)                      if pd.notna(cost_ph) else None
            out['plane_cost_ph']   = plane_cost_ph_native
            out['mp_total_ph']     = round(out['mp_fuel_cost_ph'] + plane_cost_ph_native, 2) \
                if (out['mp_fuel_cost_ph'] is not None and plane_cost_ph_native is not None) else None
            out['ec_total_ph']     = round(out['ec_fuel_cost_ph'] + plane_cost_ph_native, 2) \
                if (out['ec_fuel_cost_ph'] is not None and plane_cost_ph_native is not None) else None
            return out

        r['hour_rates']      = calc_hour_rates(ff75_gph, ff55_gph, cost_ph, fuel_price, density, fx_rate)
        r['currency']        = currency
        r['currency_symbol'] = CURRENCY_SYMBOLS[currency]
        r['weight_unit']     = weight_unit
        r['volume_unit']     = volume_unit

        results.append(r)

    # Řazení: vhodná letadla napřed, pak dle economy total_cost
    def sort_key(x):
        suitable = 0 if x['suitable'] else 1
        cost = x['econ_cruise'].get('total_cost') or 9_999_999
        return (suitable, cost)

    results.sort(key=sort_key)
    meta = {
        'total_pax_kg':   round(total_pax_kg, 1),
        'occupied_seats': occupied_seats,
    }
    return results, currency, CURRENCY_SYMBOLS[currency], weight_unit, volume_unit, meta


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

def _sanitize(obj):
    """Rekurzivně nahradí float NaN a Inf za None (JSON-safe)."""
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    # pandas NA / numpy scalar
    try:
        if isinstance(obj, float) and not (obj == obj):   # NaN check
            return None
    except TypeError:
        pass
    # convert numpy int/float scalars to Python native
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        f = float(obj)
        return None if (np.isnan(f) or np.isinf(f)) else f
    return obj


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/hangar', methods=['GET'])
def api_hangar():
    """Vrátí surová data z plane_table.csv pro záložku Hangár."""
    try:
        df = load_planes()
        # Vybrané sloupce pro zobrazení – v pořadí skupin (nová struktura CSV)
        cols = [
            # Identifikace
            'type', 'Manufacturer', 'Designation', 'Name',
            # Konfigurace
            'No. Seats', 'Gear Type', 'Fuel type',
            # Rozměry
            'Wingspan [m]', 'Length [m]', 'Height [m]',
            # Hmotnosti
            'Empty Weight [kg]', 'MTOW [kg]', 'Useful Load [kg]',
            # Nádrž
            'Fuel Capacity [l]',
            # Motor
            'Engine Manufacturer', 'Engine type', 'No. pistons',
            'Engine power [HP]', 'Engine power [kW]',
            # Rychlosti (km/h – nová základní jednotka)
            'Vcruise_75 [km/h]', 'Vcruise_65 [km/h]', 'Vcruise_55 [km/h]',
            'Vs0 [km/h]', 'Vs1 [km/h]',
            'Vx [km/h]', 'Vy [km/h]',
            'Vno [km/h]', 'Vne [km/h]',
            # Spotřeba (l/h)
            'FF_75 [l/h]', 'FF_55 [l/h]',
            # Dolet (km)
            'Range_MP [km]', 'Range_EC [km]',
            # Náklady
            'Fixed cost [CZK/yr]', 'Variable cost [CZK/yr]',
        ]
        present = [c for c in cols if c in df.columns]
        sub = df[present].copy()
        # NaN → None pro JSON
        records = []
        for _, row in sub.iterrows():
            rec = {}
            for c in present:
                v = row[c]
                if pd.isna(v):
                    rec[c] = None
                else:
                    rec[c] = v
            records.append(rec)
        return jsonify({'ok': True, 'columns': present, 'rows': _sanitize(records)})
    except Exception as e:
        import traceback
        return jsonify({'ok': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/compute', methods=['POST'])
def api_compute():
    params = request.get_json(force=True)
    try:
        results, currency, currency_symbol, weight_unit, volume_unit, meta = compute(params)
        safe = _sanitize(results)
        return jsonify({
            'ok': True,
            'planes': safe,
            'currency': currency,
            'currency_symbol': currency_symbol,
            'weight_unit': weight_unit,
            'volume_unit': volume_unit,
            'total_pax_kg':   meta['total_pax_kg'],
            'occupied_seats': meta['occupied_seats'],
        })
    except Exception as e:
        import traceback
        return jsonify({'ok': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

