"""
test_sorting.py – testy řazení tabulky kliknutím na záhlaví sloupce.

Ověřuje:
- kliknutí na záhlaví změní sort-arrow na ▲
- druhé kliknutí změní na ▼ (obrácené pořadí)
- po seřazení podle „Sed." jsou hodnoty monotónní
"""
import re


def _col_idx_by_data(page, data_col: str) -> int:
    """Vrátí index (0-based) sloupce podle atributu data-col."""
    headers = page.locator("#col-headers th[data-col]")
    for i in range(headers.count()):
        if headers.nth(i).get_attribute("data-col") == data_col:
            return i
    raise ValueError(f"Sloupec {data_col!r} nenalezen")


def _get_column_values(page, col_idx: int) -> list:
    """Vrátí textové hodnoty sloupce col_idx (0-based) ze všech viditelných řádků."""
    rows = page.locator("#table-body tr:not(.unsuitable):not(:has(td[colspan]))")
    vals = []
    for i in range(rows.count()):
        cell = rows.nth(i).locator("td").nth(col_idx)
        vals.append(cell.inner_text().strip())
    return vals


def test_click_column_sets_ascending_arrow(page):
    """Kliknutí na záhlaví zobrazí ▲."""
    th = page.locator("#col-headers th[data-col='no_seats']")
    th.click()
    page.wait_for_timeout(200)
    assert "▲" in th.inner_text()


def test_double_click_column_sets_descending_arrow(page):
    """Druhé kliknutí zobrazí ▼."""
    th = page.locator("#col-headers th[data-col='no_seats']")
    th.click()
    page.wait_for_timeout(150)
    th.click()
    page.wait_for_timeout(150)
    assert "▼" in th.inner_text()


def test_sort_by_seats_ascending(page):
    """Seřazení podle počtu sedadel ▲ – hodnoty jsou neklesající."""
    th = page.locator("#col-headers th[data-col='no_seats']")
    th.click()
    page.wait_for_timeout(300)

    # Zjistíme index sloupce No. Seats v DOM (col-headers má i th bez data-col)
    all_ths = page.locator("#col-headers th")
    seat_idx = None
    for i in range(all_ths.count()):
        if all_ths.nth(i).get_attribute("data-col") == "no_seats":
            seat_idx = i
            break
    assert seat_idx is not None

    vals = _get_column_values(page, seat_idx)
    numeric = [int(v) for v in vals if v.isdigit()]
    assert numeric == sorted(numeric), f"Sedadla nejsou seřazena vzestupně: {numeric}"


def test_sort_by_manufacturer_ascending(page):
    """Seřazení podle výrobce ▲ – první řada abecedně."""
    th = page.locator("#col-headers th[data-col='manufacturer']")
    th.click()
    page.wait_for_timeout(300)

    all_ths = page.locator("#col-headers th")
    mfr_idx = None
    for i in range(all_ths.count()):
        if all_ths.nth(i).get_attribute("data-col") == "manufacturer":
            mfr_idx = i
            break

    vals = _get_column_values(page, mfr_idx)
    assert vals == sorted(vals, key=str.lower), f"Výrobci nejsou seřazeni: {vals}"


def test_sort_by_ec_total_restores_best_row(page):
    """Po seřazení zpět podle ec_total je best-row stále přítomna."""
    # Přepneme na Economy view, jinak je sloupec ec_total skrytý
    page.evaluate("() => { document.getElementById('vm-ec').click(); }")
    page.wait_for_timeout(200)
    # Nejprve seřadíme jinak
    page.locator("#col-headers th[data-col='no_seats']").click()
    page.wait_for_timeout(200)
    # Pak zpět na ec_total (teď je viditelný)
    page.locator("#col-headers th[data-col='ec_total']").click()
    page.wait_for_timeout(300)
    assert page.locator("#table-body tr.best-row").count() == 1

