"""
test_unsuitable.py – testy filtrování nevhodných letadel.

Podmínka vhodnosti: useful_load >= trip_load = FOB[kg] + payload[kg]

Ověřuje:
- při výchozím obsazení jsou nevhodné řádky skryty
- tlačítko „Zobrazit nevhodná" je přítomno
- po kliknutí se nevhodné řádky zobrazí
- po druhém kliknutí se opět skryjí
- přetížení letadla způsobí jeho nevhodnost (vysoká hmotnost osádky → trip_load > useful_load)
"""


def test_unsuitable_rows_hidden_by_default(page):
    """Nevhodné řádky jsou ve výchozím stavu skryté."""
    unsuitable = page.locator("#table-body tr.unsuitable")
    # Mohou být přítomny v DOM, ale nesmí být viditelné
    for i in range(min(unsuitable.count(), 5)):
        assert not unsuitable.nth(i).is_visible()


def test_toggle_button_shows_unsuitable(page):
    """Po kliknutí na toggle se nevhodné řádky zobrazí."""
    page.locator("#toggle-unsuitable").click()
    page.wait_for_timeout(300)
    unsuitable = page.locator("#table-body tr.unsuitable")
    if unsuitable.count() > 0:
        assert unsuitable.first.is_visible()


def test_toggle_button_hides_unsuitable_again(page):
    """Druhé kliknutí nevhodné opět skryje."""
    page.locator("#toggle-unsuitable").click()   # zobrazit
    page.wait_for_timeout(200)
    page.locator("#toggle-unsuitable").click()   # skrýt
    page.wait_for_timeout(200)
    unsuitable = page.locator("#table-body tr.unsuitable")
    for i in range(min(unsuitable.count(), 3)):
        assert not unsuitable.nth(i).is_visible()


def test_overloaded_crew_marks_planes_unsuitable(page):
    """Extrémní hmotnost osádky označí letadla jako nevhodná."""
    # Nastavíme 6 cestujících po 200 kg – většina letadel bude přetížena
    page.locator(".tab-btn", has_text="Obsazení").click()
    for i in range(1, 7):
        page.locator(f"#pax{i}_weight").fill("200")
        page.locator(f"#pax{i}_weight").dispatch_event("input")
        page.locator(f"#pax{i}_baggage").fill("30")
        page.locator(f"#pax{i}_baggage").dispatch_event("input")

    page.locator("#btn-compute").click()
    # Čekáme na dokončení výpočtu (status bar se změní)
    page.wait_for_function(
        "() => document.getElementById('status-bar').textContent.length > 30",
        timeout=8_000,
    )
    page.wait_for_timeout(300)

    unsuitable = page.locator("#table-body tr.unsuitable")
    assert unsuitable.count() > 0


def test_normal_crew_has_suitable_planes(page):
    """Standardní obsazení (pilot + 1 PAX) dává alespoň 1 vhodné letadlo."""
    suitable = page.locator("#table-body tr:not(.unsuitable):not(:has(td[colspan]))")
    assert suitable.count() >= 1


def test_suitable_type_col_green(page):
    """Sloupec Typ vhodného letadla má zelenou barvu textu."""
    color = page.evaluate("""() => {
        const row = document.querySelector('#table-body tr:not(.unsuitable)');
        if (!row) return null;
        return row.querySelector('td:first-child').style.color;
    }""")
    assert color is not None and color != '', "Vhodné letadlo: sloupec Typ nemá nastavenou barvu"
    # rgb(111, 217, 111) = #6fd96f
    assert '111' in color or '6f' in color.lower() or 'green' in color.lower(), \
        f"Vhodné letadlo: barva Typ by měla být zelená, dostáno: {color}"


def test_unsuitable_type_col_red(page):
    """Sloupec Typ nevhodného letadla má červenou barvu textu."""
    # Přinutíme přetížení
    page.locator(".tab-btn", has_text="Obsazení").click()
    for i in range(1, 7):
        page.locator(f"#pax{i}_weight").fill("200")
        page.locator(f"#pax{i}_weight").dispatch_event("input")
    page.locator("#btn-compute").click()
    page.wait_for_function(
        "() => document.getElementById('status-bar').textContent.length > 30",
        timeout=8_000,
    )
    page.wait_for_timeout(300)
    page.locator("#toggle-unsuitable").click()
    page.wait_for_timeout(300)

    color = page.evaluate("""() => {
        const row = document.querySelector('#table-body tr.unsuitable');
        if (!row) return null;
        return row.querySelector('td:first-child').style.color;
    }""")
    assert color is not None and color != '', "Nevhodné letadlo: sloupec Typ nemá nastavenou barvu"
    # rgb(208, 96, 96) = #d06060
    assert '208' in color or 'd0' in color.lower() or 'red' in color.lower(), \
        f"Nevhodné letadlo: barva Typ by měla být červená, dostáno: {color}"

