"""
test_api.py – přímé testy REST API /api/compute (bez prohlížeče).

Definice (weight_balance_rules.md):
  payload    = součet osádky + zavazadla  (pevná hodnota, nezávislá na letadle)
  trip_fuel  = palivo na let A→B
  reserve    = palivo na fuel_reserve_min minut
  FOB        = trip_fuel + reserve
  trip_load  = FOB [kg] + payload [kg]
  podmínka   : useful_load >= trip_load

Používá Flask testovací klient – rychlé unit testy backendu.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as flask_app


@pytest.fixture(scope="module")
def client():
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        yield c


BASE_PARAMS = {
    "avgas_price": 75, "jet_a1_price": 45,
    "avgas_density": 0.72, "jet_a1_density": 0.81,
    "fuel_reserve_min": 30,
    "person_weight_kg": 76, "baggage_per_seat_kg": 5,
    "distance_nm": 200, "wind_kt": 0,
    "eur_to_czk": 24.545, "usd_to_czk": 21.315, "gbp_to_czk": 28.299,
    "pax1_weight": 100, "pax1_baggage": 5,
    "pax2_weight": 65,  "pax2_baggage": 5,
    "pax3_weight": 0,   "pax3_baggage": 0,
    "pax4_weight": 0,   "pax4_baggage": 0,
    "pax5_weight": 0,   "pax5_baggage": 0,
    "pax6_weight": 0,   "pax6_baggage": 0,
}

# payload pro BASE_PARAMS = 100+5 + 65+5 = 175 kg
BASE_PAYLOAD_KG = 175.0


def post(client, params):
    return client.post("/api/compute", json=params)


# ── Základní API ──────────────────────────────────────────────────────────────

def test_api_returns_200(client):
    r = post(client, BASE_PARAMS)
    assert r.status_code == 200


def test_api_returns_ok_true(client):
    data = post(client, BASE_PARAMS).get_json()
    assert data["ok"] is True


def test_api_returns_planes_list(client):
    data = post(client, BASE_PARAMS).get_json()
    assert isinstance(data["planes"], list)
    assert len(data["planes"]) > 0


def test_each_plane_has_required_keys(client):
    data = post(client, BASE_PARAMS).get_json()
    required = {"type", "manufacturer", "designation", "name",
                "no_seats", "fuel_type", "payload_kg",
                "suitable", "max_power", "econ_cruise",
                "currency", "currency_symbol"}
    for plane in data["planes"]:
        missing = required - set(plane.keys())
        assert not missing, f"Letadlo {plane.get('designation')} chybí klíče: {missing}"


def test_max_power_has_required_keys(client):
    data = post(client, BASE_PARAMS).get_json()
    req = {"v_kt", "v_kmh", "ff_lph", "flight_time_h",
           "flight_time_fmt", "trip_fuel_l", "fob_l",
           "trip_load_kg", "load_reserve_kg", "fuel_cost", "total_cost"}
    for plane in data["planes"]:
        mp = plane["max_power"]
        if mp.get("v_kt") is not None:
            missing = req - set(mp.keys())
            assert not missing, f"{plane['designation']} max_power chybí: {missing}"


def test_econ_cruise_has_required_keys(client):
    data = post(client, BASE_PARAMS).get_json()
    req = {"v_kt", "v_kmh", "ff_lph", "flight_time_h",
           "flight_time_fmt", "trip_fuel_l", "fob_l",
           "trip_load_kg", "load_reserve_kg", "fuel_cost", "total_cost"}
    for plane in data["planes"]:
        ec = plane["econ_cruise"]
        if ec.get("v_kt") is not None:
            missing = req - set(ec.keys())
            assert not missing, f"{plane['designation']} econ_cruise chybí: {missing}"


# ── Payload = součet osádky (pevná hodnota) ───────────────────────────────────

def test_payload_equals_crew_total(client):
    """payload_kg = součet všech cestujících + zavazadla (definice)."""
    params = {**BASE_PARAMS,
              "pax1_weight": 80, "pax1_baggage": 10,
              "pax2_weight": 70, "pax2_baggage": 5,
              "pax3_weight": 0,  "pax3_baggage": 0}
    crew_total = 80 + 10 + 70 + 5  # = 165 kg
    data = post(client, params).get_json()
    for plane in data["planes"]:
        assert abs(plane["payload_kg"] - crew_total) < 0.5, (
            f"{plane['designation']}: payload {plane['payload_kg']} ≠ {crew_total}"
        )


def test_payload_same_for_all_planes(client):
    """Payload závisí jen na obsazení, ne na letadle."""
    data = post(client, BASE_PARAMS).get_json()
    payloads = {p["payload_kg"] for p in data["planes"]}
    assert len(payloads) == 1, f"Payload by měl být stejný pro všechna letadla: {payloads}"
    assert abs(next(iter(payloads)) - BASE_PAYLOAD_KG) < 0.5


def test_payload_is_base_crew_weight(client):
    """BASE_PARAMS: payload = 100+5+65+5 = 175 kg."""
    data = post(client, BASE_PARAMS).get_json()
    for plane in data["planes"]:
        assert abs(plane["payload_kg"] - BASE_PAYLOAD_KG) < 0.5


# ── FOB = trip_fuel + reserve ─────────────────────────────────────────────────

def test_fob_greater_than_trip_fuel(client):
    """FOB > trip_fuel – FOB obsahuje rezervu."""
    data = post(client, BASE_PARAMS).get_json()
    found = False
    for plane in data["planes"]:
        ec = plane["econ_cruise"]
        tf = ec.get("trip_fuel_l")
        fob = ec.get("fob_l")
        if tf is not None and fob is not None and tf > 0:
            assert fob > tf, (
                f"{plane['designation']}: FOB {fob} musí být > trip_fuel {tf}"
            )
            found = True
            break
    assert found, "Nenalezeno letadlo s platnými daty"


def test_fob_increases_with_longer_reserve(client):
    """Delší rezerva (45 min) zvyšuje FOB oproti 30 min."""
    r30 = post(client, {**BASE_PARAMS, "fuel_reserve_min": 30}).get_json()
    r45 = post(client, {**BASE_PARAMS, "fuel_reserve_min": 45}).get_json()
    # Indexujeme podle designation aby řazení nevadilo
    by_desig30 = {p["designation"]: p for p in r30["planes"]}
    by_desig45 = {p["designation"]: p for p in r45["planes"]}
    found = False
    for desig, p30 in by_desig30.items():
        p45 = by_desig45.get(desig)
        if not p45:
            continue
        fob30 = p30["econ_cruise"].get("fob_l")
        fob45 = p45["econ_cruise"].get("fob_l")
        if fob30 and fob45 and fob30 > 0:
            assert fob45 > fob30, (
                f"{desig}: FOB(45min)={fob45} ≤ FOB(30min)={fob30}"
            )
            found = True
    assert found, "Nenalezeno letadlo s platnými FOB hodnotami"


# ── trip_load = FOB[kg] + payload[kg] ────────────────────────────────────────

def test_trip_load_equals_fob_kg_plus_payload(client):
    """trip_load_kg = FOB[l]*hustota + payload_kg."""
    data = post(client, BASE_PARAMS).get_json()
    avgas_density = 0.72
    for plane in data["planes"]:
        ec = plane["econ_cruise"]
        tl = ec.get("trip_load_kg")
        fob = ec.get("fob_l")
        payload = plane["payload_kg"]
        if tl is not None and fob is not None and payload is not None:
            fuel_type = plane.get("fuel_type", "")
            density = 0.81 if "JET" in fuel_type.upper() else avgas_density
            expected = round(fob * density + payload, 1)
            assert abs(tl - expected) < 1.0, (
                f"{plane['designation']}: trip_load {tl} ≠ FOB*density+payload = {expected}"
            )
            break


# ── Vhodnost: useful_load >= trip_load ───────────────────────────────────────

def test_suitable_planes_satisfy_trip_load_condition(client):
    """Vhodná letadla: useful_load >= trip_load (EC – konzervativnější)."""
    data = post(client, BASE_PARAMS).get_json()
    for plane in data["planes"]:
        if plane["suitable"]:
            ec = plane["econ_cruise"]
            ul = plane.get("useful_load")
            tl = ec.get("trip_load_kg")
            if ul and tl:
                assert float(ul) >= tl - 0.5, (
                    f"{plane['designation']}: vhodné, ale trip_load {tl} > useful_load {ul}"
                )


def test_overloaded_plane_marked_unsuitable(client):
    """Letadlo přetížené (trip_load > useful_load) je označeno jako nevhodné."""
    heavy = {**BASE_PARAMS,
             **{f"pax{i}_weight": 200 for i in range(1, 7)},
             **{f"pax{i}_baggage": 30  for i in range(1, 7)}}
    data = post(client, heavy).get_json()
    unsuitable = [p for p in data["planes"] if not p["suitable"]]
    assert len(unsuitable) > 0


def test_minimal_crew_gives_suitable_planes(client):
    """Minimální obsazení dává alespoň 1 vhodné letadlo."""
    minimal = {**BASE_PARAMS,
               **{f"pax{i}_weight": 0  for i in range(1, 7)},
               **{f"pax{i}_baggage": 0 for i in range(1, 7)},
               "pax1_weight": 80}
    data = post(client, minimal).get_json()
    suitable = [p for p in data["planes"] if p["suitable"]]
    assert len(suitable) > 0


def test_load_reserve_equals_useful_load_minus_trip_load(client):
    """load_reserve_kg = useful_load - trip_load_kg."""
    data = post(client, BASE_PARAMS).get_json()
    for plane in data["planes"]:
        ec = plane["econ_cruise"]
        lr = ec.get("load_reserve_kg")
        tl = ec.get("trip_load_kg")
        ul = plane.get("useful_load")
        if lr is not None and tl is not None and ul:
            expected = round(float(ul) - tl, 1)
            assert abs(lr - expected) < 0.5, (
                f"{plane['designation']}: load_reserve {lr} ≠ useful_load - trip_load = {expected}"
            )
            break


def test_suitable_planes_have_nonnegative_load_reserve(client):
    """Vhodná letadla mají load_reserve_kg >= 0."""
    data = post(client, BASE_PARAMS).get_json()
    for plane in data["planes"]:
        if plane["suitable"]:
            ec = plane["econ_cruise"]
            lr = ec.get("load_reserve_kg")
            if lr is not None:
                assert lr >= -0.5, (
                    f"{plane['designation']}: vhodné, ale load_reserve = {lr}"
                )


# ── Letové výpočty ────────────────────────────────────────────────────────────

def test_headwind_increases_flight_time(client):
    """Čelní vítr prodlužuje dobu letu oproti klidnému vzduchu."""
    calm     = post(client, {**BASE_PARAMS, "wind_kt":   0}).get_json()
    headwind = post(client, {**BASE_PARAMS, "wind_kt": -50}).get_json()

    found = False
    for c, h in zip(calm["planes"], headwind["planes"]):
        ct = c["max_power"].get("flight_time_h")
        ht = h["max_power"].get("flight_time_h")
        if ct and ht and abs(ct - ht) > 0.001:
            assert ht > ct, f"{c['designation']}: čelní vítr by měl prodloužit let"
            found = True
            break
    assert found, "Nenalezeno letadlo s detekovatelným rozdílem doby letu"


def test_tailwind_decreases_flight_time(client):
    """Zadní vítr zkracuje dobu letu."""
    calm     = post(client, {**BASE_PARAMS, "wind_kt":  0}).get_json()
    tailwind = post(client, {**BASE_PARAMS, "wind_kt": 30}).get_json()

    for c, t in zip(calm["planes"], tailwind["planes"]):
        if (c["max_power"].get("flight_time_h") and
                t["max_power"].get("flight_time_h")):
            assert t["max_power"]["flight_time_h"] < c["max_power"]["flight_time_h"]
            break


def test_higher_fuel_price_increases_cost(client):
    """Vyšší cena paliva zvyšuje náklady."""
    cheap = post(client, {**BASE_PARAMS, "avgas_price": 50}).get_json()
    dear  = post(client, {**BASE_PARAMS, "avgas_price": 100}).get_json()

    for c, d in zip(cheap["planes"], dear["planes"]):
        if (c["econ_cruise"].get("fuel_cost") and
                d["econ_cruise"].get("fuel_cost")):
            assert d["econ_cruise"]["fuel_cost"] > c["econ_cruise"]["fuel_cost"]
            break


def test_longer_distance_increases_trip_fuel(client):
    """Delší vzdálenost zvyšuje trip_fuel."""
    short = post(client, {**BASE_PARAMS, "distance_nm": 100}).get_json()
    long_ = post(client, {**BASE_PARAMS, "distance_nm": 400}).get_json()

    for s, l in zip(short["planes"], long_["planes"]):
        if (s["econ_cruise"].get("trip_fuel_l") and
                l["econ_cruise"].get("trip_fuel_l")):
            assert l["econ_cruise"]["trip_fuel_l"] > s["econ_cruise"]["trip_fuel_l"]
            break


def test_longer_distance_increases_fob(client):
    """Delší vzdálenost zvyšuje FOB (trip_fuel + reserve)."""
    short = post(client, {**BASE_PARAMS, "distance_nm": 100}).get_json()
    long_ = post(client, {**BASE_PARAMS, "distance_nm": 400}).get_json()

    for s, l in zip(short["planes"], long_["planes"]):
        if (s["econ_cruise"].get("fob_l") and l["econ_cruise"].get("fob_l")):
            assert l["econ_cruise"]["fob_l"] > s["econ_cruise"]["fob_l"]
            break


def test_flight_time_fmt_format(client):
    """Formát doby letu odpovídá Xh YYm."""
    import re
    data = post(client, BASE_PARAMS).get_json()
    pattern = re.compile(r"^\d+h \d{2}m$")
    for plane in data["planes"]:
        fmt = plane["econ_cruise"].get("flight_time_fmt")
        if fmt and fmt != "–":
            assert pattern.match(fmt), f"Špatný formát: {fmt!r}"


# ── Testy měny ────────────────────────────────────────────────────────────────

def test_default_currency_is_czk(client):
    """Bez zadání currency je výchozí CZK."""
    data = post(client, BASE_PARAMS).get_json()
    assert data["currency"] == "CZK"
    assert data["currency_symbol"] == "Kč"
    for plane in data["planes"]:
        assert plane["currency"] == "CZK"
        assert plane["currency_symbol"] == "Kč"


@pytest.mark.parametrize("currency,symbol", [
    ("EUR", "€"),
    ("USD", "$"),
    ("GBP", "£"),
    ("CZK", "Kč"),
])
def test_currency_symbol_returned(client, currency, symbol):
    """API vrátí správný symbol pro každou měnu."""
    data = post(client, {**BASE_PARAMS, "currency": currency}).get_json()
    assert data["ok"] is True
    assert data["currency"] == currency
    assert data["currency_symbol"] == symbol


def test_eur_costs_lower_than_czk(client):
    """Náklady v EUR jsou menší než v CZK (kurz < 1)."""
    czk_data = post(client, {**BASE_PARAMS, "currency": "CZK"}).get_json()
    eur_data = post(client, {**BASE_PARAMS, "currency": "EUR", "eur_to_czk": 24.545}).get_json()

    for c, e in zip(czk_data["planes"], eur_data["planes"]):
        ct = c["econ_cruise"].get("total_cost")
        et = e["econ_cruise"].get("total_cost")
        if ct and et:
            assert et < ct, f"{c['designation']}: EUR {et} musí být < CZK {ct}"
            break


def test_custom_exchange_rate_applied(client):
    """Vlastní kurz 1 EUR = 10 CZK dá vyšší EUR cenu než 1 EUR = 24.545 CZK."""
    default_eur = post(client, {**BASE_PARAMS, "currency": "EUR", "eur_to_czk": 24.545}).get_json()
    cheap_eur   = post(client, {**BASE_PARAMS, "currency": "EUR", "eur_to_czk": 10.0}).get_json()

    for d, c in zip(default_eur["planes"], cheap_eur["planes"]):
        dt = d["econ_cruise"].get("total_cost")
        ct = c["econ_cruise"].get("total_cost")
        if dt and ct:
            assert ct > dt, "Kurz 1EUR=10CZK → vyšší EUR cena než kurz 1EUR=24.545CZK"
            break


def test_unknown_currency_falls_back_to_czk(client):
    """Neznámá měna se tiše přepadne na CZK."""
    data = post(client, {**BASE_PARAMS, "currency": "YEN"}).get_json()
    assert data["ok"] is True
    assert data["currency"] == "CZK"


# ── API metadata: total_pax_kg a occupied_seats ───────────────────────────────

def test_api_returns_total_pax_kg(client):
    """API response obsahuje top-level klíč total_pax_kg."""
    data = post(client, BASE_PARAMS).get_json()
    assert "total_pax_kg" in data, "API musí vracet total_pax_kg v top-level response"


def test_api_total_pax_kg_matches_crew(client):
    """total_pax_kg v response odpovídá součtu osádky z formuláře."""
    params = {**BASE_PARAMS,
              "pax1_weight": 100, "pax1_baggage": 5,
              "pax2_weight": 65,  "pax2_baggage": 5,
              "pax3_weight": 0,   "pax3_baggage": 0}
    # 100+5+65+5 = 175 kg
    data = post(client, params).get_json()
    assert abs(data["total_pax_kg"] - 175.0) < 0.5, (
        f"Očekáváno 175, dostali jsme {data['total_pax_kg']}"
    )


def test_api_total_pax_kg_updates_with_crew_change(client):
    """Při zvýšení hmotnosti osádky na 220 kg API vrátí 220 v total_pax_kg."""
    params = {**BASE_PARAMS,
              "pax1_weight": 120, "pax1_baggage": 5,
              "pax2_weight": 65,  "pax2_baggage": 5,
              "pax3_weight": 20,  "pax3_baggage": 5}
    # 120+5+65+5+20+5 = 220 kg
    expected = 120 + 5 + 65 + 5 + 20 + 5
    data = post(client, params).get_json()
    assert abs(data["total_pax_kg"] - expected) < 0.5, (
        f"Očekáváno {expected} kg, dostali jsme {data['total_pax_kg']}"
    )
    # payload_kg v letadlech musí souhlasit s total_pax_kg
    for plane in data["planes"]:
        assert abs(plane["payload_kg"] - expected) < 0.5, (
            f"{plane['designation']}: payload_kg {plane['payload_kg']} ≠ {expected}"
        )


def test_api_returns_occupied_seats(client):
    """API response obsahuje top-level klíč occupied_seats."""
    data = post(client, BASE_PARAMS).get_json()
    assert "occupied_seats" in data, "API musí vracet occupied_seats v top-level response"


def test_api_occupied_seats_pilot_and_one_pax(client):
    """BASE_PARAMS: pilot + 1 PAX → occupied_seats = 2."""
    data = post(client, BASE_PARAMS).get_json()
    assert data["occupied_seats"] == 2, (
        f"Očekáváno 2 obsazená sedadla, dostali jsme {data['occupied_seats']}"
    )


def test_api_occupied_seats_three_pax(client):
    """Tři obsazení cestující → occupied_seats = 3."""
    params = {**BASE_PARAMS,
              "pax3_weight": 75, "pax3_baggage": 5}
    data = post(client, params).get_json()
    assert data["occupied_seats"] == 3, (
        f"Očekáváno 3 obsazená sedadla, dostali jsme {data['occupied_seats']}"
    )


def test_api_occupied_seats_only_pilot(client):
    """Pouze pilot → occupied_seats = 1."""
    params = {**BASE_PARAMS,
              "pax2_weight": 0, "pax2_baggage": 0}
    data = post(client, params).get_json()
    assert data["occupied_seats"] == 1


# ── occupied_seats jako podmínka nevhodnosti ──────────────────────────────────

def test_unsuitable_when_seats_exceeded(client):
    """Letadlo s méně sedadly než occupied_seats musí být označeno jako nevhodné."""
    # Obsadíme 6 sedadel – každé jednomístné i dvoumístné letadlo bude nevhodné
    params = {**BASE_PARAMS,
              "pax1_weight": 80, "pax1_baggage": 5,
              "pax2_weight": 80, "pax2_baggage": 5,
              "pax3_weight": 80, "pax3_baggage": 5,
              "pax4_weight": 80, "pax4_baggage": 5,
              "pax5_weight": 80, "pax5_baggage": 5,
              "pax6_weight": 80, "pax6_baggage": 5}
    data = post(client, params).get_json()
    for plane in data["planes"]:
        no_seats = plane.get("no_seats") or 0
        if no_seats < 6:
            assert not plane["suitable"], (
                f"{plane['designation']} ({no_seats} sedadel, 6 obsazeno) "
                f"musí být nevhodné, ale suitable={plane['suitable']}"
            )
            assert "sedadel" in plane.get("unsuitable_reason", "").lower() or \
                   "seat" in plane.get("unsuitable_reason", "").lower() or \
                   str(6) in plane.get("unsuitable_reason", ""), (
                f"{plane['designation']}: chybí zmínka o sedadlech v důvodu: "
                f"{plane.get('unsuitable_reason')}"
            )


def test_suitable_when_enough_seats(client):
    """Letadlo s dostatkem sedadel pro osádku je vhodné (z pohledu sedadel)."""
    params = {**BASE_PARAMS,
              "pax2_weight": 0, "pax2_baggage": 0}
    data = post(client, params).get_json()
    for plane in data["planes"]:
        no_seats = plane.get("no_seats") or 0
        if no_seats >= 1:
            reason = plane.get("unsuitable_reason", "")
            assert "sedadel" not in reason.lower() or "kapacita 1" not in reason, (
                f"{plane['designation']}: letadlo má dost sedadel ({no_seats}≥1), "
                f"ale je nevhodné kvůli sedadlům: {reason}"
            )


# ── fail_seats a fail_load flagy pro granulární označení v tabulce ────────────

def test_fail_seats_flag_set_when_seats_exceeded(client):
    """fail_seats=True pokud occupied_seats > no_seats letadla."""
    params = {**BASE_PARAMS,
              "pax1_weight": 80, "pax1_baggage": 5,
              "pax2_weight": 80, "pax2_baggage": 5,
              "pax3_weight": 80, "pax3_baggage": 5,
              "pax4_weight": 80, "pax4_baggage": 5,
              "pax5_weight": 80, "pax5_baggage": 5,
              "pax6_weight": 80, "pax6_baggage": 5}
    data = post(client, params).get_json()
    for plane in data["planes"]:
        no_seats = plane.get("no_seats") or 0
        if no_seats < 6:
            assert plane.get("fail_seats") is True, (
                f"{plane['designation']} ({no_seats} sedadel, 6 obsazeno): "
                f"očekáváno fail_seats=True"
            )


def test_fail_seats_false_when_enough_seats(client):
    """fail_seats=False pokud letadlo má dost sedadel."""
    # 1 pilot – letadla s ≥1 sedadlem nemají fail_seats
    params = {**BASE_PARAMS,
              "pax2_weight": 0, "pax2_baggage": 0}
    data = post(client, params).get_json()
    for plane in data["planes"]:
        no_seats = plane.get("no_seats") or 0
        if no_seats >= 1:
            assert plane.get("fail_seats") is False, (
                f"{plane['designation']} ({no_seats} sedadel, 1 obsazeno): "
                f"očekáváno fail_seats=False"
            )


def test_fail_load_flag_set_when_overloaded(client):
    """fail_load=True pokud trip_load > useful_load."""
    # Extrémně těžká osádka – většina letadel bude přetížená
    heavy = {**BASE_PARAMS,
             "pax1_weight": 300, "pax1_baggage": 100,
             "pax2_weight": 300, "pax2_baggage": 100}
    data = post(client, heavy).get_json()
    overloaded = [p for p in data["planes"] if p.get("fail_load")]
    assert len(overloaded) > 0, "S extrémně těžkou osádkou musí být alespoň jedno letadlo fail_load=True"
    for p in overloaded:
        assert not p["suitable"], f"{p['designation']}: fail_load=True ale suitable=True"


def test_fail_load_false_when_light_crew(client):
    """fail_load=False pro velmi lehkou osádku."""
    light = {**BASE_PARAMS,
             "pax1_weight": 50, "pax1_baggage": 0,
             "pax2_weight": 0,  "pax2_baggage": 0}
    data = post(client, light).get_json()
    for plane in data["planes"]:
        assert plane.get("fail_load") is False, (
            f"{plane['designation']}: lehká osádka, očekáváno fail_load=False, "
            f"dostali jsme {plane.get('fail_load')}"
        )


def test_fail_flags_independent(client):
    """fail_seats a fail_load jsou nezávislé – mohou být oba True zároveň."""
    # 6 těžkých pasažérů – pravděpodobně oba fail zároveň u malých letadel
    params = {**BASE_PARAMS,
              "pax1_weight": 200, "pax1_baggage": 50,
              "pax2_weight": 200, "pax2_baggage": 50,
              "pax3_weight": 200, "pax3_baggage": 50,
              "pax4_weight": 200, "pax4_baggage": 50,
              "pax5_weight": 200, "pax5_baggage": 50,
              "pax6_weight": 200, "pax6_baggage": 50}
    data = post(client, params).get_json()
    both_fail = [p for p in data["planes"]
                 if p.get("fail_seats") and p.get("fail_load")]
    # U letadel s <6 sedadly a malou užitnou zátěží musí být oba fail True
    assert len(both_fail) > 0, (
        "S 6 velmi těžkými pasažéry musí existovat letadlo s fail_seats=True i fail_load=True"
    )
    for p in both_fail:
        assert not p["suitable"], f"{p['designation']}: oba fail True, ale suitable=True"


def test_each_plane_has_fail_flags(client):
    """Každé letadlo v response musí mít klíče fail_seats, fail_load, fail_load_mp, fail_load_ec."""
    data = post(client, BASE_PARAMS).get_json()
    for plane in data["planes"]:
        for key in ("fail_seats", "fail_load", "fail_load_mp", "fail_load_ec"):
            assert key in plane, f"{plane.get('designation')}: chybí {key}"
            assert isinstance(plane[key], bool), f"{plane.get('designation')}: {key} musí být bool"


# ── fail_load_mp / fail_load_ec – granulární flagy pro každý profil ───────────

def test_fail_load_mp_independent_of_ec(client):
    """
    Bristell RG při 220 NM: MP nevyhovuje (fail_load_mp=True),
    ale EC vyhovuje (fail_load_ec=False).
    Ověřuje že flagy jsou na sobě nezávislé.
    """
    params = {**BASE_PARAMS,
              "distance_nm": 220,
              "pax1_weight": 100, "pax1_baggage": 5,
              "pax2_weight": 65,  "pax2_baggage": 5,
              "pax3_weight": 0,   "pax3_baggage": 0,
              "pax4_weight": 0,   "pax4_baggage": 0,
              "pax5_weight": 0,   "pax5_baggage": 0,
              "pax6_weight": 0,   "pax6_baggage": 0}
    data = post(client, params).get_json()
    rg = next((p for p in data["planes"] if p["designation"] == "RG"), None)
    assert rg is not None, "Bristell RG nenalezen v tabulce"
    assert rg["fail_load_mp"] is True,  f"Bristell RG 220NM: očekáváno fail_load_mp=True, got {rg['fail_load_mp']}"
    assert rg["fail_load_ec"] is False, f"Bristell RG 220NM: očekáváno fail_load_ec=False, got {rg['fail_load_ec']}"


def test_fail_load_both_when_very_heavy(client):
    """Extrémně těžká osádka → fail_load_mp=True i fail_load_ec=True pro malá letadla."""
    params = {**BASE_PARAMS,
              "pax1_weight": 300, "pax1_baggage": 100,
              "pax2_weight": 300, "pax2_baggage": 100}
    data = post(client, params).get_json()
    both = [p for p in data["planes"] if p.get("fail_load_mp") and p.get("fail_load_ec")]
    assert len(both) > 0, "S extrémní osádkou musí mít aspoň jedno letadlo oba fail_load flagy True"
    for p in both:
        assert p["fail_load"] is True
        assert p["suitable"] is False


def test_fail_load_false_both_when_light(client):
    """Lehká osádka → fail_load_mp=False a fail_load_ec=False pro vhodná letadla."""
    params = {**BASE_PARAMS,
              "pax1_weight": 50, "pax1_baggage": 0,
              "pax2_weight": 0,  "pax2_baggage": 0}
    data = post(client, params).get_json()
    for plane in data["planes"]:
        if plane["suitable"]:
            assert plane["fail_load_mp"] is False, \
                f"{plane['designation']}: suitable=True ale fail_load_mp=True"
            assert plane["fail_load_ec"] is False, \
                f"{plane['designation']}: suitable=True ale fail_load_ec=False"


def test_fail_load_consistency(client):
    """fail_load = fail_load_mp OR fail_load_ec (logická konzistence)."""
    data = post(client, BASE_PARAMS).get_json()
    for plane in data["planes"]:
        expected = plane["fail_load_mp"] or plane["fail_load_ec"]
        assert plane["fail_load"] == expected, (
            f"{plane['designation']}: fail_load={plane['fail_load']} != "
            f"fail_load_mp({plane['fail_load_mp']}) OR fail_load_ec({plane['fail_load_ec']})"
        )


# ── annual_hours – vliv na hodinové náklady letadla ───────────────────────────

def test_plane_cost_ph_uses_annual_hours(client):
    """
    Zdvojnásobení annual_hours na 160 h/rok sníží plane_cost_ph na polovinu.
    plane_cost_ph = (fixed + variable) / annual_hours
    """
    r80  = post(client, {**BASE_PARAMS, "annual_hours": 80}).get_json()
    r160 = post(client, {**BASE_PARAMS, "annual_hours": 160}).get_json()
    found = False
    for p80, p160 in zip(r80["planes"], r160["planes"]):
        cp80  = p80["hour_rates"].get("plane_cost_ph")
        cp160 = p160["hour_rates"].get("plane_cost_ph")
        if cp80 and cp160:
            assert abs(cp80 / 2 - cp160) < 1.0, (
                f"{p80['designation']}: při 2× více hodinách by plane_cost_ph měl být poloviční. "
                f"80h={cp80}, 160h={cp160}"
            )
            found = True
            break
    assert found, "Nenalezeno letadlo s platnými hour_rates"


def test_annual_hours_affects_total_cost_per_flight(client):
    """
    Více nalétaných hodin ročně → nižší plane_cost_ph → nižší total_cost na let.
    """
    r80  = post(client, {**BASE_PARAMS, "annual_hours":  80}).get_json()
    r200 = post(client, {**BASE_PARAMS, "annual_hours": 200}).get_json()
    for p80, p200 in zip(r80["planes"], r200["planes"]):
        tc80  = p80["econ_cruise"].get("total_cost")
        tc200 = p200["econ_cruise"].get("total_cost")
        if tc80 and tc200:
            assert tc200 < tc80, (
                f"{p80['designation']}: více hodin ročně → levnější let. "
                f"80h={tc80}, 200h={tc200}"
            )
            break


def test_annual_hours_default_is_80(client):
    """Bez parametru annual_hours se použije výchozí 80 h/rok."""
    with_default = post(client, BASE_PARAMS).get_json()           # bez annual_hours
    with_80      = post(client, {**BASE_PARAMS, "annual_hours": 80}).get_json()
    for pd_, p80 in zip(with_default["planes"], with_80["planes"]):
        cp_def = pd_["hour_rates"].get("plane_cost_ph")
        cp_80  = p80["hour_rates"].get("plane_cost_ph")
        if cp_def and cp_80:
            assert abs(cp_def - cp_80) < 0.01, (
                f"{pd_['designation']}: výchozí annual_hours by mělo být 80. "
                f"default={cp_def}, 80h={cp_80}"
            )
            break


def test_annual_hours_minimum_1(client):
    """annual_hours=0 se ošetří na minimum 1 h (bez dělení nulou)."""
    data = post(client, {**BASE_PARAMS, "annual_hours": 0}).get_json()
    assert data["ok"] is True, "annual_hours=0 nesmí způsobit chybu serveru"
    for plane in data["planes"]:
        cp = plane["hour_rates"].get("plane_cost_ph")
        if cp is not None:
            assert cp > 0, f"{plane['designation']}: plane_cost_ph musí být > 0"


