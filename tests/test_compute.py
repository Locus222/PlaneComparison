"""
test_compute.py – testy výpočtu a zobrazení výsledků v tabulce.

Ověřuje:
- úvodní auto-výpočet naplní tabulku řádky
- po stisknutí Vypočítat se tabulka aktualizuje
- souhrn pod tabulkou zobrazuje počet letadel
- nejlevnější letadlo je zvýrazněno (best-row)
- sloupce Doba letu mají správný formát h:mm
- při krátkém dosahu nejsou viditelná varování pro krátkou vzdálenost
"""
import re
import pytest


COMPUTED_JS = "() => document.getElementById('status-bar').textContent.length > 30"


def _wait_computed(page, timeout=8_000):
    """Počká, až proběhne výpočet (status-bar má text > 30 znaků)."""
    page.wait_for_function(COMPUTED_JS, timeout=timeout)


def test_table_has_rows_after_load(page):
    """Tabulka po načtení obsahuje alespoň 5 řádků."""
    rows = page.locator("#table-body tr:not(.unsuitable)")
    assert rows.count() >= 5


def test_compute_button_triggers_update(page):
    """Kliknutí na Vypočítat aktualizuje status-bar."""
    page.locator("#btn-compute").click()
    _wait_computed(page)
    status = page.locator("#status-bar").inner_text()
    assert len(status) > 30


def test_summary_bar_shows_count(page):
    """Souhrn zobrazuje 'vhodných'."""
    text = page.locator("#sum-count").inner_text()
    assert "vhodn" in text


def test_best_row_highlighted(page):
    """Nejlevnější vhodné letadlo má třídu best-row."""
    assert page.locator("#table-body tr.best-row").count() == 1


def test_flight_time_format(page):
    """Doba letu je ve formátu Xh YYm."""
    cell = page.locator("#table-body tr:not(.unsuitable) td:nth-child(17)").first
    text = cell.inner_text()
    if text != "–":
        assert re.match(r"\d+h \d{2}m", text), f"Neočekávaný formát doby letu: {text!r}"


def test_cheapest_summary_shown(page):
    """Souhrn obsahuje text 'Nejlevn'."""
    assert "Nejlevn" in page.locator("#sum-cheapest").inner_text()


def test_fastest_summary_shown(page):
    """Souhrn obsahuje text 'Nejrychlej'."""
    assert "Nejrychlej" in page.locator("#sum-fastest").inner_text()


def test_short_distance_no_range_warning(page):
    """Pro velmi krátkou vzdálenost (10 NM) nejsou žádná ⚠ varování dosahu."""
    page.locator(".tab-btn", has_text="Pl" ).click()   # Plán tab
    page.locator("#distance_nm").fill("10")
    page.locator("#distance_nm").dispatch_event("input")
    page.locator("#btn-compute").click()
    _wait_computed(page)
    warnings = page.locator(".range-warn")
    assert warnings.count() == 0


def test_long_distance_triggers_range_warning(page):
    """Pro velmi dlouhou vzdálenost (2000 NM) se u některých letadel objeví ⚠ (FOB > kapacita nádrže)."""
    page.locator(".tab-btn", has_text="Pl").click()   # Plán tab
    page.locator("#distance_nm").fill("2000")
    page.locator("#distance_nm").dispatch_event("input")
    page.locator("#btn-compute").click()
    _wait_computed(page)
    warnings = page.locator(".range-warn")
    assert warnings.count() > 0

