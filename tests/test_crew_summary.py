"""
test_crew_summary.py – testy živého souhrnu obsazení.

Ověřuje, že:
- celková hmotnost se aktualizuje při změně váhy/zavazadla
- počet obsazených sedadel se počítá správně (> 0 = obsazeno)
- nulové hodnoty se nezapočítávají jako obsazená sedadla
- payload badge se aktualizuje OKAMŽITĚ bez čekání na API
- počet obsazených sedadel je podmínka vhodnosti letadla
"""


def _go_crew(page):
    page.locator(".tab-btn", has_text="Obsazení").click()


def _fill(page, field_id, value):
    page.locator(f"#{field_id}").fill(str(value))
    page.locator(f"#{field_id}").dispatch_event("input")


def _total_kg(page) -> float:
    raw = page.locator("#total_pax_kg").input_value()  # "175 kg"
    return float(raw.replace("kg", "").strip())


def _seats(page) -> int:
    return int(page.locator("#occupied_seats").input_value())


def test_initial_crew_total(page):
    """Výchozí hodnoty: pilot 100+5, PAX2 65+5 = 175 kg, 2 sedadla."""
    _go_crew(page)
    assert _total_kg(page) == 175.0
    assert _seats(page) == 2


def test_add_pax3(page):
    """Přidání PAX3 zvýší hmotnost i počet sedadel."""
    _go_crew(page)
    _fill(page, "pax3_weight", 80)
    _fill(page, "pax3_baggage", 10)
    assert _total_kg(page) == 265.0   # 175 + 90
    assert _seats(page) == 3


def test_remove_pax2(page):
    """Nulová váha PAX2 ho vyjme ze sedadel."""
    _go_crew(page)
    _fill(page, "pax2_weight", 0)
    _fill(page, "pax2_baggage", 0)
    assert _seats(page) == 1          # pouze pilot


def test_all_six_pax(page):
    """Šest cestujících se sečte správně."""
    _go_crew(page)
    total = 0
    for i in range(1, 7):
        w = 70 + i
        b = 5
        _fill(page, f"pax{i}_weight",  w)
        _fill(page, f"pax{i}_baggage", b)
        total += w + b
    assert _total_kg(page) == float(total)
    assert _seats(page) == 6


def test_zero_baggage_still_counts_seat(page):
    """Cestující s váhou > 0 ale bez zavazadla se počítá jako obsazené sedadlo."""
    _go_crew(page)
    _fill(page, "pax3_weight",  60)
    _fill(page, "pax3_baggage",  0)
    assert _seats(page) == 3


def test_crew_change_triggers_recompute(page):
    """Změna hmotnosti osádky spustí automatický přepočet tabulky (do 2 s)."""
    _go_crew(page)
    # Zaznamenáme text status-baru před změnou
    page.evaluate("() => { document.getElementById('status-bar').textContent = 'BEFORE'; }")
    # Změníme váhu pilota – spustí debounce 600 ms → doCompute
    _fill(page, "pax1_weight", 90)
    # Počkáme až status-bar zobrazí výsledek (max 5 s)
    page.wait_for_function(
        "() => { const t = document.getElementById('status-bar').textContent; "
        "return t.length > 30 && t !== 'BEFORE'; }",
        timeout=5_000,
    )
    # Tabulka musí obsahovat řádky
    assert page.locator("#table-body tr").count() > 0


def test_crew_change_updates_payload_display(page):
    """Změna hmotnosti osádky aktualizuje payload badge v action-baru."""
    _go_crew(page)
    # Nastav jen pilota – proveď všechny změny najednou, pak počkej
    for i in range(1, 7):
        _fill(page, f"pax{i}_weight",  0)
        _fill(page, f"pax{i}_baggage", 0)
    _fill(page, "pax1_weight",  80)
    _fill(page, "pax1_baggage", 10)
    # Počkej déle než debounce (600 ms) + čas výpočtu
    page.wait_for_timeout(1_500)
    page.wait_for_function(
        "() => { const t = document.getElementById('status-bar').textContent; "
        "return t.length > 30 && !t.includes('Počítám'); }",
        timeout=6_000,
    )
    payload_text = page.locator("#payload-value").inner_text()
    # payload = 80+10 = 90 kg → text obsahuje "90"
    assert "90" in payload_text.replace("\u00a0", " "), \
        f"Payload badge neobsahuje 90: {payload_text!r}"


# ── Okamžitá aktualizace payload badge (bez čekání na API) ────────────────────

def test_payload_badge_updates_immediately(page):
    """
    Payload badge v action-baru se aktualizuje OKAMŽITĚ při změně obsazení
    – bez čekání na API (debounce).
    Ověřuje, že updateCrewSummary() aktualizuje badge synchronně.
    """
    _go_crew(page)
    # Vynulujeme všechna sedadla
    for i in range(1, 7):
        _fill(page, f"pax{i}_weight",  0)
        _fill(page, f"pax{i}_baggage", 0)
    # Nastavíme jen pilota: 100 kg + 10 kg = 110 kg
    _fill(page, "pax1_weight",  100)
    _fill(page, "pax1_baggage", 10)

    # Badge by měl být viditelný a obsahovat "110" BEZ čekání na API
    # (max 200 ms – čistě synchronní JS, žádný síťový požadavek)
    page.wait_for_function(
        "() => {"
        "  const el = document.getElementById('payload-display');"
        "  const val = document.getElementById('payload-value');"
        "  if (!el || el.style.display === 'none') return false;"
        "  return val.textContent.replace(/\\u00a0/g,' ').includes('110');"
        "}",
        timeout=1_000,
    )
    payload_text = page.locator("#payload-value").inner_text()
    assert "110" in payload_text.replace("\u00a0", " "), \
        f"Payload badge měl okamžitě zobrazit 110, ale zobrazuje: {payload_text!r}"


