"""
test_units.py – Playwright testy pro přepínače jednotek váhy a objemu.

Ověřuje:
- přepínač váhy (kg / lb) je přítomen na kartě Obecné
- přepínač objemu (litr / US gal / Imp gal) je přítomen na kartě Obecné
- výchozí jednotky jsou kg a litr
- záhlaví tabulky se aktualizuje po přepnutí
- hodnoty v buňkách se převedou (lb = kg × 2.20462; US gal = l × 0.264172; Imp gal = l × 0.219969)
- přepnutí zpět na kg/l obnoví původní hodnoty
"""
import re
import pytest

KG_TO_LB  = 2.20462
L_TO_USG  = 0.264172
L_TO_IMG  = 0.219969

COMPUTED_JS = "() => document.getElementById('status-bar').textContent.length > 30"


def _wait_computed(page, timeout=10_000):
    page.wait_for_function(COMPUTED_JS, timeout=timeout)


def _click_and_wait(page, timeout=10_000):
    page.evaluate("() => { document.getElementById('status-bar').textContent = ''; }")
    page.locator("#btn-compute").click()
    page.wait_for_function(COMPUTED_JS, timeout=timeout)


def _go_general(page):
    page.locator(".tab-btn", has_text="Obecné").click()


def _select_unit(page, name: str, value: str):
    """Klikne na radio button jednotky (name = weight_unit / volume_unit)."""
    page.evaluate(
        "([n,v]) => { const el = document.querySelector(`input[name='${n}'][value='${v}']`); if(el) el.click(); }",
        [name, value]
    )
    page.wait_for_timeout(150)


def _header_texts(page, selector: str) -> list:
    return page.locator(selector).all_inner_texts()


def _first_row_col(page, td_index: int) -> str:
    """Vrátí text buňky (1-based index) prvního vhodného řádku."""
    return page.evaluate(
        f"""() => {{
            const rows = [...document.querySelectorAll('#table-body tr:not(.unsuitable)')];
            if (!rows.length) return '';
            const tds = rows[0].querySelectorAll('td');
            return tds[{td_index - 1}] ? tds[{td_index - 1}].innerText : '';
        }}"""
    )


def _parse_num(text: str) -> float:
    """Parsuje číslo z lokalizovaného stringu (cs-CZ: mezera jako oddělovač tisíců, čárka jako des. tečka)."""
    clean = re.sub(r'[^\d,]', '', text).replace(',', '.')
    parts = clean.split('.')
    if len(parts) > 2:
        clean = ''.join(parts[:-1]) + '.' + parts[-1]
    return float(clean) if clean else 0.0


# ── Přítomnost sliderů ─────────────────────────────────────────────────────────

def test_weight_slider_present(page):
    """Slider váhy je přítomen na kartě Obecné."""
    _go_general(page)
    assert page.locator("#weight-slider").is_visible()


def test_volume_slider_present(page):
    """Slider objemu je přítomen na kartě Obecné."""
    _go_general(page)
    assert page.locator("#volume-slider").is_visible()


def test_weight_slider_options(page):
    """Slider váhy má možnosti kg a lb."""
    labels = page.locator("#weight-slider label").all_inner_texts()
    assert labels == ["kg", "lb"]


def test_volume_slider_options(page):
    """Slider objemu má možnosti litr, US gal, Imp gal."""
    labels = page.locator("#volume-slider label").all_inner_texts()
    assert labels == ["litr", "US gal", "Imp gal"]


def test_both_sliders_in_general_tab(page):
    """Oba slidery jsou v kartě Obecné."""
    assert page.locator("#tab-general #weight-slider").count() == 1
    assert page.locator("#tab-general #volume-slider").count() == 1


# ── Výchozí stav ───────────────────────────────────────────────────────────────

def test_default_weight_unit_kg(page):
    """Výchozí jednotka váhy je kg."""
    val = page.evaluate(
        "() => document.querySelector('input[name=\"weight_unit\"]:checked')?.value"
    )
    assert val == "kg"


def test_default_volume_unit_l(page):
    """Výchozí jednotka objemu je litr."""
    val = page.evaluate(
        "() => document.querySelector('input[name=\"volume_unit\"]:checked')?.value"
    )
    assert val == "l"


def test_default_wt_headers_kg(page):
    """Záhlaví hmotnostních sloupců výchozně obsahuje 'kg'."""
    texts = _header_texts(page, ".wt-unit")
    assert all(t == "kg" for t in texts), f"Očekáváno 'kg', dostáno: {texts}"


def test_default_vol_headers_l(page):
    """Záhlaví objemových sloupců výchozně obsahuje 'l'."""
    texts = _header_texts(page, ".vol-unit")
    assert all(t == "l" for t in texts), f"Očekáváno 'l', dostáno: {texts}"


# ── Záhlaví po přepnutí ────────────────────────────────────────────────────────

