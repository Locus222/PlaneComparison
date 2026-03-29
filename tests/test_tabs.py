"""
test_tabs.py – testy přepínání záložek.

Ověřuje, že:
- výchozí aktivní záložka je „Obecné"
- kliknutí na záložku ji aktivuje a zobrazí odpovídající obsah
- pole na neaktivní kartě jsou skrytá
"""


def test_default_active_tab_is_general(page):
    active = page.locator(".tab-btn.active")
    assert "Obecné" in active.inner_text()
    assert page.locator("#tab-general").is_visible()


def test_click_plan_tab(page):
    page.locator(".tab-btn", has_text="Plán").click()
    assert page.locator("#tab-plan").is_visible()
    assert not page.locator("#tab-general").is_visible()
    # Pole vzdálenosti musí být viditelné
    assert page.locator("#distance_nm").is_visible()
    assert page.locator("#wind_kt").is_visible()


def test_click_crew_tab(page):
    page.locator(".tab-btn", has_text="Obsazení").click()
    assert page.locator("#tab-crew").is_visible()
    assert not page.locator("#tab-plan").is_visible()
    # Pilot pole musí být viditelná
    assert page.locator("#pax1_weight").is_visible()


def test_switch_back_to_general(page):
    page.locator(".tab-btn", has_text="Plán").click()
    page.locator(".tab-btn", has_text="Obecné").click()
    assert page.locator("#tab-general").is_visible()
    assert not page.locator("#tab-plan").is_visible()


def test_general_tab_fields_present(page):
    for field_id in ["avgas_price", "jet_a1_price", "avgas_density",
                     "jet_a1_density", "fuel_reserve_min",
                     "person_weight_kg", "baggage_per_seat_kg"]:
        assert page.locator(f"#{field_id}").count() == 1, f"Chybí pole #{field_id}"


def test_plan_tab_fields_present(page):
    page.locator(".tab-btn", has_text="Plán").click()
    for field_id in ["distance_nm", "distance_km", "wind_kt", "alternate_nm"]:
        assert page.locator(f"#{field_id}").is_visible(), f"Chybí pole #{field_id}"


def test_crew_tab_fields_present(page):
    page.locator(".tab-btn", has_text="Obsazení").click()
    for i in range(1, 7):
        assert page.locator(f"#pax{i}_weight").is_visible()
        assert page.locator(f"#pax{i}_baggage").is_visible()
    assert page.locator("#total_pax_kg").is_visible()
    assert page.locator("#occupied_seats").is_visible()