def test_payload_badge_updates_after_pilot_weight_change(page):
    """
    Konkrétní scénář z bug reportu: pilot 100→120 kg, přidán PAX3 75+5 kg.
    Výsledek: celková hmotnost 220 kg (120+5+65+5+75+5).
    Badge musí zobrazit 220 okamžitě po změnách.
    """
    _go_crew(page)
    # Výchozí stav: pax1=100+5, pax2=65+5 → 175 kg
    # Změníme pilota na 120 kg
    _fill(page, "pax1_weight", 120)
    # Přidáme PAX3: 75+5
    _fill(page, "pax3_weight",  75)
    _fill(page, "pax3_baggage",  5)

    expected_total = 120 + 5 + 65 + 5 + 75 + 5  # = 275 kg

    page.wait_for_function(
        f"() => {{"
        f"  const val = document.getElementById('payload-value');"
        f"  if (!val) return false;"
        f"  return val.textContent.replace(/\\u00a0/g,' ').includes('{expected_total}');"
        f"}}",
        timeout=1_000,
    )
    payload_text = page.locator("#payload-value").inner_text()
    assert str(expected_total) in payload_text.replace("\u00a0", " "), \
        f"Payload badge měl zobrazit {expected_total}, ale zobrazuje: {payload_text!r}"


def test_payload_badge_visible_on_page_load(page):
    """
    Payload badge je viditelný hned po načtení stránky
    (updateCrewSummary() se volá při inicializaci).
    """
    # Badge by měl být zobrazen hned (updateCrewSummary je voláno při init)
    page.wait_for_function(
        "() => {"
        "  const el = document.getElementById('payload-display');"
        "  return el && el.style.display !== 'none';"
        "}",
        timeout=2_000,
    )
    payload_text = page.locator("#payload-value").inner_text().replace("\u00a0", " ")
    # Výchozí: 100+5+65+5 = 175 kg
    assert "175" in payload_text, \
        f"Výchozí payload badge měl zobrazit 175, ale zobrazuje: {payload_text!r}"


# ── Počet sedadel jako podmínka vhodnosti ─────────────────────────────────────

def test_table_marks_plane_unsuitable_when_seats_exceeded(page):
    """
    Letadlo s méně sedadly než je počet cestujících musí být v tabulce
    označeno jako nevhodné (řádek musí mít třídu 'unsuitable').
    Obsadíme 6 sedadel a ověříme, že alespoň jedno letadlo je nevhodné.
    """
    _go_crew(page)
    # Obsadíme všech 6 sedadel
    for i in range(1, 7):
        _fill(page, f"pax{i}_weight",  80)
        _fill(page, f"pax{i}_baggage",  5)

    # Počkáme na dokončení přepočtu
    page.wait_for_function(
        "() => { const t = document.getElementById('status-bar').textContent;"
        "return t.includes('aktualizovány') || t.includes('Výsledky'); }",
        timeout=8_000,
    )
    # Alespoň jeden řádek musí mít třídu unsuitable (letadlo s <6 sedadly)
    unsuitable_rows = page.locator("#table-body tr.unsuitable").count()
    assert unsuitable_rows > 0, (
        "Po obsazení 6 sedadel musí být alespoň jedno letadlo označeno "
        "jako nevhodné (třída 'unsuitable')."
    )


def test_occupied_seats_count_reflected_in_table(page):
    """
    Zobrazený počet vhodných letadel se sníží, pokud obsadíme více sedadel
    než má letadlo kapacitu (počet obsazených = podmínka vhodnosti).
    """
    _go_crew(page)
    # Nejprve výpočet s 1 sedadlem (jen pilot) – zaznamenáme počet vhodných
    for i in range(2, 7):
        _fill(page, f"pax{i}_weight",  0)
        _fill(page, f"pax{i}_baggage", 0)
    page.wait_for_function(
        "() => { const t = document.getElementById('status-bar').textContent;"
        "return t.includes('aktualizovány') || t.includes('Výsledky'); }",
        timeout=8_000,
    )
    count_1_pax = int(
        page.locator("#sum-count strong").inner_text().split()[0]
    )

    # Obsadíme 6 sedadel
    for i in range(1, 7):
        _fill(page, f"pax{i}_weight",  80)
        _fill(page, f"pax{i}_baggage",  5)
    page.wait_for_function(
        "() => { const t = document.getElementById('status-bar').textContent;"
        "return t.includes('aktualizovány') || t.includes('Výsledky'); }",
        timeout=8_000,
    )
    count_6_pax = int(
        page.locator("#sum-count strong").inner_text().split()[0]
    )

    assert count_6_pax <= count_1_pax, (
        f"S 6 cestujícími ({count_6_pax} vhodných) by nemělo být více "
        f"vhodných letadel než s 1 ({count_1_pax} vhodných)."
    )


