"""
test_nm_km_sync.py – testy obousměrné synchronizace NM ↔ km.
"""
import pytest


NM_TO_KM = 1.852


def _get_val(page, field_id: str) -> float:
    return float(page.locator(f"#{field_id}").input_value())


def test_nm_to_km_sync(page):
    """Změna NM přepočítá km."""
    page.locator(".tab-btn", has_text="Plán").click()
    page.locator("#distance_nm").fill("100")
    page.locator("#distance_nm").dispatch_event("input")
    km_val = _get_val(page, "distance_km")
    assert abs(km_val - 185) < 2   # 100 * 1.852 = 185.2


def test_km_to_nm_sync(page):
    """Změna km přepočítá NM."""
    page.locator(".tab-btn", has_text="Plán").click()
    page.locator("#distance_km").fill("370")
    page.locator("#distance_km").dispatch_event("input")
    nm_val = _get_val(page, "distance_nm")
    assert abs(nm_val - 200) < 2   # 370 / 1.852 ≈ 199.8


def test_zero_distance(page):
    """Nulová vzdálenost se synchronizuje."""
    page.locator(".tab-btn", has_text="Plán").click()
    page.locator("#distance_nm").fill("0")
    page.locator("#distance_nm").dispatch_event("input")
    assert _get_val(page, "distance_km") == 0.0


@pytest.mark.parametrize("nm,expected_km", [
    (50,  93),
    (200, 370),
    (500, 926),
])
def test_nm_to_km_parametric(page, nm, expected_km):
    page.locator(".tab-btn", has_text="Plán").click()
    page.locator("#distance_nm").fill(str(nm))
    page.locator("#distance_nm").dispatch_event("input")
    km_val = _get_val(page, "distance_km")
    assert abs(km_val - expected_km) < 2

