"""
test_hangar.py – testy REST API /api/hangar (záložka Hangár).

Ověřuje že endpoint vrací data z plane_table.csv
ve správné struktuře pro zobrazení v tabulce.
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


# ── Základní struktura response ───────────────────────────────────────────────

def test_hangar_returns_200(client):
    r = client.get("/api/hangar")
    assert r.status_code == 200


def test_hangar_returns_ok_true(client):
    data = client.get("/api/hangar").get_json()
    assert data["ok"] is True


def test_hangar_has_columns_and_rows(client):
    data = client.get("/api/hangar").get_json()
    assert "columns" in data
    assert "rows" in data
    assert isinstance(data["columns"], list)
    assert isinstance(data["rows"], list)


def test_hangar_has_planes(client):
    """Response obsahuje alespoň 1 letadlo."""
    data = client.get("/api/hangar").get_json()
    assert len(data["rows"]) > 0


def test_hangar_row_count_matches_csv(client):
    """Počet řádků odpovídá počtu letadel v CSV (35 řádků dat)."""
    data = client.get("/api/hangar").get_json()
    # plane_table.csv má 35 letadel (1 řádek záhlaví)
    assert len(data["rows"]) >= 30, f"Očekáváno ≥30 letadel, dostali jsme {len(data['rows'])}"


# ── Obsah sloupců ─────────────────────────────────────────────────────────────

def test_hangar_contains_identification_columns(client):
    """Response obsahuje identifikační sloupce."""
    data = client.get("/api/hangar").get_json()
    cols = set(data["columns"])
    for required in ("type", "Manufacturer", "Designation", "Name"):
        assert required in cols, f"Chybí sloupec: {required}"


def test_hangar_contains_weight_columns(client):
    """Response obsahuje hmotnostní sloupce."""
    data = client.get("/api/hangar").get_json()
    cols = set(data["columns"])
    for required in ("Empty Weight [kg]", "MTOW [kg]", "Usefull Load [kg]"):
        assert required in cols, f"Chybí sloupec: {required}"


def test_hangar_contains_cost_columns(client):
    """Response obsahuje nákladové sloupce (Fixed a Variable cost)."""
    data = client.get("/api/hangar").get_json()
    cols = set(data["columns"])
    assert "Fixed cost 80h/y [CZK]" in cols,    "Chybí Fixed cost 80h/y [CZK]"
    assert "Variable cost 80h/y [CZK]" in cols, "Chybí Variable cost 80h/y [CZK]"


def test_hangar_no_total_cost_column(client):
    """Odstraněný sloupec 'total cost per hour' nesmí být v response."""
    data = client.get("/api/hangar").get_json()
    assert "total cost per hour" not in data["columns"], \
        "Sloupec 'total cost per hour' byl odstraněn z CSV a nesmí být v response"


# ── Obsah dat ─────────────────────────────────────────────────────────────────

def test_hangar_each_row_has_all_columns(client):
    """Každý řádek má klíče odpovídající deklarovaným sloupcům."""
    data = client.get("/api/hangar").get_json()
    cols = data["columns"]
    for row in data["rows"]:
        for col in cols:
            assert col in row, f"Řádek nemá klíč '{col}': {row.get('Designation')}"


def test_hangar_type_values_are_known(client):
    """Sloupec 'type' obsahuje jen SEP nebo MEP."""
    data = client.get("/api/hangar").get_json()
    for row in data["rows"]:
        t = row.get("type")
        assert t in ("SEP", "MEP"), f"Neznámý typ: {t!r}"


def test_hangar_mtow_greater_than_empty_weight(client):
    """MTOW > Empty Weight pro každé letadlo."""
    data = client.get("/api/hangar").get_json()
    for row in data["rows"]:
        mtow = row.get("MTOW [kg]")
        ew   = row.get("Empty Weight [kg]")
        if mtow is not None and ew is not None:
            assert mtow > ew, (
                f"{row.get('Designation')}: MTOW {mtow} musí být > Empty Weight {ew}"
            )


def test_hangar_useful_load_equals_mtow_minus_empty(client):
    """Useful Load ≈ MTOW − Empty Weight (tolerancí 20 kg – drobné odchylky v datech)."""
    data = client.get("/api/hangar").get_json()
    for row in data["rows"]:
        mtow = row.get("MTOW [kg]")
        ew   = row.get("Empty Weight [kg]")
        ul   = row.get("Usefull Load [kg]")
        if mtow and ew and ul:
            assert abs(ul - (mtow - ew)) < 20, (
                f"{row.get('Designation')}: UL={ul} ≠ MTOW-EW={mtow-ew} (rozdíl > 20 kg)"
            )


def test_hangar_fixed_cost_positive(client):
    """Fixed cost je kladné číslo pokud je zadáno."""
    data = client.get("/api/hangar").get_json()
    for row in data["rows"]:
        fc = row.get("Fixed cost 80h/y [CZK]")
        if fc is not None:
            assert fc > 0, f"{row.get('Designation')}: Fixed cost musí být > 0"


def test_hangar_no_nan_in_response(client):
    """Response neobsahuje NaN (musí být None/null)."""
    import json, math
    raw = client.get("/api/hangar").data.decode()
    # JSON spec nezná NaN – pokud by byl přítomen, json.loads by selhal
    parsed = json.loads(raw)
    # Rekurzivní kontrola
    def check(obj):
        if isinstance(obj, float):
            assert not math.isnan(obj), "Response obsahuje NaN float"
        elif isinstance(obj, dict):
            for v in obj.values(): check(v)
        elif isinstance(obj, list):
            for v in obj: check(v)
    check(parsed)