def test_lb_header_after_switch(page):
    """Po přepnutí na lb záhlaví obsahuje 'lb'."""
    _select_unit(page, "weight_unit", "lb")
    texts = _header_texts(page, ".wt-unit")
    assert all(t == "lb" for t in texts)


def test_usg_header_after_switch(page):
    """Po přepnutí na US gal záhlaví obsahuje 'US gal'."""
    _select_unit(page, "volume_unit", "usg")
    texts = _header_texts(page, ".vol-unit")
    assert all(t == "US gal" for t in texts)


def test_img_header_after_switch(page):
    """Po přepnutí na Imp gal záhlaví obsahuje 'Imp gal'."""
    _select_unit(page, "volume_unit", "img")
    texts = _header_texts(page, ".vol-unit")
    assert all(t == "Imp gal" for t in texts)


def test_back_to_kg_header(page):
    """Návrat na kg záhlaví zobrazí 'kg'."""
    _select_unit(page, "weight_unit", "lb")
    _select_unit(page, "weight_unit", "kg")
    texts = _header_texts(page, ".wt-unit")
    assert all(t == "kg" for t in texts)


# ── Numerická správnost hodnot v tabulce ──────────────────────────────────────
# Sloupce (1-based): 7=MTOW, 8=fuel_cap_l, 9=useful_load
# (sloupec Payload byl odebrán z tabulky – zobrazuje se v action-baru)
# MP: 10=load_reserve, 11=V, 12=Spotr, 13=FOB, 14=mp_trip_fuel_l(palivo)

def test_lb_values_larger_than_kg(page):
    """Hodnoty hmotností v lb jsou ~2.2× větší než v kg."""
    # kg hodnota
    _select_unit(page, "weight_unit", "kg")
    kg_text = _first_row_col(page, 7)

    # lb hodnota
    _select_unit(page, "weight_unit", "lb")
    lb_text = _first_row_col(page, 7)

    kg_val = _parse_num(kg_text)
    lb_val = _parse_num(lb_text)
    assert kg_val > 0 and lb_val > 0, f"kg={kg_text!r}, lb={lb_text!r}"
    ratio = lb_val / kg_val
    assert abs(ratio - KG_TO_LB) < 0.01, f"Poměr lb/kg = {ratio:.4f}, očekáváno {KG_TO_LB}"


def test_usg_values_smaller_than_l(page):
    """Hodnoty objemu v US gal jsou ~0.264× hodnot v litrech."""
    _select_unit(page, "volume_unit", "l")
    l_text = _first_row_col(page, 14)   # mp_trip_fuel_l

    _select_unit(page, "volume_unit", "usg")
    usg_text = _first_row_col(page, 14)

    l_val   = _parse_num(l_text)
    usg_val = _parse_num(usg_text)
    assert l_val > 0 and usg_val > 0, f"l={l_text!r}, usg={usg_text!r}"
    ratio = usg_val / l_val
    assert abs(ratio - L_TO_USG) < 0.005, f"Poměr usg/l = {ratio:.4f}, očekáváno {L_TO_USG}"


def test_img_values_smaller_than_l(page):
    """Hodnoty objemu v Imp gal jsou ~0.22× hodnot v litrech."""
    _select_unit(page, "volume_unit", "l")
    l_val = _parse_num(_first_row_col(page, 14))

    _select_unit(page, "volume_unit", "img")
    img_val = _parse_num(_first_row_col(page, 14))

    assert l_val > 0 and img_val > 0
    ratio = img_val / l_val
    assert abs(ratio - L_TO_IMG) < 0.005, f"Poměr img/l = {ratio:.4f}, očekáváno {L_TO_IMG}"


def test_back_to_l_restores_values(page):
    """Návrat na litr obnoví původní hodnoty."""
    _select_unit(page, "volume_unit", "l")
    l_val_1 = _parse_num(_first_row_col(page, 14))

    _select_unit(page, "volume_unit", "usg")
    _select_unit(page, "volume_unit", "l")
    l_val_2 = _parse_num(_first_row_col(page, 14))

    assert abs(l_val_1 - l_val_2) < 0.1, f"Po návratu na l: {l_val_1} ≠ {l_val_2}"


# ── Kombinace jednotek ─────────────────────────────────────────────────────────

def test_lb_and_usg_simultaneously(page):
    """Kombinace lb + US gal zobrazí správné záhlaví pro oba."""
    _select_unit(page, "weight_unit", "lb")
    _select_unit(page, "volume_unit", "usg")
    wt_texts  = _header_texts(page, ".wt-unit")
    vol_texts = _header_texts(page, ".vol-unit")
    assert all(t == "lb" for t in wt_texts)
    assert all(t == "US gal" for t in vol_texts)


def test_compute_with_lb_input_works(page):
    """Výpočet funguje i po přepnutí na lb (tabulka se naplní)."""
    _select_unit(page, "weight_unit", "lb")
    _click_and_wait(page)
    assert page.locator("#table-body tr:not(.unsuitable)").count() >= 1

